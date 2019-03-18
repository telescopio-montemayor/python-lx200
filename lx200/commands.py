#!/usr/bin/env python3

import re
import attr


ALL_COMMANDS = []


def register(command):
    ALL_COMMANDS.append(command)
    return command


def is_command(data, command):
    return command.can_be(data) not in (None, False)


@attr.s
class BaseCommand:
    value = attr.ib(default=None)

    @classmethod
    def from_data(cls, data):
        """ Tries to parse the given data block as this command.
        If successful returns a new instance of this command properly
        initialized"""
        raise NotImplementedError

    @classmethod
    def can_be(cls, data):
        """ Returns True if data can be parsed as this command"""
        raise NotImplementedError

    def serialize(self):
        """ Returns a dict with current data suitable to build a response """
        try:
            return self.store_value
        except:
            pass

        to_include = [field for field in attr.fields(self.__class__) if field.repr]
        return attr.asdict(self, filter=attr.filters.include(*to_include))


class UnknownCommand(BaseCommand):
    @classmethod
    def from_data(cls, data=None):
        instance = cls(value=data)
        return instance

    # XXX FIXME: later test that this is really unknown?
    @classmethod
    def can_be(cls, data=None):
        return True


@attr.s
class SimpleCommand(BaseCommand):
    value = attr.ib(default=None, repr=False)
    pattern = None

    @classmethod
    def from_data(cls, data):
        matches = cls.can_be(data)
        if not matches:
            raise ValueError('Provided block of data "{}" is not valid for {}'.format(data, cls.__qualname__))
        else:
            instance = cls()
            return instance.parse(matches, data)

    def parse(self, matches, data=None):
        return self

    @classmethod
    def can_be(cls, data):
        if cls.pattern is None:
            raise NotImplementedError('Command pattern is not defined')

        try:
            return cls.pattern.fullmatch(data)
        except AttributeError:
            return (data == cls.pattern) or (data == bytes(cls.pattern, 'utf-8'))


@attr.s
class SimpleNumericCommand(SimpleCommand):
    value = attr.ib(default=0, repr=True)
    default_type = int
    type_map = {}

    def parse(self, matches, data):
        named_groups = matches.groupdict()

        if not named_groups:
            self.value = self.default_type(matches.group(1))
            return self

        for (name, value) in named_groups.items():
            converter = self.type_map.get(name, self.default_type)
            # If a group is optional its value will be None
            # built-in types (like int, float) do not handle None as a valid argument
            # however, this way we can get a sane default
            if value is not None:
                setattr(self, name, converter(value))
            else:
                setattr(self, name, converter())

        return self


@attr.s
class SignedDMSCommand(SimpleNumericCommand):
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=0)
    minutes = attr.ib(default=0)
    seconds = attr.ib(default=0)

    def parse(self, matches, data):
        super().parse(matches, data)
        if self.degrees < 0:
            self.minutes = -1 * self.minutes
            try:
                self.seconds = -1 * self.seconds
            except:
                # We may not have seconds in some subclasses
                pass

        return self


# These two are here for completeness only, as they do not use the start and
# end delimiters shared by the rest of the command set.
@register
class ACK(SimpleCommand):
    """ Alignment Query """
    load_path = 'mount.alignment_mode'
    pattern = '\x06'


@register
class EOT(SimpleCommand):
    """ Firmware Download Request """
    pattern = '\x04'


# Alignment related commands

@register
class AutomaticAlignment(SimpleCommand):
    """ Start Telescope Automatic Alignment Sequence [Autostar II/RCX400 only] """
    pattern = 'Aa'


@register
class LandAlignment(SimpleCommand):
    store_path = 'mount.alignment_mode'
    store_value = {'value': 'L'}
    pattern = 'AL'


@register
class PolarAlignment(SimpleCommand):
    store_path = 'mount.alignment_mode'
    store_value = {'value': 'P'}
    pattern = 'AP'


@register
class AltAzAlignment(SimpleCommand):
    store_path = 'mount.alignment_mode'
    store_value = {'value': 'A'}
    pattern = 'AA'


# Anti Backlash

@register
class SetAltitudeAntiBacklash(SimpleNumericCommand):
    store_path = 'mount.backlash.altitude'
    pattern = re.compile(r'^\$BA ?(\d{1,2})$')


@register
class SetDeclinationAntiBacklash(SetAltitudeAntiBacklash):
    pass


