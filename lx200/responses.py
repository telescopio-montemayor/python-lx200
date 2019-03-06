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

    def __str__(self):
        return '{}\n'.format(self.format_value(self.value))

    def format_value(self, value):
        return str(value)


@register
@map_response(c.EOT, c.LandAlignment, c.PolarAlignment, c.AltAzAlignment, c.SetAltitudeAntiBacklash, c.SetDeclinationAntiBacklash)
@map_response(c.SetAzimuthAntiBacklash, c.SetRightAscentionAntiBacklash, c.IncreaseReticleBrightness, c.DecreaseReticleBrightness)
@map_response(c.SetReticleFlashRate, c.SetReticleFlashDutyCycle, c.SyncSelenographic)
class EmptyResponse(BaseResponse):
    pass


@register
@map_response(c.AutomaticAlignment)
class BooleanResponse(BaseResponse):
    def format_value(self, value):
        if value:
            return '1'
        else:
            return '0'


@register
@map_response(c.ACK)
@attr.s
class ACK(BaseResponse):
    AltAz = 'A'
    Downloader = 'D'
    Land = 'L'
    Polar = 'P'

    value = attr.ib(default='A')


@register
@map_response(c.SyncDatabase)
@attr.s
class SyncDatabase(BaseResponse):
    value = attr.ib(default=" M31 EX GAL MAG 3.5 SZ178.0'#")


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
        return '{}#'.format(value)


@register
@map_response(c.GetLocalTime12H)
@attr.s
class GetLocalTime12H(BaseResponse):
    hours = attr.ib(default=0)
    minutes = attr.ib(default=0)
    seconds = attr.ib(default=0)

    def format_value(self, value):
        return '{}:{}:{}#'.format(self.hours, self.minutes, self.seconds)



