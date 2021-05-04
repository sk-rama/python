#!/usr/bin/env python

import socket

HOST = ''                 # Symbolic name meaning all available interfaces
PORT = 9100               # Arbitrary non-privileged port

def listen():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as connection:
        connection.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        connection.bind((HOST, PORT))
        connection.listen()
        current_connection, address = connection.accept()
        with current_connection:
            while True:
                data = current_connection.recv(2048)

                if data in [b'close\r\n', b'exit\r\n', b'quit\r\n', b'down\r\n', b'shutdown\r\n']:
                    current_connection.shutdown(socket.SHUT_RDWR)
                    current_connection.close()
                    exit()

                elif data:
                    current_connection.sendall(data)
                    print(data)


if __name__ == "__main__":
    try:
        listen()
    except KeyboardInterrupt:
        pass
