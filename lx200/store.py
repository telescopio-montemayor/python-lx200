#!/usr/bin/env python3

from collections import defaultdict


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
    def __init__(self, *args, **kwargs):

        return super().__init__(Store, *args, **kwargs)

    def commit_command(self, command):
        path = get_store_path(command)

        # XXX FIXME: we should probably log this, but many commands will not implement the store interface
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
