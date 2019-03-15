#!/usr/bin/env python3

from enum import Enum
import attr

from lx200 import commands as c
from . import defaults


ALL_RESPONSES = []
COMMAND_RESPONSE_MAP = {}


def for_command(command):
    try:
        response = COMMAND_RESPONSE_MAP.get(command, None)
    except TypeError:
        response = COMMAND_RESPONSE_MAP.get(command.__class__, None)

    if not response:
        raise KeyError('Response not found for command: {}'.format(command))

    default_data = defaults.for_command(command)
    return response(command=command, **default_data)


def register(response):
    ALL_RESPONSES.append(response)
    return response


def map_response(command, *args):
    def check_unique(cmd):
        if cmd in COMMAND_RESPONSE_MAP:
            raise ValueError('Command {} already mapped to a response'.format(cmd))

    def __inner(response):
        check_unique(command)
        COMMAND_RESPONSE_MAP[command] = response
        for cmd in args:
            check_unique(cmd)
            COMMAND_RESPONSE_MAP[cmd] = response
        return response
    return __inner


def get_unmapped_commands():
    return [cmd for cmd in c.ALL_COMMANDS if cmd not in COMMAND_RESPONSE_MAP]


def get_responses_with_bad_defaults():
    out = []
    for command in c.ALL_COMMANDS:
        response = COMMAND_RESPONSE_MAP.get(command, None)
        if response:
            try:
                str(response())
            except Exception as e:
                out.append((command, e))

    return out


@attr.s
class BaseResponse:
    value = attr.ib(default='')
    command = attr.ib(default=None)
    suffix = attr.ib(default='#', repr=False)
    new_line = attr.ib(default=False, repr=False)

    def __str__(self):
        suffix = self.suffix
        if self.new_line:
            suffix += '\n'
        return '{}{}'.format(self.format_value(self.value), suffix)

    def format_value(self, value):
        return str(value)

    def serialize(self):
        """ Returns a dict with current data """

        to_include = [field for field in attr.fields(self.__class__) if field.repr and field.name != 'command']
        return attr.asdict(self, filter=attr.filters.include(*to_include))


@register
@map_response(c.GetAltitude, c.GetDeclination, c.GetSelectedObjectDeclination, c.GetSelectedTargetDeclination)
@map_response(c.GetDistanceToMeridian, c.GetAzimuth)
@attr.s
class DMSResponse(BaseResponse):
    value = attr.ib(default=None, repr=False)
    high_precision = attr.ib(default=True)
    degrees = attr.ib(default=0)
    degrees_separator = attr.ib(default=':', repr=False)
    minutes = attr.ib(default=0)
    minutes_separator = attr.ib(default=':', repr=False)
    seconds = attr.ib(default=0)

    def format_value(self, value):
        out = '{:=+03d}{}{}'.format(self.degrees, self.degrees_separator, self.minutes)
        if self.high_precision:
            out += '{}{:=02.0f}'.format(self.minutes_separator, self.seconds)

        return out


@register
@map_response(c.GetRightAscencion, c.GetSelectedTargetRightAscencion, c.GetSelectedObjectRightAscencion)
@map_response(c.GetSiderealTime)
@attr.s
class HMSResponse(BaseResponse):
    value = attr.ib(default=None, repr=False)
    high_precision = attr.ib(default=True)
    hours = attr.ib(default=0)
    hours_separator = attr.ib(default=':', repr=False)
    minutes = attr.ib(default=0)
    minutes_separator = attr.ib(default=':', repr=False)
    seconds = attr.ib(default=0)

    def format_value(self, value):
        if self.high_precision:
            out = '{:=+03d}{}{}{}{:=02.0f}'.format(self.hours, self.hours_separator, self.minutes, self.minutes_separator, self.seconds)
        else:
            minutes_frac = self.minutes + self.seconds/60.0
            out = '{:=+03d}{}{:=04.1f}'.format(self.hours, self.hours_separator, minutes_frac)

        return out


