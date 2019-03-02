#!/usr/bin/env python3

import re

COMMAND_START = ':'
COMMAND_END = '#'


def is_command(data, command):
    return command.can_be(data) is not None


class BaseCommand:
    @classmethod
    def parse(cls, data):
        """ Tries to parse the given data block as this command.
        If successful returns a new instance of this command properly
        initialized or None otherwise"""
        raise NotImplementedError

    @classmethod
    def can_be(cls, data):
        """ Returns True if data can be parsed as this command"""
        raise NotImplementedError


class SimpleCommand(BaseCommand):
    pattern = None

    @classmethod
    def parse(cls, data):
        raise NotImplementedError

    @classmethod
    def can_be(cls, data):
        if cls.pattern is None:
            raise NotImplementedError('Command pattern is not defined')

        try:
            return cls.pattern.fullmatch(data)
        except AttributeError:
            return (data == cls.pattern) or (data == bytes(cls.pattern, 'utf-8'))


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

class SetAltitudeAntiBacklash(SimpleCommand):
    pattern = re.compile(r'^\$BA(\d\d)$')


class SetDeclinationAntiBacklash(SetAltitudeAntiBacklash):
    pass


class SetAzimuthAntiBacklash(SimpleCommand):
    pattern = re.compile(r'^\$BZ(\d\d)$')


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
