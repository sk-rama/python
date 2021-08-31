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
        self.logger.debug('__init__')
        socketserver.BaseRequestHandler.__init__(self, request, client_address, server)
        return

    def setup(self):
        self.logger.debug('setup')
        return socketserver.BaseRequestHandler.setup(self)

    def handle(self):
        self.logger.debug('handle')

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
        self.logger.debug('finish')
        return socketserver.BaseRequestHandler.finish(self)

class ForkingTcpServer(socketserver.ForkingTCPServer, socketserver.TCPServer):
    def __init__(self, server_address, handler_class=ForkingRequestHandler):
        self.logger = logging.getLogger('ForkingTcpServer')
        self.logger.debug('__init__')
        socketserver.ForkingTCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        socketserver.ForkingTCPServer.server_activate(self)
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return socketserver.ForkingTCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return socketserver.ForkingTCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return socketserver.ForkingTCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return socketserver.ForkingTCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return socketserver.ForkingTCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
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
