#!/usr/bin/env python3

from collections import defaultdict

import lx200.responses.defaults as response_defaults
import lx200.commands


def get_paths(command):
    return {
        'store': getattr(command, 'store_path', None),
        'load': getattr(command, 'load_path', None)
    }


def get_load_path(command):
    paths = get_paths(command)
    return paths['load'] or paths['store']


def get_store_path(command):
    paths = get_paths(command)
    return paths['store'] or paths['load']


class Store(defaultdict):
    def __init__(self, seed_from_defaults=True, *args, **kwargs):

        super().__init__(lambda: defaultdict(dict), *args, **kwargs)

        if seed_from_defaults:
            paths_to_create = [get_store_path(cmd) for cmd in lx200.commands.ALL_COMMANDS]
            for path in paths_to_create:
                if path is None:
                    continue
                self[path] = defaultdict(dict)

            for command, defaults in response_defaults.COMMAND_DEFAULT_MAP.items():
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
        data = self[path]

        for key, value in data.items():
            setattr(response, key, value)

        return response
