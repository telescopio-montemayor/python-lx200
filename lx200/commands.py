#!/usr/bin/env python3

import re
import attr

COMMAND_START = ':'
COMMAND_END = '#'


def is_command(data, command):
    return command.can_be(data) is not None


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
class ACK(SimpleCommand):
    """ Alignment Query """
    pattern = '\x06'


class EOT(SimpleCommand):
    """ Firmware Download Request """
    pattern = '\x04'


# Alignment related commands

class AutomaticAlignment(SimpleCommand):
    """ Start Telescope Automatic Alignment Sequence [Autostar II/RCX400 only] """
    pattern = 'Aa'


class LandAlignment(SimpleCommand):
    pattern = 'AL'


class PolarAlignment(SimpleCommand):
    pattern = 'AP'


class AltAzAlignment(SimpleCommand):
    pattern = 'AA'


# Anti Backlash

class SetAltitudeAntiBacklash(SimpleNumericCommand):
    pattern = re.compile(r'^\$BA(\d{1,2})$')


class SetDeclinationAntiBacklash(SetAltitudeAntiBacklash):
    pass


class SetAzimuthAntiBacklash(SimpleNumericCommand):
    pattern = re.compile(r'^\$BZ(\d{1,2})$')


class SetRightAscentionAntiBacklash(SetAzimuthAntiBacklash):
    pass


# Reticule / Accessories

class IncreaseReticleBrightness(SimpleCommand):
    pattern = 'B+'


class DecreaseReticleBrightness(SimpleCommand):
    pattern = 'B-'


class SetReticleFlashRate(SimpleCommand):
    pattern = re.compile(r'^\$B(\d)$')


class SetReticleFlashDutyCycle(SimpleCommand):
    pattern = re.compile(r'^\$BD(\d{1,2})$')


# Sync Control

class SyncSelenographic(SimpleCommand):
    pattern = 'CL'


class SyncDatabase(SimpleCommand):
    pattern = 'CM'


# Distance Bars

class DistanceBars(SimpleCommand):
    pattern = 'D'


# XXX TODO: Fan / Heater commands
# XXX TODO: Focuser Control
# XXX TODO: GPS / Magnetometer


# Get Telescope Information

class GetAlignmentMenuEntry0(SimpleCommand):
    pattern = 'G0'


class GetAlignmentMenuEntry1(SimpleCommand):
    pattern = 'G1'


class GetAlignmentMenuEntry2(SimpleCommand):
    pattern = 'G2'


class GetLocalTime12H(SimpleCommand):
    pattern = 'Ga'


class GetAltitude(SimpleCommand):
    pattern = 'GA'


class GetBrowseBrighterMagnitudeLimit(SimpleCommand):
    pattern = 'Gb'


class GetDate(SimpleCommand):
    pattern = 'GC'


class GetClockFormat(SimpleCommand):
    pattern = 'Gc'


class GetDeclination(SimpleCommand):
    pattern = 'GD'


class GetSelectedObjectDeclination(SimpleCommand):
    pattern = 'Gd'


class GetSelectedTargetDeclination(GetSelectedObjectDeclination):
    pass


class GetSelenographicLatitude(SimpleCommand):
    pattern = 'GE'


class GetSelenographicLongitude(SimpleCommand):
    pattern = 'Ge'


class GetFindFieldDiameter(SimpleCommand):
    pattern = 'GF'


class GetBrowseFaintMagnitudeLimit(SimpleCommand):
    pattern = 'Gf'


class GetUTCOffsetTime(SimpleCommand):
    pattern = 'GG'


class GetSiteLongitude(SimpleCommand):
    pattern = 'Gg'


class GetDailySavingsTimeSettings(SimpleCommand):
    pattern = 'GH'


class GetHighLimit(SimpleCommand):
    pattern = 'Gh'


class GetLocalTime24H(SimpleCommand):
    pattern = 'GL'


class GetDistanceToMeridian(SimpleCommand):
    pattern = 'Gm'


class GetLargerSizeLimit(SimpleCommand):
    pattern = 'Gl'


class GetSite1Name(SimpleCommand):
    pattern = 'GM'


class GetSite2Name(SimpleCommand):
    pattern = 'GN'


class GetSite3Name(SimpleCommand):
    pattern = 'GO'


class GetSite4Name(SimpleCommand):
    pattern = 'GP'


class GetBacklashValues(SimpleCommand):
    pattern = 'GpB'


class GetHomeData(SimpleCommand):
    pattern = 'GpH'


class GetSensorOffsets(SimpleCommand):
    pattern = 'GpS'


class GetLowerLimit(SimpleCommand):
    pattern = 'Go'


class GetMinimumQualityForFind(SimpleCommand):
    pattern = 'Gq'


class GetRightAscencion(SimpleCommand):
    pattern = 'GR'


class GetSelectedObjectRightAscencion(SimpleCommand):
    pattern = 'Gr'


