#!/usr/bin/env python3

from enum import Enum
import attr

from . import commands as c


ALL_RESPONSES = []
COMMAND_RESPONSE_MAP = {}


def register(response):
    ALL_RESPONSES.append(response)
    return response


def map_response(command, *args):
    def __inner(response):
        COMMAND_RESPONSE_MAP[command] = response
        for cmd in args:
            COMMAND_RESPONSE_MAP[cmd] = response
        return response
    return __inner


def get_unmapped_commands():
    return [cmd for cmd in c.ALL_COMMANDS if cmd not in COMMAND_RESPONSE_MAP]


@attr.s
class BaseResponse:
    value = attr.ib(default='')
    command = attr.ib(default=None)
    suffix = attr.ib(default='#')

    def __str__(self):
        return '{}{}\n'.format(self.format_value(self.value), self.suffix)

    def format_value(self, value):
        return str(value)


@register
@map_response(c.GetAltitude, c.GetDeclination, c.GetSelectedObjectDeclination, c.GetSelectedTargetDeclination)
@map_response(c.GetDistanceToMeridian, c.GetAzimuth)
@attr.s
class DMSResponse(BaseResponse):
    high_precision = attr.ib(default=True)
    degrees = attr.ib(default=0)
    degrees_separator = attr.ib(default='*')
    minutes = attr.ib(default=0)
    minutes_separator = attr.ib(default='\'')
    seconds = attr.ib(default=0)

    def format_value(self, value):
        out = '{:=+03d}{}{}'.format(self.degrees, self.degrees_separator, self.minutes)
        if self.high_precision:
            out += '{}{:=02.0f}'.format(self.minutes_separator, self.seconds)

        return out + self.suffix


@register
@map_response(c.GetRightAscencion, c.GetSelectedTargetRightAscencion, c.GetSelectedObjectRightAscencion)
@map_response(c.GetSiderealTime, c.GetFirmwareTime, )
@attr.s
class HMSResponse(BaseResponse):
    high_precision = attr.ib(default=True)
    hours = attr.ib(default=0)
    hours_separator = attr.ib(default=':')
    minutes = attr.ib(default=0)
    minutes_separator = attr.ib(default=':')
    seconds = attr.ib(default=0)

    def format_value(self, value):
        if self.high_precision:
            out = '{:=+03d}{}{}{}{:=02.0f}'.format(self.degrees, self.degrees_separator, self.minutes, self.minutes_separator, self.seconds)
        else:
            minutes_frac = self.minutes + self.seconds/60.0
            out = '{:=+03d}{}{:=04.1f}'.format(self.degrees, self.degrees_separator, minutes_frac)

        return out + self.suffix


@register
@map_response(c.EOT, c.LandAlignment, c.PolarAlignment, c.AltAzAlignment, c.SetAltitudeAntiBacklash, c.SetDeclinationAntiBacklash)
@map_response(c.SetAzimuthAntiBacklash, c.SetRightAscentionAntiBacklash, c.IncreaseReticleBrightness, c.DecreaseReticleBrightness)
@map_response(c.SetReticleFlashRate, c.SetReticleFlashDutyCycle, c.SyncSelenographic)
@map_response(c.CalibrateHomePosition, c.SeekHomePosition, c.Sleep, c.Park, c.SetParkPosition, c.WakeUp)
@map_response(c.ToggleTimeFormat, c.Initialize)
@map_response(c.GuideEast, c.GuideNorth, c.GuideWest, c.GuideSouth, c.MoveEast, c.MoveNorth, c.MoveWest, c.MoveSouth)
@map_response(c.HaltAll, c.HaltEastward, c.HaltNorthwawrd, c.HaltWestward, c.HaltSouthward)
@map_response(c.SetSlewRateToCentering, c.SetSlewRateToFinding, c.SetSlewRateToGuiding, c.SetSlewRateToMax)
@map_response(c.SetRightAscentionSlewRate, c.SetDeclinationSlewRate, c.SetAltitudeSlewRate, c.SetAzimuthSlewRate, c.SetGuideRate)
@map_response(c.EnableFlexureCorrection, c.DisableFlexureCorrection, c.SetDSTEnabled, c.StepQualityLimit, c.IncrementManualRate)
@map_response(c.DecrementManualRate, c.EnableAltitudePEC, c.EnableAzimuthPEC, c.EnableRightAscencionPEC, c.DisableAltitudePEC)
@map_response(c.DisableAzimuthPEC, c.DisableRightAscencionPEC)
@map_response(c.SetLunarTracking, c.SelectSiderealTrackingRate, c.SelectCustomTrackingRate, c.SelectSolarTrackingRate)
class EmptyResponse(BaseResponse):
    pass


# XXX FIXME: some parts of the documentation use a '#' as suffix for these responses
@register
@map_response(c.AutomaticAlignment, c.GetDailySavingsTimeSettings)
class BooleanResponse(BaseResponse):
    suffix = ''

    def format_value(self, value):
        if value:
            return '1'
        else:
            return '0'


@register
@map_response(c.ACK)
@attr.s
class ACK(BaseResponse):
    suffix = ''
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
    value = attr.ib(default=1)

    def format_value(self, value):
        value = int(value)
        if value not in range(11):
            raise ValueError('Value for DistanceBars not in range(0, 11)')

        bars = '|' * value
        return bars


@register
@map_response(c.GetAlignmentMenuEntry0, c.GetAlignmentMenuEntry1, c.GetAlignmentMenuEntry2)
@attr.s
class GetAlignmentMenuEntry(BaseResponse):
    value = attr.ib(default='The Menu Entry (legacy command)')

    def format_value(self, value):
        return '{}'.format(value)


@register
@map_response(c.GetSite1Name, c.GetSite2Name, c.GetSite3Name, c.GetSite4Name)
@attr.s
class GetSiteName(BaseResponse):
    value = attr.ib('The site name')


@register
@map_response(c.GetLocalTime12H, c.GetLocalTime24H)
@map_response(c.GetFirmwareTime)
@attr.s
class GetLocalTime(BaseResponse):
    hours = attr.ib(default=0)
    minutes = attr.ib(default=0)
    seconds = attr.ib(default=0)

    def format_value(self, value):
        return '{}:{}:{}'.format(self.hours, self.minutes, self.seconds)


@register
@map_response(c.GetBrowseBrighterMagnitudeLimit, c.GetBrowseFaintMagnitudeLimit)
@map_response(c.GetUTCOffsetTime)
class SignedFloatResponse(BaseResponse):

    def format_value(self, value):
            out = '{:=+05.1f}'.format(value)

            return out


@register
@map_response(c.GetDate)
@attr.s
class DateResponse(BaseResponse):
    year = attr.ib(default=0)
    month = attr.ib(default=0)
    day = attr.ib(default=0)

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
            return '12'
        else:
            return '24'


@register
@map_response(c.GetSelenographicLatitude, c.GetSelenographicLongitude)
@attr.s
class GetSelenographicCoordinate(BaseResponse):
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
    high_precision = False


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
