#!/usr/bin/env python3

# source: https://pymotw.com/2/SocketServer/

import os
import logging
import sys
import socketserver

logging.basicConfig(level=logging.DEBUG, format='%(asctime)-15s %(name)s: %(message)s')

class ForkingRequestHandler(socketserver.BaseRequestHandler):
    
    def __init__(self, request, client_address, server):
        self.logger = logging.getLogger('ForkingRequestHandler')
        self.logger.debug(f'ForkingRequestHandler __init__ {os.getpid()}')
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug(f'setup {os.getpid()}')
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug(f'handle {os.getpid()}')

        # Echo the back to the client
        data = self.request.recv(1024)
        self.logger.debug(f'recv()->{data}')
        data = data.decode('utf-8')
        cur_pid = os.getpid()
        response = f'({cur_pid}, {data})'.encode('utf-8')
        self.request.send(response)
        self.logger.debug(f'send()->{response}')
        return

    def finish(self):
        self.logger.debug(f'finish {os.getpid()}')
        return socketserver.BaseRequestHandler.finish(self)

class ForkingTcpServer(socketserver.ForkingTCPServer, socketserver.TCPServer):
    def __init__(self, server_address, handler_class=ForkingRequestHandler):
        self.logger = logging.getLogger('ForkingTcpServer')
        self.logger.debug(f'__init__ {os.getpid()}')
        socketserver.ForkingTCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug(f'server_activate {os.getpid()}')
        socketserver.ForkingTCPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug(f'waiting for request {os.getpid()}')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        return socketserver.ForkingTCPServer.serve_forever(self)

    def handle_request(self):
        self.logger.debug(f'handle_request {os.getpid()}')
        return socketserver.ForkingTCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug(f'verify_request {os.getpid()}: requeest: {request}, client: {client_address}')
        return socketserver.ForkingTCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug(f'process_request {os.getpid()}: request: {request}, client: {client_address}')
        return socketserver.ForkingTCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug(f'server_close {os.getpid()}')
        return socketserver.ForkingTCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug(f'finish_request {os.getpid()}: request: {request}, client: {client_address}')
        return socketserver.ForkingTCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug(f'close_request {os.getpid()}: request address: {request_address}')
        return socketserver.ForkingTCPServer.close_request(self, request_address)


if __name__ == '__main__':
    import socket
    import threading

    HOST, PORT = "0.0.0.0", 9999

    with ForkingTcpServer((HOST, PORT), ForkingRequestHandler) as server:
        # Activate the server; this will keep running until you
        # interrupt the program with Ctrl-C
        logger = logging.getLogger('server')
        print('Server loop running in process:', os.getpid())
        logger.info('Server on %s:%s', HOST, PORT)
        server.serve_forever()