class GetSelectedTargetRightAscencion(GetSelectedObjectRightAscencion):
    pass


class GetSiderealTime(SimpleCommand):
    pattern = 'GS'


class GetSmallerSizeLimit(SimpleCommand):
    pattern = 'Gs'


class GetTrackingRate(SimpleCommand):
    pattern = 'GT'


class GetSiteLatitude(SimpleCommand):
    pattern = 'Gt'


class GetFirmwareDate(SimpleCommand):
    pattern = 'GVD'


class GetFirmwareNumber(SimpleCommand):
    pattern = 'GVN'


class GetProductName(SimpleCommand):
    pattern = 'GVP'


class GetFirmwareTime(SimpleCommand):
    pattern = 'GVT'


class GetAlignmentStatus(SimpleCommand):
    pattern = 'GW'


class GetDeepskySearchString(SimpleCommand):
    pattern = 'Gy'


class GetAzimuth(SimpleCommand):
    pattern = 'GZ'


# Home Position

class CalibrateHomePosition(SimpleCommand):
    pattern = 'hC'


class SeekHomePosition(SimpleCommand):
    pattern = 'hF'


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


class Sleep(SimpleCommand):
    pattern = 'hN'


class Park(SimpleCommand):
    pattern = 'hP'


class SetParkPosition(SimpleCommand):
    pattern = 'hS'


class WakeUp(SimpleCommand):
    pattern = 'hW'


class QueryHomeStatus(SimpleCommand):
    pattern = 'h?'


# Time Format

class ToggleTimeFormat(SimpleCommand):
    pattern = 'H'


# Initialization

class Initialize(SimpleCommand):
    pattern = 'I'


# XXX TODO: Object Library

# Movement Commands

class SlewToTargetAltAz(SimpleCommand):
    pattern = 'MA'


class GuideNorth(SimpleNumericCommand):
    pattern = re.compile(r'^Mgn(\d{4})$')


class GuideSouth(SimpleNumericCommand):
    pattern = re.compile(r'^Mgs(\d{4})$')


class GuideEast(SimpleNumericCommand):
    pattern = re.compile(r'^Mge(\d{4})$')


class GuideWest(SimpleNumericCommand):
    pattern = re.compile(r'^Mgw(\d{4})$')


class MoveEast(SimpleCommand):
    pattern = 'Me'


class MoveNorth(SimpleCommand):
    pattern = 'Mn'


class MoveSouth(SimpleCommand):
    pattern = 'Ms'


class MoveWest(SimpleCommand):
    pattern = 'Mw'


class SlewToTargetObject(SlewToTargetAltAz):
    pattern = 'MS'


class SlewToTarget(SlewToTargetObject):
    pass


# Precision toggle

class HighPrecisionToggle(SimpleCommand):
    pattern = 'P'


# XXX FIXME: This also appears documented as 'User Format Control'
class PrecisionPositionToggle(SimpleCommand):
    pattern = 'U'


# XXX TODO: Smart Drive Control

# Movement Commands (halt)

class HaltAll(SimpleCommand):
    pattern = 'Q'


class HaltEastward(SimpleCommand):
    pattern = 'Qe'


class HaltNorthwawrd(SimpleCommand):
    pattern = 'Qn'


class HaltSouthward(SimpleCommand):
    pattern = 'Qs'


class HaltWestward(SimpleCommand):
    pattern = 'Qw'


# XXX TODO: Field de-rotator

# Slew Rate

class SetSlewRateToCentering(SimpleCommand):
    pattern = 'RC'


class SetSlewRateToGuiding(SimpleCommand):
    pattern = 'RG'


class SetSlewRateToFinding(SimpleCommand):
    pattern = 'RM'


class SetSlewRateToMax(SimpleCommand):
    pattern = 'RS'


class SetRightAscentionSlewRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^RA(?P<value>\d\d\.\d)$')


class SetAzimuthSlewRate(SetRightAscentionSlewRate):
    pass


class SetDeclinationSlewRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Re(?P<value>\d\d\.\d)$')


class SetAltitudeSlewRate(SetDeclinationSlewRate):
    pass


class SetGuideRate(SimpleNumericCommand):
    default_type = float
    pattern = re.compile(r'^Rg(?P<value>\d\d\.\d)$')


# XXX TODO: Telescope Set Commands

# Tracking

class IncrementManualRate(SimpleCommand):
    pattern = 'T+'


class DecrementManualRate(SimpleCommand):
    pattern = 'T-'


class SetLunarTracking(SimpleCommand):
    pattern = 'TL'


class SelectCustomTrackingRate(SimpleCommand):
    pattern = 'TM'


class SelectSiderealTrackingRate(SimpleCommand):
    pattern = 'TQ'


class SelectSolarTrackingRate(SimpleCommand):
    pattern = 'TS'


# XXX TODO: PEC
