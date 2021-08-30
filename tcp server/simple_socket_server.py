#!/usr/bin/env python3

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

class ForkingTcpServer(socketserver.ForkingTCPServer):
    
    def __init__(self, server_address, handler_class=ForkingRequestHandler):
        self.logger = logging.getLogger('ForkingTcpServer')
        self.logger.debug('__init__')
        socketserver.TCPServer.__init__(self, server_address, handler_class)
        return

    def server_activate(self):
        self.logger.debug('server_activate')
        socketserver.TCPServer.server_activate(self)
        return

    def serve_forever(self):
        self.logger.debug('waiting for request')
        self.logger.info('Handling requests, press <Ctrl-C> to quit')
        while True:
            self.handle_request()
        return

    def handle_request(self):
        self.logger.debug('handle_request')
        return socketserver.TCPServer.handle_request(self)

    def verify_request(self, request, client_address):
        self.logger.debug('verify_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.verify_request(self, request, client_address)

    def process_request(self, request, client_address):
        self.logger.debug('process_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.process_request(self, request, client_address)

    def server_close(self):
        self.logger.debug('server_close')
        return socketserver.TCPServer.server_close(self)

    def finish_request(self, request, client_address):
        self.logger.debug('finish_request(%s, %s)', request, client_address)
        return socketserver.TCPServer.finish_request(self, request, client_address)

    def close_request(self, request_address):
        self.logger.debug('close_request(%s)', request_address)
        return socketserver.TCPServer.close_request(self, request_address)

if __name__ == '__main__':
    import socket
    import threading

    HOST, PORT = "localhost", 9999

#    address = (HOST, PORT) # let the kernel give us a port
#    server = ForkingTcpServer(address, ForkingRequestHandler)
#    ip, port = server.server_address # find out what port we were given
#
#    t = threading.Thread(target=server.serve_forever)
#    t.setDaemon(False) # don't hang on exit
#    t.start()
#
#    print('Server loop running in process:', os.getpid())
#
#    logger = logging.getLogger('client')
#    logger.info('Server on %s:%s', ip, port)
with ForkingTcpServer((HOST, PORT), ForkingRequestHandler) as server:
    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()
