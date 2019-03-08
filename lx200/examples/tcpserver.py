#!/usr/bin/env python3

import asyncio

from lx200.parser import Parser
import lx200.responses


class LX200Protocol(asyncio.Protocol):
    def __init__(self):
        self.transport = None
        self.parser = Parser()

    def connection_made(self, transport):
        self.transport = transport
        print('Connected: ', transport.get_extra_info('socket', 'peername'))

    def data_received(self, data):
        self.parser.feed(data.decode('ascii'))
        while self.parser.output:
            command = self.parser.output.pop()
            response = lx200.responses.for_command(command)
            self.transport.write(bytes(str(response), 'ascii'))


if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser(description='Simulates an LX200 compatible telescope with tcp connection', prog='lx200.examples.tcpserver')

    parser.add_argument('--port', type=int, required=False, default=7634)
    parser.add_argument('--host', type=str, required=False, default='127.0.0.1')
    args = parser.parse_args()

    loop = asyncio.get_event_loop()
    coro = loop.create_server(LX200Protocol, args.host, args.port)
    server = loop.run_until_complete(coro)

    print('LX200 TCP server example')
    print('Serving on {}'.format(server.sockets[0].getsockname()))

    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
