#!/usr/bin/env python3

import asyncio
import logging

from aiohttp import web

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


async def run():
    import argparse

    logging.basicConfig()
    logger.setLevel(logging.INFO)

    parser = argparse.ArgumentParser(description='Simulates an LX200 compatible telescope with tcp connection', prog='lx200.examples.tcpserver')

    parser.add_argument('--verbose', required=False, default=False, action='store_true')
    parser.add_argument('--port', type=int, required=False, default=7634, help='TCP port for the LX200 server (%(default)s)')
    parser.add_argument('--web-port', type=int, required=False, default=8081, help='TCP port for the status server (%(default)s)')
    parser.add_argument('--host', type=str, required=False, default='127.0.0.1', help='Host for all the servers (%(default)s)')
    args = parser.parse_args()

    if args.verbose:
        logger.setLevel(logging.DEBUG)

    store = Store()

    def protocol_factory(*args, **kwargs):
        return LX200Protocol(store, *args, **kwargs)

    loop = asyncio.get_running_loop()
    server = await loop.create_server(protocol_factory, args.host, args.port)

    routes = web.RouteTableDef()

    @routes.get('/')
    async def json_store_status(request):
        return web.json_response(request.app['scope_store'])

    app = web.Application()
    app['scope_store'] = store

    app.add_routes(routes)

    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, args.host, args.web_port)
    await site.start()

    logger.info('LX200 TCP server example')
    logger.info('Serving on {}'.format(server.sockets[0].getsockname()))
    logger.info('Serving state on http://{}:{}'.format(args.host, args.web_port))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(run())
    loop.run_forever()
