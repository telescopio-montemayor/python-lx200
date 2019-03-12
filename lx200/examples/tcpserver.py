#!/usr/bin/env python3

import asyncio
import logging

from lx200.parser import Parser
from lx200.store import Store
import lx200.responses


logger = logging.getLogger('lx200.examples.tcpserver')


class LX200Protocol(asyncio.Protocol):
    def __init__(self, store):
        self.transport = None
        self.store = store
        self.parser = Parser()

    def connection_made(self, transport):
        self.transport = transport
        transport.set_write_buffer_limits(high=0, low=0)
        logger.info('Connected: {}'.format(transport.get_extra_info('socket', 'peername')))

    def data_received(self, data):
        decoded_data = data.decode('ascii')
        self.parser.feed(decoded_data)

        logger.debug('<< {}'.format(decoded_data))

        while self.parser.output:
            command = self.parser.output.pop()
            self.store.commit_command(command)

            response = lx200.responses.for_command(command)

            self.store.fill_response(response)

            logger.debug('>> {}'.format(repr(response)))
            logger.debug('>> {}'.format(str(response)))

            self.transport.write(bytes(str(response), 'ascii'))


if __name__ == '__main__':
    import argparse

    logging.basicConfig()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Simulates an LX200 compatible telescope with tcp connection', prog='lx200.examples.tcpserver')

    parser.add_argument('--verbose', required=False, default=False, action='store_true')
    parser.add_argument('--port', type=int, required=False, default=7634)
    parser.add_argument('--host', type=str, required=False, default='127.0.0.1')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    store = Store()

    def protocol_factory(*args, **kwargs):
        return LX200Protocol(store, *args, **kwargs)

    loop = asyncio.get_event_loop()
    coro = loop.create_server(protocol_factory, args.host, args.port)
    server = loop.run_until_complete(coro)

    logger.info('LX200 TCP server example')
    logger.info('Serving on {}'.format(server.sockets[0].getsockname()))

    loop.run_forever()

    server.close()
    loop.run_until_complete(server.wait_closed())
    loop.close()