@register
class SetAzimuthAntiBacklash(SimpleNumericCommand):
    store_path = 'mount.backlash.azimuth'
    pattern = re.compile(r'^\$BZ ?(\d{1,2})$')


@register
class SetRightAscentionAntiBacklash(SetAzimuthAntiBacklash):
    pass


# Reticule / Accessories

@register
class IncreaseReticleBrightness(SimpleCommand):
    pattern = 'B+'


@register
class DecreaseReticleBrightness(SimpleCommand):
    pattern = 'B-'


@register
class SetReticleFlashRate(SimpleNumericCommand):
    store_path = 'reticle.flash.rate'
    pattern = re.compile(r'^\$B ?(\d)$')


@register
class SetReticleFlashDutyCycle(SimpleNumericCommand):
    store_path = 'reticle.flash.duty_cycle'
    pattern = re.compile(r'^\$BD ?(\d{1,2})$')


# Sync Control

@register
class SyncSelenographic(SimpleCommand):
    pattern = 'CL'


@register
class SyncDatabase(SimpleCommand):
    pattern = 'CM'


# Distance Bars

@register
class DistanceBars(SimpleCommand):
    load_path = 'mount.target.distance'
    pattern = 'D'


# XXX TODO: Fan / Heater commands

# Focuser Control

@register
class MoveFocuserInward(SimpleCommand):
    pattern = 'F+'


@register
class MoveFocuserOutward(SimpleCommand):
    pattern = 'F-'


@register
class PulseFocuser(SimpleNumericCommand):
    pattern = re.compile(r'^FP ?([-+ ]?\d{1,5})$')


@register
class TiltCorrectorPlate(SimpleCommand):
    default_type = str
    pattern = re.compile(r'^FC ?([nsew])$')


@register
class HaltFocuserMotion(SimpleCommand):
    pattern = 'FQ'


@register
class SetFocuserPreset(SimpleNumericCommand):
    pattern = re.compile(r'^FLD ?([123456789])$')


@register
@attr.s
class SetFocuserPresetName(SimpleNumericCommand):
    default_type = str
    store_path = 'focuser.presets.name_{idx}'
    idx = attr.ib(default=1)
    pattern = re.compile(r'^FLN ?(?P<idx>[123456789])(?P<value>[\w\s]+)$')


@register
class SyncFocuserToPreset(SimpleNumericCommand):
    pattern = re.compile(r'^FLS ?([123456789])$')


@register
class SetFocuserSpeedFastest(SimpleCommand):
    store_path = 'focuser.speed'
    store_value = {'value': 4}
    pattern = 'FF'


@register
class SetFocuserSpeedSlowest(SimpleCommand):
    store_path = 'focuser.speed'
    store_value = {'value': 1}
    pattern = 'FS'


@register
@attr.s
class SetFocuserSpeed(SimpleNumericCommand):
    value = attr.ib(default=1)
    store_path = 'focuser.speed'
    pattern = re.compile(r'^F ?([1234])$')


@register
class QueryFocuserBusyStatus(SimpleCommand):
    load_path = 'focuser.busy'
    pattern = 'FB'


# XXX TODO: GPS / Magnetometer


# Get Telescope Information

@register
class GetAlignmentMenuEntry0(SimpleCommand):
    load_path = 'mount.alignment.menu_0'
    pattern = 'G0'


@register
class GetAlignmentMenuEntry1(SimpleCommand):
    load_path = 'mount.alignment.menu_1'
    pattern = 'G1'


@register
class GetAlignmentMenuEntry2(SimpleCommand):
    load_path = 'mount.alignment.menu_2'
    pattern = 'G2'


@register
class GetLocalTime12H(SimpleCommand):
    load_path = 'site.time'
    pattern = 'Ga'


@register
class GetAltitude(SimpleCommand):
    load_path = 'mount.altitude'
    pattern = 'GA'


@register
class GetBrowseBrighterMagnitudeLimit(SimpleCommand):
    pattern = 'Gb'


@register
class GetDate(SimpleCommand):
    load_path = 'site.date'
    pattern = 'GC'


@register
class GetClockFormat(SimpleCommand):
    load_path = 'mount.clock_format_24h'
    pattern = 'Gc'


@register
class GetDeclination(SimpleCommand):
    load_path = 'mount.declination'
    pattern = 'GD'


@register
class GetSelectedObjectDeclination(SimpleCommand):
    load_path = 'mount.target.declination'
    pattern = 'Gd'


@register
class GetSelectedTargetDeclination(GetSelectedObjectDeclination):
    pass