@register
@map_response(c.EOT, c.LandAlignment, c.PolarAlignment, c.AltAzAlignment, c.SetAltitudeAntiBacklash, c.SetDeclinationAntiBacklash)
@map_response(c.SetAzimuthAntiBacklash, c.SetRightAscentionAntiBacklash, c.IncreaseReticleBrightness, c.DecreaseReticleBrightness)
@map_response(c.SetReticleFlashRate, c.SetReticleFlashDutyCycle, c.SyncSelenographic)
@map_response(c.CalibrateHomePosition, c.SeekHomePosition, c.Sleep, c.Park, c.SetParkPosition, c.WakeUp)
@map_response(c.ToggleTimeFormat, c.Initialize, c.PrecisionPositionToggle)
@map_response(c.GuideEast, c.GuideNorth, c.GuideWest, c.GuideSouth, c.MoveEast, c.MoveNorth, c.MoveWest, c.MoveSouth)
@map_response(c.HaltAll, c.HaltEastward, c.HaltNorthwawrd, c.HaltWestward, c.HaltSouthward)
@map_response(c.SetSlewRateToCentering, c.SetSlewRateToFinding, c.SetSlewRateToGuiding, c.SetSlewRateToMax)
@map_response(c.SetRightAscentionSlewRate, c.SetDeclinationSlewRate, c.SetAltitudeSlewRate, c.SetAzimuthSlewRate, c.SetGuideRate)
@map_response(c.EnableFlexureCorrection, c.DisableFlexureCorrection, c.SetDSTEnabled, c.StepQualityLimit, c.IncrementManualRate)
@map_response(c.DecrementManualRate, c.EnableAltitudePEC, c.EnableAzimuthPEC, c.EnableRightAscencionPEC, c.DisableAltitudePEC)
@map_response(c.DisableAzimuthPEC, c.DisableRightAscencionPEC)
@map_response(c.SetLunarTracking, c.SelectSiderealTrackingRate, c.SelectCustomTrackingRate, c.SelectSolarTrackingRate)
@attr.s
class EmptyResponse(BaseResponse):
    def __str__(self):
        return ''


@register
@map_response(c.AutomaticAlignment, c.GetDailySavingsTimeSettings)
@map_response(c.SetTargetAltitude, c.SetTargetDeclination, c.SetTargetRightAscencion, c.SetTargetAzimuth)
@map_response(c.SetTargetSelenographicLatitude, c.SetTargetSelenographicLongitude)
@map_response(c.SetFaintMagnitude, c.SetFieldDiameter, c.SetSiteLongitude, c.SetSiteLatitude)
@map_response(c.SetUTCOffset, c.SetMaximumElevation, c.SetSmallestObjectSize, c.SetLargestObjectSize)
@map_response(c.SetLocalTime, c.SetLocalSiderealTime, c.BypassDSTEntry)
@map_response(c.SetSite1Name, c.SetSite2Name, c.SetSite3Name, c.SetSite4Name, c.SetObjectSelectionString)
@map_response(c.SetLowestElevation, c.SetBacklashValues, c.SetHomeData, c.SetSensorOffsets, c.SetSlewRate)
@attr.s
class BooleanResponse(BaseResponse):
    value = attr.ib(default=True)
    output_true = attr.ib(default='1')
    output_false = attr.ib(default='0')
    suffix = attr.ib(default='', repr=False)

    def format_value(self, value):
        if value:
            return self.output_true
        else:
            return self.output_false


@register
@map_response(c.SetTrackingRate)
@attr.s
class SetTrackingRate(BooleanResponse):
    output_true = attr.ib(default='2')


@register
@map_response(c.GetTrackingRate)
@attr.s
class GetTrackingRate(BaseResponse):
    value = attr.ib(default=60)

    def format_value(self, value):
        return '{:=04.1f}'.format(value)


@register
@map_response(c.GetHomeData, c.GetBacklashValues)
@attr.s
class GetHomeData(BaseResponse):
    value = attr.ib(default=None, repr=False)
    axis_1 = attr.ib(default=0)
    axis_2 = attr.ib(default=0)

    def format_value(self, value):
        return '{} {}'.format(self.axis_1, self.axis_2)


@register
@map_response(c.SetHandboxDate)
@attr.s
class SetHandboxDate(BooleanResponse):
    output_true = attr.ib(default='1Updating  Planetary Data#                       #')


@register
@map_response(c.SlewToTargetAltAz)
@attr.s
class SlewToTargetAltAz(BooleanResponse):
    output_true = attr.ib(default='0')
    output_false = attr.ib(default='1')


@register
@map_response(c.ACK)
@attr.s
class ACK(BaseResponse):
    suffix = attr.ib(default='', repr=False)
    AltAz = 'A'
    Downloader = 'D'
    Land = 'L'
    Polar = 'P'

    value = attr.ib(default='A')


