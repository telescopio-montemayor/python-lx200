#!/usr/bin/env python3

import asyncio

from lx200.parser import Parser
from lx200.store import Store
import lx200.responses


class LX200Protocol(asyncio.Protocol):
    def __init__(self, store):
        self.transport = None
        self.store = store
        self.parser = Parser()

    def connection_made(self, transport):
        self.transport = transport
        print('Connected: ', transport.get_extra_info('socket', 'peername'))

    def data_received(self, data):
        self.parser.feed(data.decode('ascii'))
        while self.parser.output:
            command = self.parser.output.pop()
            self.store.commit_command(command)

            response = lx200.responses.for_command(command)

            self.store.fill_response(response)
            self.transport.write(bytes(str(response), 'ascii'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Simulates an LX200 compatible telescope with tcp connection', prog='lx200.examples.tcpserver')

    parser.add_argument('--port', type=int, required=False, default=7634)
    parser.add_argument('--host', type=str, required=False, default='127.0.0.1')
    args = parser.parse_args()

    store = Store()

    def protocol_factory(*args, **kwargs):
        return LX200Protocol(store, *args, **kwargs)

    loop = asyncio.get_event_loop()
    coro = loop.create_server(protocol_factory, args.host, args.port)
    server = loop.run_until_complete(coro)

    print('LX200 TCP server example')
    print('Serving on {}'.format(server.sockets[0].getsockname()))

    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