@register
class GetSelenographicLatitude(SimpleCommand):
    load_path = 'mount.target.selenographic.latitude'
    pattern = 'GE'


@register
class GetSelenographicLongitude(SimpleCommand):
    load_path = 'mount.target.selenographic.longitude'
    pattern = 'Ge'


@register
class GetFindFieldDiameter(SimpleCommand):
    pattern = 'GF'


@register
class GetBrowseFaintMagnitudeLimit(SimpleCommand):
    pattern = 'Gf'


@register
class GetUTCOffsetTime(SimpleCommand):
    load_path = 'site.utc_offset'
    pattern = 'GG'


@register
class GetSiteLongitude(SimpleCommand):
    load_path = 'site.longitude'
    pattern = 'Gg'


@register
class GetDailySavingsTimeSettings(SimpleCommand):
    load_path = 'site.dst.enabled'
    pattern = 'GH'


@register
class GetHighLimit(SimpleCommand):
    pattern = 'Gh'


@register
class GetLocalTime24H(SimpleCommand):
    load_path = 'site.time'
    pattern = 'GL'


@register
class GetDistanceToMeridian(SimpleCommand):
    pattern = 'Gm'


@register
class GetLargerSizeLimit(SimpleCommand):
    pattern = 'Gl'


@register
class GetSite1Name(SimpleCommand):
    load_path = 'site.name_1'
    pattern = 'GM'


@register
class GetSite2Name(SimpleCommand):
    load_path = 'site.name_2'
    pattern = 'GN'


@register
class GetSite3Name(SimpleCommand):
    load_path = 'site.name_3'
    pattern = 'GO'


@register
class GetSite4Name(SimpleCommand):
    load_path = 'site.name_4'
    pattern = 'GP'


@register
class GetBacklashValues(SimpleCommand):
    load_path = 'mount.backlash.values'
    pattern = 'GpB'


@register
class GetHomeData(SimpleCommand):
    pattern = 'GpH'


@register
class GetSensorOffsets(SimpleCommand):
    pattern = 'GpS'


@register
class GetLowerLimit(SimpleCommand):
    pattern = 'Go'


@register
class GetMinimumQualityForFind(SimpleCommand):
    pattern = 'Gq'


@register
class GetRightAscencion(SimpleCommand):
    load_path = 'mount.right_ascencion'
    pattern = 'GR'


@register
class GetSelectedObjectRightAscencion(SimpleCommand):
    load_path = 'mount.target.right_ascencion'
    pattern = 'Gr'


@register
class GetSelectedTargetRightAscencion(GetSelectedObjectRightAscencion):
    pass


@register
class GetSiderealTime(SimpleCommand):
    pattern = 'GS'


@register
class GetSmallerSizeLimit(SimpleCommand):
    pattern = 'Gs'


@register
class GetTrackingRate(SimpleCommand):
    load_path = 'mount.tracking.rate'
    pattern = 'GT'


@register
class GetSiteLatitude(SimpleCommand):
    load_path = 'site.latitude'
    pattern = 'Gt'


@register
class GetFirmwareDate(SimpleCommand):
    load_path = 'firmware.date'
    pattern = 'GVD'


@register
class GetFirmwareNumber(SimpleCommand):
    load_path = 'firmware.number'
    pattern = 'GVN'


@register
class GetProductName(SimpleCommand):
    pattern = 'GVP'


@register
class GetFirmwareTime(SimpleCommand):
    load_path = 'firmware.time'
    pattern = 'GVT'


@register
class GetAlignmentStatus(SimpleCommand):
    pattern = 'GW'


@register
class GetDeepskySearchString(SimpleCommand):
    pattern = 'Gy'


@register
class GetAzimuth(SimpleCommand):
    load_path = 'mount.azimuth'
    pattern = 'GZ'


# Home Position

@register
class CalibrateHomePosition(SimpleCommand):
    pattern = 'hC'


@register
class SeekHomePosition(SimpleCommand):
    pattern = 'hF'


@register
@attr.s
class BypassDSTEntry(SimpleNumericCommand):
    value = attr.ib(default=None, repr=False)
    # YYMMDDHHMMSS
    year = attr.ib(default=None)
    month = attr.ib(default=None)
    day = attr.ib(default=None)
    hours = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^hI ?(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2})$')


@register
class Sleep(SimpleCommand):
    pattern = 'hN'


@register
class Park(SimpleCommand):
    pattern = 'hP'