@register
@map_response(c.SyncDatabase)
@attr.s
class SyncDatabase(BaseResponse):
    value = attr.ib(default=" M31 EX GAL MAG 3.5 SZ178.0'")


@register
@map_response(c.DistanceBars)
@attr.s
class DistanceBars(BaseResponse):
    """ Distance (if not zero isSlewing will return true on INDI side) """
    value = attr.ib(default=0)
    suffix = attr.ib(default='')

    def format_value(self, value):
        if value not in range(6):
            raise ValueError('Value for DistanceBars {} is not in range 0..6'.format(value))

        return '|' * value + '#'


@register
@map_response(c.GetAlignmentMenuEntry0, c.GetAlignmentMenuEntry1, c.GetAlignmentMenuEntry2)
@attr.s
class GetAlignmentMenuEntry(BaseResponse):
    value = attr.ib(default='The Menu Entry (legacy command)')


@register
@map_response(c.GetSite1Name, c.GetSite2Name, c.GetSite3Name, c.GetSite4Name)
@attr.s
class GetSiteName(BaseResponse):
    value = attr.ib('TheSiteName')


@register
@map_response(c.GetLocalTime12H, c.GetLocalTime24H)
@map_response(c.GetFirmwareTime)
@attr.s
class GetLocalTime(BaseResponse):
    value = attr.ib(default=None, repr=False)
    hours = attr.ib(default=10)
    minutes = attr.ib(default=33)
    seconds = attr.ib(default=34)

    def format_value(self, value):
        return '{}:{}:{}'.format(self.hours, self.minutes, self.seconds)


@register
@map_response(c.GetFirmwareDate)
@attr.s
class GetFirmwareDate(BaseResponse):
    value = attr.ib(default=None, repr=False)
    year = attr.ib(default=1999)
    month = attr.ib(default=12)
    day = attr.ib(default=31)

    def format_value(self, value):
        return '{} {} {}'.format(self.month, self.day, self.year)


@register
@map_response(c.GetFirmwareNumber)
@attr.s
class GetFirmwareNumber(BaseResponse):
    value = attr.ib(default=None, repr=False)
    major = attr.ib(default=42)
    minor = attr.ib(default=0)

    def format_value(self, value):
        return '{}.{}'.format(self.major, self.minor)


@register
@map_response(c.GetBrowseBrighterMagnitudeLimit, c.GetBrowseFaintMagnitudeLimit)
@map_response(c.GetUTCOffsetTime)
@attr.s
class SignedFloatResponse(BaseResponse):
    value = attr.ib(default=0)

    def format_value(self, value):
            out = '{:=+05.1f}'.format(value)

            return out


@register
@map_response(c.GetDate)
@attr.s
class DateResponse(BaseResponse):
    value = attr.ib(default=None, repr=False)
    year = attr.ib(default=13)
    month = attr.ib(default=12)
    day = attr.ib(default=11)

    def format_value(self, value):
        return '{:=02d}/{:=02d}/{:=02d}'.format(self.month, self.day, self.year % 100)


@register
@map_response(c.GetClockFormat)
@attr.s
class GetClockFormat(BaseResponse):
    FORMAT12H = False
    FORMAT24H = True
    value = attr.ib(default=True)

    def format_value(self, value):
        if value:
            return '24'
        else:
            return '12'


@register
@map_response(c.GetSelenographicLatitude, c.GetSelenographicLongitude)
@attr.s
class GetSelenographicCoordinate(BaseResponse):
    value = attr.ib(default=None, repr=False)
    degrees = attr.ib(default=99)
    minutes = attr.ib(default=99)

    def format_value(self, value):
        return '{:+d}*{:d}'.format(self.degrees, self.minutes)


@register
@map_response(c.GetFindFieldDiameter)
class GetFindFieldDiameter(BaseResponse):
    pass


@register
@map_response(c.GetSiteLongitude, c.GetSiteLatitude)
class LowPrecisionDMSResponse(DMSResponse):
    high_precision = attr.ib(default=False)


@register
@map_response(c.GetDeepskySearchString)
@attr.s
class GetDeepskySearchString(BaseResponse):
    """
    A string indicating the class of objects returned by FIND/BROWSE.
    A lower-case character means that class is ignored.
    - G Galaxies
    - P Planetary Nebulas
    - D Diffuse Nebulas
    - C Globular Clusters
    - O Open Clusters
    """
    value = attr.ib(default='gpdco')


