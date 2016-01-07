#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
import socket

CONFIG = sys.argv[1]

with open(CONFIG, 'r') as file3:
    lineas = file3.readlines()
    usuario = lineas[1].split()[1].split('"')[1]
    passwd = lineas[1].split()[2].split('"')[1]
    ip_server = lineas[2].split()[1].split('"')[1]
    puerto_server = lineas[2].split()[2].split('"')[1]
    puerto_rtp = lineas[3].split()[1].split('"')[1]
    ip_proxy = lineas[4].split()[1].split('"')[1]
    puerto_proxy = lineas[4].split()[2].split('"')[1]
    log_path = lineas[5].split()[1].split('"')[1]
    audio_path = lineas[6].split()[1].split('"')[1]

class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Recibimos peticiones SIP y enviamos mensajes o servicios
    """

    def handle(self):
        while 1:
            line = self.rfile.read()
            linea = line.decode('utf-8')
            linea_lista = linea.split()

            print("El servidor Proxy nos manda " + line.decode('utf-8'))
            if not line:
                break
            if linea_lista[0] == 'INVITE':
                mensaje = self.wfile.write(b'SIP/2.0 100 Trying' + b'\r\n\r\n' + b'SIP/2.0 180 Ring' + b'\r\n\r\n' + b'SIP/2.0 200 OK' + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[3] + linea_lista[4], 'utf-8')) + b'\r\n\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[5], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[6], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[7], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[8], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[9] + ' ' + linea_lista[10] + ' ' + linea_lista[11], 'utf-8')) + b'\r\n\r\n')

            
if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip_server, int(puerto_server)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