@register
class SetParkPosition(SimpleCommand):
    pattern = 'hS'


@register
class WakeUp(SimpleCommand):
    pattern = 'hW'


@register
class QueryHomeStatus(SimpleCommand):
    pattern = 'h?'


# Time Format

@register
class ToggleTimeFormat(SimpleCommand):
    store_path = 'mount.clock_format_24h'
    store_value = {'value': True}
    pattern = 'H'


# Initialization

@register
class Initialize(SimpleCommand):
    pattern = 'I'


# XXX TODO: Object Library

# Movement Commands

@register
class SlewToTargetAltAz(SimpleCommand):
    pattern = 'MA'


@register
class GuideNorth(SimpleNumericCommand):
    pattern = re.compile(r'^Mgn ?(\d{4})$')


@register
class GuideSouth(SimpleNumericCommand):
    pattern = re.compile(r'^Mgs ?(\d{4})$')


@register
class GuideEast(SimpleNumericCommand):
    pattern = re.compile(r'^Mge ?(\d{4})$')


@register
class GuideWest(SimpleNumericCommand):
    pattern = re.compile(r'^Mgw ?(\d{4})$')


@register
class MoveEast(SimpleCommand):
    pattern = 'Me'


@register
class MoveNorth(SimpleCommand):
    pattern = 'Mn'


@register
class MoveSouth(SimpleCommand):
    pattern = 'Ms'


@register
class MoveWest(SimpleCommand):
    pattern = 'Mw'


@register
class SlewToTargetObject(SlewToTargetAltAz):
    pattern = 'MS'


@register
class SlewToTarget(SlewToTargetObject):
    pass


# Precision toggle

@register
class HighPrecisionToggle(SimpleCommand):
    store_path = 'high_precision_enabled'
    store_value = {'value': True}
    pattern = 'P'


# XXX FIXME: This also appears documented as 'User Format Control'
@register
class PrecisionPositionToggle(SimpleCommand):
    store_path = 'high_precision_enabled'
    store_value = {'value': True}
    pattern = 'U'


@register
class SelectSite(SimpleNumericCommand):
    store_path = 'site.selected'
    pattern = re.compile(r'^W ?(\d)$')


# XXX TODO: Smart Drive Control

# Movement Commands (halt)

@register
class HaltAll(SimpleCommand):
    pattern = 'Q'


@register
class HaltEastward(SimpleCommand):
    pattern = 'Qe'


@register
class HaltNorthwawrd(SimpleCommand):
    pattern = 'Qn'


@register
class HaltSouthward(SimpleCommand):
    pattern = 'Qs'


@register
class HaltWestward(SimpleCommand):
    pattern = 'Qw'


# XXX TODO: Field de-rotator

# Slew Rate

@register
class SetSlewRateToCentering(SimpleCommand):
    store_path = 'mount.slew.rate'
    store_value = {'value': 'centering'}
    pattern = 'RC'


@register
class SetSlewRateToGuiding(SimpleCommand):
    store_path = 'mount.slew.rate'
    store_value = {'value': 'guiding'}
    pattern = 'RG'


@register
class SetSlewRateToFinding(SimpleCommand):
    store_path = 'mount.slew.rate'
    store_value = {'value': 'finding'}
    pattern = 'RM'


@register
class SetSlewRateToMax(SimpleCommand):
    store_path = 'mount.slew.rate'
    store_value = {'value': 'max'}
    pattern = 'RS'


@register
class SetRightAscentionSlewRate(SimpleNumericCommand):
    default_type = float
    store_path = 'mount.slew.rate.right_ascencion'
    pattern = re.compile(r'^RA ?(?P<value>\d\d\.\d)$')


@register
class SetAzimuthSlewRate(SetRightAscentionSlewRate):
    pass


@register
class SetDeclinationSlewRate(SimpleNumericCommand):
    default_type = float
    store_path = 'mount.slew.rate.declination'
    pattern = re.compile(r'^Re ?(?P<value>\d\d\.\d)$')


@register
class SetAltitudeSlewRate(SetDeclinationSlewRate):
    pass


@register
class SetGuideRate(SimpleNumericCommand):
    default_type = float
    store_path = 'mount.guide.rate'
    pattern = re.compile(r'^Rg ?(?P<value>\d\d\.\d)$')


# Set Commands

