#!/usr/bin/env python3

from collections import defaultdict

import munch

import lx200.responses.defaults as response_defaults
import lx200.commands


def get_paths(command):
    return {
        'store': getattr(command, 'store_path', None),
        'load': getattr(command, 'load_path', None)
    }


def get_load_path(command):
    paths = get_paths(command)
    path = paths['load'] or paths['store']

    if path is not None:
        path = path.format(**command.serialize())
    return path


def get_store_path(command):
    paths = get_paths(command)
    path = paths['store'] or paths['load']

    if path is not None:
        path = path.format(**command.serialize())
    return path


class Store(defaultdict):
    def __init__(self, seed_from_defaults=True, *args, **kwargs):

        super().__init__(lambda: defaultdict(dict), *args, **kwargs)

        if seed_from_defaults:
            for cmd in lx200.commands.ALL_COMMANDS:
                command = cmd()
                path = get_store_path(command)
                if path is None:
                    continue

                stored_data = self[path]
                if hasattr(command, 'store_value'):
                    for key, value in command.store_value.items():
                        stored_data.setdefault(key, value)

            for cmd, defaults in response_defaults.COMMAND_DEFAULT_MAP.items():
                command = cmd()
                path = get_store_path(command)
                if path is None:
                    continue
                self[path].update(defaults)

    def commit_command(self, command):
        path = get_store_path(command)

        if path is None:
            return

        data = command.serialize()
        self[path].update(data)

        return command

    def fill_response(self, response):

        command = response.command
        if command is None:
            raise ValueError('Response {} does not have a command assigned'.format(response))

        path = get_load_path(command)
        if path is None:
            return

        data = self[path]

        for key, value in data.items():
            setattr(response, key, value)

        return response

    def toJSON(self, indent=4):
        return munch.munchify(self).toJSON(indent=indent, sort_keys=True)

    def toYAML(self, indent=4):
        return munch.munchify(self).toYAML(indent=indent)
