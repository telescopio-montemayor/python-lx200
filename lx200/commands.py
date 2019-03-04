#!/usr/bin/env python3

import re

COMMAND_START = ':'
COMMAND_END = '#'


def is_command(data, command):
    return command.can_be(data) is not None


class BaseCommand:
    value = None

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
    value = 0

    def parse(self, matches, data):
        self.value = int(matches.group(1))
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