@register
@attr.s
class SetTargetAltitude(SignedDMSCommand):
    store_path = 'mount.target.altitude'
    pattern = re.compile(r'^Sa ?(?P<degrees>[-+ ]?\d{2})\*(?P<minutes>\d{2})\'?(?P<seconds>\d{2})?$')


@register
class SetBrighterLimit(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Sb ?(?P<value>[-+ ]?\d\d\.\d)$')


@register
@attr.s
class SetBaudRate(SimpleNumericCommand):
    store_path = 'comms.baud_rate'
    pattern = re.compile(r'^SB ?(?P<value>\d)$')


@register
@attr.s
class SetHandboxDate(SimpleNumericCommand):
    store_path = 'site.date'
    value = attr.ib(default=None, repr=False)
    month = attr.ib(default=None)
    day = attr.ib(default=None)
    year = attr.ib(default=None)
    pattern = re.compile(r'^SC ?(?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d\d)$')


@register
@attr.s
class SetTargetDeclination(SignedDMSCommand):
    store_path = 'mount.target.declination'
    pattern = re.compile(r'^Sd ?(?P<degrees>[-+ ]?\d{2}):(?P<minutes>\d{2}):?(?P<seconds>\d{2})?$')


@register
@attr.s
class SetTargetSelenographicLatitude(SignedDMSCommand):
    store_path = 'mount.target.selenographic.latitude'
    pattern = re.compile(r'^SE ?(?P<degrees>[-+ ]?\d{2}):(?P<minutes>\d{2}):?(?P<seconds>\d{2})?$')


@register
@attr.s
class SetTargetSelenographicLongitude(SignedDMSCommand):
    store_path = 'mount.target.selenographic.longitude'
    pattern = re.compile(r'^Se ?(?P<degrees>[-+ ]?\d{2}):(?P<minutes>\d{2}):?(?P<seconds>\d{2})?$')


@register
class SetFaintMagnitude(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Sf ?(?P<value>[-+ ]?\d\d\.\d)$')


@register
class SetFieldDiameter(SimpleNumericCommand):
    pattern = re.compile(r'^SF ?(?P<value>\d{3})$')


@register
@attr.s
class SetSiteLongitude(SimpleNumericCommand):
    store_path = 'site.longitude'
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    pattern = re.compile(r'^Sg ?(?P<degrees>\d{3})[\*:](?P<minutes>\d\d)$')


@register
class SetUTCOffset(SimpleNumericCommand):
    store_path = 'site.utc_offset'
    default_type = float
    pattern = re.compile(r'^SG ?(?P<value>[-+ ]?\d\d\.?\d?)$')


@register
class SetDSTEnabled(SimpleNumericCommand):
    store_path = 'site.dst.enabled'
    pattern = re.compile(r'^SH ?(?P<value>\d)$')


@register
class SetMaximumElevation(SimpleNumericCommand):
    pattern = re.compile(r'^Sh ?(?P<value>\d\d)$')


# XXX:
# These two appear like that in the 2010 manual but seem to be transposed
# (smallest -> Sl , largest -> Ss)
@register
class SetSmallestObjectSize(SimpleNumericCommand):
    pattern = re.compile(r'^Sl ?(\d{3})$')


@register
class SetLargestObjectSize(SimpleNumericCommand):
    pattern = re.compile(r'^Ss ?(\d{3})$')


@register
@attr.s
class SetLocalTime(SimpleNumericCommand):
    store_path = 'site.time'
    value = attr.ib(default=None, repr=False)
    hours = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^SL ?(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})$')


@register
class EnableFlexureCorrection(SimpleCommand):
    store_path = 'mount.correction.flexure.enabled'
    store_value = {'value': True}
    pattern = 'Sm+'


@register
class DisableFlexureCorrection(SimpleCommand):
    store_path = 'mount.correction.flexure.enabled'
    store_value = {'value': False}
    pattern = 'Sm-'


@register
class SetSite1Name(SimpleNumericCommand):
    store_path = 'site.name_1'
    default_type = str
    pattern = re.compile(r'^SM ?([\w\s]{1,15})')


@register
class SetSite2Name(SimpleNumericCommand):
    store_path = 'site.name_2'
    default_type = str
    pattern = re.compile(r'^SN ?([\w\s]{1,15})')


@register
class SetSite3Name(SimpleNumericCommand):
    store_path = 'site.name_3'
    default_type = str
    pattern = re.compile(r'^SO ?([\w\s]{1,15})')


@register
class SetSite4Name(SimpleNumericCommand):
    store_path = 'site.name_4'
    default_type = str
    pattern = re.compile(r'^SP ?([\w\s]{1,15})')


@register
class SetLowestElevation(SimpleNumericCommand):
    pattern = re.compile(r'^So ?(\d\d)\*')


@register
class SetBacklashValues(SimpleNumericCommand):
    pattern = re.compile(r'^SpB ?(\d\d)$')


@register
class SetHomeData(SimpleNumericCommand):
    pattern = re.compile(r'^SpH ?(\d\d)')


@register
class SetSensorOffsets(SimpleNumericCommand):
    pattern = re.compile(r'^SpS ?(\d\d\d)')


@register
class StepQualityLimit(SimpleCommand):
    pattern = 'Sq'


@register
@attr.s
class SetTargetRightAscencion(SimpleNumericCommand):
    store_path = 'mount.target.right_ascencion'
    value = attr.ib(default=None, repr=False)
    hours = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    type_map = {
        'minutes': float
    }
    pattern = re.compile(r'^Sr ?(?P<hours>\d{2}):(?P<minutes>\d{2}\.?\d?):?(?P<seconds>\d{2})?$')


@register
@attr.s
class SetLocalSiderealTime(SimpleNumericCommand):
    value = attr.ib(default=None, repr=False)
    hours = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^SS ?(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})$')