@register
@map_response(c.GetAlignmentStatus)
@attr.s
class GetAlignmentStatus(BaseResponse):
    value = attr.ib(default=None, repr=False)
    mount = attr.ib(default='P')
    is_tracking = attr.ib(default=False)
    alignment = attr.ib(default=0)

    MOUNT_ALTAZ = 'A'
    MOUNT_EQUATORIAL = 'P'
    MOUNT_GERMAN = 'G'

    NEEDS_ALIGNMENT = 0
    ALIGNED_1_STAR = 1
    ALIGNED_2_STAR = 2
    ALIGNED_3_STAR = 3

    def format_value(self, value):
        if self.is_tracking:
            tracking = 'T'
        else:
            tracking = 'N'

        out = '{}{}{}'.format(self.mount, tracking, self.alignment)
        return out


@register
@map_response(c.GetProductName)
@attr.s
class GetProductName(BaseResponse):
    value = attr.ib(default='python-lx200 implementation')


@register
@map_response(c.HighPrecisionToggle)
class HighPrecisionToggle(BooleanResponse):
    output_true = attr.ib(default='HIGH PRECISION')
    output_false = attr.ib(default='LOW PRECISION')
    HIGH_PRECISION = True
    LOW_PRECISION = False


@register
@map_response(c.SlewToTarget, c.SlewToTargetObject)
@attr.s
class SlewToTarget(BaseResponse):
    suffix = attr.ib(default='', repr=False)
    value = attr.ib(default='0')

    POSSIBLE = '0'
    OBJECT_BELOW_HORIZON = '1 Object is below horizon'
    OBJECT_ABOVE_HIGHER = '2 Object is above higher limit'


@register
@map_response(c.SetBaudRate)
class SetBaudRate(BaseResponse):
    value = attr.ib(default=None, repr=False)
    def format_value(self, value):
        return '1'


# More than one command reverses the meaning of 1 and 0 to signal success or failure.
# Fun.
@register
@map_response(c.SetBrighterLimit)
@attr.s
class SetBrighterLimit(BooleanResponse):
    value = attr.ib(default=True)
    output_true = attr.ib(default='0')
    output_false = attr.ib(default='1')


@register
@map_response(c.GetHighLimit, c.GetLowerLimit)
@attr.s
class GetHighLimit(BaseResponse):
    value = attr.ib(default=0)

    def format_value(self, value):
        return '{:=+03d}*'.format(int(value))


@register
@map_response(c.GetLargerSizeLimit, c.GetSmallerSizeLimit)
@attr.s
class GetLargerSizeLimit(BaseResponse):
    value = attr.ib(default=123)


@register
@map_response(c.GetMinimumQualityForFind)
@attr.s
class GetMinimumQualityForFind(BaseResponse):
    value = attr.ib(default='GD')
    SUPER = 'SU'
    EXCELLENT = 'EX'
    VERY_GOOD = 'VG'
    GOOD = 'GD'
    FAIR = 'FR'
    POOR = 'PR'
    VERY_POOR = 'VP'


# XXX FIXME: the documented response seems wrong
@register
@map_response(c.GetSensorOffsets)
@attr.s
class GetSensorOffsets(BaseResponse):
    value = attr.ib(default=None, repr=False)
    az_error = attr.ib(default=0)
    el_error = attr.ib(default=0)
    home_offset = attr.ib(default=0)

    def format_value(self, value):
        return '{} {} {}'.format(self.az_error, self.el_error, self.home_offset)


@register
@map_response(c.QueryHomeStatus)
@attr.s
class QueryHomeStatus(BaseResponse):
    value = attr.ib(default=1)

    FOUND = 1
    IN_PROGRESS = 2
    FAILED = 0


if __name__ == '__main__':
    import sys

    unmapped = get_unmapped_commands()
    if unmapped:
        print('Unmapped commands:')
        print('\n'.join(repr(item) for item in unmapped))

    bad_defaults = get_responses_with_bad_defaults()
    if bad_defaults:
        print('Bad defaults:')
        print('\n'.join(repr(item) for item in bad_defaults))

    if unmapped or bad_defaults:
        sys.exit(1)
