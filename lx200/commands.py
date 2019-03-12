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


class SimpleNumericCommand(SimpleCommand):
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
    pattern = 'AL'


@register
class PolarAlignment(SimpleCommand):
    pattern = 'AP'


@register
class AltAzAlignment(SimpleCommand):
    pattern = 'AA'


# Anti Backlash

@register
class SetAltitudeAntiBacklash(SimpleNumericCommand):
    pattern = re.compile(r'^\$BA ?(\d{1,2})$')


@register
class SetDeclinationAntiBacklash(SetAltitudeAntiBacklash):
    pass


@register
class SetAzimuthAntiBacklash(SimpleNumericCommand):
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
    pattern = re.compile(r'^\$B ?(\d)$')


@register
class SetReticleFlashDutyCycle(SimpleNumericCommand):
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
    pattern = 'D'


# XXX TODO: Fan / Heater commands
# XXX TODO: Focuser Control
# XXX TODO: GPS / Magnetometer


# Get Telescope Information

@register
class GetAlignmentMenuEntry0(SimpleCommand):
    pattern = 'G0'


@register
class GetAlignmentMenuEntry1(SimpleCommand):
    pattern = 'G1'


@register
class GetAlignmentMenuEntry2(SimpleCommand):
    pattern = 'G2'


@register
class GetLocalTime12H(SimpleCommand):
    pattern = 'Ga'


@register
class GetAltitude(SimpleCommand):
    pattern = 'GA'


@register
class GetBrowseBrighterMagnitudeLimit(SimpleCommand):
    pattern = 'Gb'


@register
class GetDate(SimpleCommand):
    pattern = 'GC'


@register
class GetClockFormat(SimpleCommand):
    pattern = 'Gc'


@register
class GetDeclination(SimpleCommand):
    pattern = 'GD'


@register
class GetSelectedObjectDeclination(SimpleCommand):
    pattern = 'Gd'


@register
class GetSelectedTargetDeclination(GetSelectedObjectDeclination):
    pass


@register
class GetSelenographicLatitude(SimpleCommand):
    pattern = 'GE'


@register
class GetSelenographicLongitude(SimpleCommand):
    pattern = 'Ge'


@register
class GetFindFieldDiameter(SimpleCommand):
    pattern = 'GF'


@register
class GetBrowseFaintMagnitudeLimit(SimpleCommand):
    pattern = 'Gf'


@register
class GetUTCOffsetTime(SimpleCommand):
    pattern = 'GG'


@register
class GetSiteLongitude(SimpleCommand):
    pattern = 'Gg'


@register
class GetDailySavingsTimeSettings(SimpleCommand):
    pattern = 'GH'


@register
class GetHighLimit(SimpleCommand):
    pattern = 'Gh'


@register
class GetLocalTime24H(SimpleCommand):
    pattern = 'GL'


@register
class GetDistanceToMeridian(SimpleCommand):
    pattern = 'Gm'


@register
class GetLargerSizeLimit(SimpleCommand):
    pattern = 'Gl'


@register
class GetSite1Name(SimpleCommand):
    pattern = 'GM'


@register
class GetSite2Name(SimpleCommand):
    pattern = 'GN'


@register
class GetSite3Name(SimpleCommand):
    pattern = 'GO'


@register
class GetSite4Name(SimpleCommand):
    pattern = 'GP'


@register
class GetBacklashValues(SimpleCommand):
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
    pattern = 'GR'


@register
class GetSelectedObjectRightAscencion(SimpleCommand):
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
    pattern = 'GT'


@register
class GetSiteLatitude(SimpleCommand):
    pattern = 'Gt'


@register
class GetFirmwareDate(SimpleCommand):
    pattern = 'GVD'


@register
class GetFirmwareNumber(SimpleCommand):
    pattern = 'GVN'


@register
class GetProductName(SimpleCommand):
    pattern = 'GVP'


@register
class GetFirmwareTime(SimpleCommand):
    pattern = 'GVT'


@register
class GetAlignmentStatus(SimpleCommand):
    pattern = 'GW'


@register
class GetDeepskySearchString(SimpleCommand):
    pattern = 'Gy'


@register
class GetAzimuth(SimpleCommand):
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
    pattern = 'P'


# XXX FIXME: This also appears documented as 'User Format Control'
@register
class PrecisionPositionToggle(SimpleCommand):
    pattern = 'U'


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
    pattern = 'RC'


@register
class SetSlewRateToGuiding(SimpleCommand):
    pattern = 'RG'


@register
class SetSlewRateToFinding(SimpleCommand):
    pattern = 'RM'


@register
class SetSlewRateToMax(SimpleCommand):
    pattern = 'RS'


@register
class SetRightAscentionSlewRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^RA ?(?P<value>\d\d\.\d)$')


@register
class SetAzimuthSlewRate(SetRightAscentionSlewRate):
    pass


@register
class SetDeclinationSlewRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Re ?(?P<value>\d\d\.\d)$')


@register
class SetAltitudeSlewRate(SetDeclinationSlewRate):
    pass


