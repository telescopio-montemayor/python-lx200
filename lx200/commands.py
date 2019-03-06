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


class SimpleCommand(BaseCommand):
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
    pattern = re.compile(r'^\$BA(\d{1,2})$')


@register
class SetDeclinationAntiBacklash(SetAltitudeAntiBacklash):
    pass


@register
class SetAzimuthAntiBacklash(SimpleNumericCommand):
    pattern = re.compile(r'^\$BZ(\d{1,2})$')


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
class SetReticleFlashRate(SimpleCommand):
    pattern = re.compile(r'^\$B(\d)$')


@register
class SetReticleFlashDutyCycle(SimpleCommand):
    pattern = re.compile(r'^\$BD(\d{1,2})$')


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
    # YYMMDDHHMMSS
    year = attr.ib(default=None)
    month = attr.ib(default=None)
    day = attr.ib(default=None)
    hours = attr.ib(default=None)
    minutes = attr.ib(default=None)
    seconds = attr.ib(default=None)
    pattern = re.compile(r'^hI(?P<year>\d{2})(?P<month>\d{2})(?P<day>\d{2})(?P<hours>\d{2})(?P<minutes>\d{2})(?P<seconds>\d{2})$')


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
    pattern = re.compile(r'^Mgn(\d{4})$')


@register
class GuideSouth(SimpleNumericCommand):
    pattern = re.compile(r'^Mgs(\d{4})$')


@register
class GuideEast(SimpleNumericCommand):
    pattern = re.compile(r'^Mge(\d{4})$')


@register
class GuideWest(SimpleNumericCommand):
    pattern = re.compile(r'^Mgw(\d{4})$')


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
    pattern = re.compile(r'^RA(?P<value>\d\d\.\d)$')


@register
class SetAzimuthSlewRate(SetRightAscentionSlewRate):
    pass


@register
class SetDeclinationSlewRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Re(?P<value>\d\d\.\d)$')


@register
class SetAltitudeSlewRate(SetDeclinationSlewRate):
    pass


@register
class SetGuideRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Rg(?P<value>\d\d\.\d)$')


# XXX TODO: Telescope Set Commands

# Tracking

@register
class IncrementManualRate(SimpleCommand):
    pattern = 'T+'


@register
class DecrementManualRate(SimpleCommand):
    pattern = 'T-'


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
