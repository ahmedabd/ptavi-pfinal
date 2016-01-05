#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import sys
import os

CONFIG = sys.argv[1]

with open(CONFIG, 'r') as file2:
    lineas = file2.readlines()
    nombre_proxy = lineas[1].split()[1].split('"')[1]
    ip_proxy = lineas[1].split()[2].split('"')[1]
    puerto_proxy = lineas[1].split()[3].split('"')[1]
    data_path = lineas[2].split()[1].split('"')[1]
    passwd_path = lineas[2].split()[2].split('"')[1]
    log_path = lineas[3].split()[1].split('"')[1]


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Recibimos peticiones SIP y enviamos mensajes o servicios
    """

    def handle(self):
        while 1:
            line = self.rfile.read()
            linea = line.decode('utf-8')
            linea_lista = linea.split()

            print("El cliente nos manda " + line.decode('utf-8'))
            if not line:
                break
            if linea_lista[0] == 'REGISTER' and len(linea_lista) == 5:
                self.wfile.write(b'SIP/2.1 401 Unauthorized' + b'\r\n')
                self.wfile.write(b'WWW Authenticate: nonce ="898989"' + b'\r\n\r\n')
            if linea_lista[0] == 'REGISTER' and len(linea_lista) == 7:
                self.wfile.write(b'SIP/2.0 200 OK' + b'\r\n\r\n')

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip_proxy, int(puerto_proxy)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