@register
class SetGuideRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Rg ?(?P<value>\d\d\.\d)$')


# Set Commands

@register
@attr.s
class SetTargetAltitude(SignedDMSCommand):
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^Sa ?(?P<degrees>[-+ ]?\d{2})\*(?P<minutes>\d{2})\'?(?P<seconds>\d{2})?$')


@register
class SetBrighterLimit(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Sb ?(?P<value>[-+ ]?\d\d\.\d)$')


@register
class SetBaudRate(SimpleNumericCommand):
    pattern = re.compile(r'^SB ?(?P<value>\d)$')


@register
class SetHandboxDate(SimpleNumericCommand):
    value = attr.ib(default=None, repr=False)
    month = attr.ib(default=None)
    day = attr.ib(default=None)
    year = attr.ib(default=None)
    pattern = re.compile(r'^SC ?(?P<month>\d\d)/(?P<day>\d\d)/(?P<year>\d\d)$')


@register
@attr.s
class SetTargetDeclination(SignedDMSCommand):
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^Sd ?(?P<degrees>[-+ ]?\d{2}):(?P<minutes>\d{2}):?(?P<seconds>\d{2})?$')


@register
@attr.s
class SetTargetSelenographicLatitude(SignedDMSCommand):
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^SE ?(?P<degrees>[-+ ]?\d{2}):(?P<minutes>\d{2}):?(?P<seconds>\d{2})?$')


@register
@attr.s
class SetTargetSelenographicLongitude(SignedDMSCommand):
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
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
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    pattern = re.compile(r'^Sg ?(?P<degrees>\d{3})[\*:](?P<minutes>\d\d)$')


@register
class SetUTCOffset(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^SG ?(?P<value>[-+ ]?\d\d\.?\d?)$')


@register
class SetDSTEnabled(SimpleNumericCommand):
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
    value = attr.ib(default=None, repr=False)
    hours = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^SL ?(?P<hours>\d{2}):(?P<minutes>\d{2}):(?P<seconds>\d{2})$')


@register
class EnableFlexureCorrection(SimpleCommand):
    pattern = 'Sm+'


@register
class DisableFlexureCorrection(SimpleCommand):
    pattern = 'Sm-'


@register
class SetSite1Name(SimpleNumericCommand):
    default_type = str
    pattern = re.compile(r'^SM ?([\w\s]{1,15})')


@register
class SetSite2Name(SimpleNumericCommand):
    default_type = str
    pattern = re.compile(r'^SN ?([\w\s]{1,15})')


@register
class SetSite3Name(SimpleNumericCommand):
    default_type = str
    pattern = re.compile(r'^SO ?([\w\s]{1,15})')


@register
class SetSite4Name(SimpleNumericCommand):
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
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    type_map = {
        'minutes': float
    }
    pattern = re.compile(r'^Sr ?(?P<degrees>\d{2}):(?P<minutes>\d{2}\.?\d?):?(?P<seconds>\d{2})?$')


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
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    pattern = re.compile(r'^St ?(?P<degrees>[-+ ]?\d{2})[\*:](?P<minutes>\d\d):(?P<seconds>\d\d)$')


@register
class SetTrackingRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^ST ?(\d{2,4}\.?\d{0,6})')


@register
class EnableAltitudePEC(SimpleCommand):
    pattern = 'STA+'


@register
class DisableAltitudePEC(SimpleCommand):
    pattern = 'STA-'


@register
class EnableRightAscencionPEC(SimpleCommand):
    pattern = 'STZ+'


@register
class EnableAzimuthPEC(EnableRightAscencionPEC):
    pass


@register
class DisableRightAscencionPEC(SimpleCommand):
    pattern = 'STZ-'


@register
class DisableAzimuthPEC(DisableRightAscencionPEC):
    pass


@register
class SetSlewRate(SimpleNumericCommand):
    pattern = re.compile(r'^Sw ?(\d)$')


# XXX FIXME: there seems to be a parameter missing in the manual
@register
class SetObjectSelectionString(SimpleCommand):
    pattern = 'SyGPDCO'


@register
@attr.s
class SetTargetAzimuth(SimpleNumericCommand):
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=None)
    minutes = attr.ib(default=None)
    pattern = re.compile(r'^Sz ?(?P<degrees>\d{3})\*(?P<minutes>\d{2})$')


# Tracking

# These two are also defined in the 'Set' group but do the same thing, so we lump them in a single command.
@register
class IncrementManualRate(SimpleCommand):
    pattern = re.compile('(^ST\+$)|(^T\+$)')


@register
class DecrementManualRate(SimpleCommand):
    pattern = re.compile('(^ST\-$)|(^T\-$)')


@register
class SetLunarTracking(SimpleCommand):
    pattern = 'TL'


@register
class SelectCustomTrackingRate(SimpleCommand):
    pattern = 'TM'


@register
class SelectSiderealTrackingRate(SimpleCommand):
    pattern = 'TQ'


@register
class SelectSolarTrackingRate(SimpleCommand):
    pattern = 'TS'


# XXX TODO: PEC