@register
@attr.s
class SetSiteLatitude(SignedDMSCommand):
    store_path = 'site.latitude'
    pattern = re.compile(r'^St ?(?P<degrees>[-+ ]?\d{2})[\*:](?P<minutes>\d\d):(?P<seconds>\d\d)$')


@register
class SetTrackingRate(SimpleNumericCommand):
    store_path = 'mount.tracking.rate'
    default_type = float
    pattern = re.compile(r'^ST ?(\d{2,4}\.?\d{0,6})')


@register
class EnableAltitudePEC(SimpleCommand):
    store_path = 'mount.correction.pec.altitude.enabled'
    store_value = {'value': True}
    pattern = 'STA+'


@register
class DisableAltitudePEC(SimpleCommand):
    store_path = 'mount.correction.pec.altitude.enabled'
    store_value = {'value': False}
    pattern = 'STA-'


@register
class EnableRightAscencionPEC(SimpleCommand):
    store_path = 'mount.correction.pec.right_ascencion.enabled'
    store_value = {'value': True}
    pattern = 'STZ+'


@register
class EnableAzimuthPEC(EnableRightAscencionPEC):
    pass


@register
class DisableRightAscencionPEC(SimpleCommand):
    store_path = 'mount.correction.pec.right_ascencion.enabled'
    store_value = {'value': False}
    pattern = 'STZ-'


@register
class DisableAzimuthPEC(DisableRightAscencionPEC):
    pass


@register
class SetSlewRate(SimpleNumericCommand):
    store_path = 'mount.slew.rate'
    pattern = re.compile(r'^Sw ?(\d)$')


# XXX FIXME: there seems to be a parameter missing in the manual
@register
class SetObjectSelectionString(SimpleCommand):
    pattern = 'SyGPDCO'


@register
@attr.s
class SetTargetAzimuth(SimpleNumericCommand):
    store_path = 'mount.target.azimuth'
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    pattern = re.compile(r'^Sz ?(?P<degrees>\d{3})\*(?P<minutes>\d{2})$')


# Tracking

# These two are also defined in the 'Set' group but do the same thing, so we lump them in a single command.
@register
class IncrementManualRate(SimpleCommand):
    pattern = re.compile(r'(^ST\+$)|(^T\+$)')


@register
class DecrementManualRate(SimpleCommand):
    pattern = re.compile(r'(^ST\-$)|(^T\-$)')


@register
class SetLunarTracking(SimpleCommand):
    store_path = 'mount.tracking.rate_name'
    store_value = {'value': 'LUNAR'}
    pattern = 'TL'


@register
class SelectCustomTrackingRate(SimpleCommand):
    store_path = 'mount.tracking.rate_name'
    store_value = {'value': 'CUSTOM'}
    pattern = 'TM'


@register
class SelectSiderealTrackingRate(SimpleCommand):
    store_path = 'mount.tracking.rate_name'
    store_value = {'value': 'SIDEREAL'}
    pattern = 'TQ'


@register
class SelectSolarTrackingRate(SimpleCommand):
    store_path = 'mount.tracking.rate_name'
    store_value = {'value': 'SOLAR'}
    pattern = 'TS'


# XXX TODO: PEC
