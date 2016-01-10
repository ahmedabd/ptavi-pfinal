#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
import socket

CONFIG = sys.argv[1]
FICH_AUDIO = 'cancion.mp3'

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

    dicc = {}

    def handle(self):
        while 1:
            line = self.rfile.read()
            linea = line.decode('utf-8')
            linea_lista = linea.split()



            print("El servidor Proxy nos manda " + line.decode('utf-8'))
            if not line:
                break
            if linea_lista[0] == 'INVITE':
                print(linea_lista)
                mensaje = self.wfile.write(b'SIP/2.0 100 Trying' + b'\r\n\r\n' + b'SIP/2.0 180 Ring' + b'\r\n\r\n' + b'SIP/2.0 200 OK' + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[3] + linea_lista[4], 'utf-8')) + b'\r\n\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[5], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[6] + ' ' + linea_lista[7], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[8], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[9], 'utf-8')) + b'\r\n')
                mensaje += self.wfile.write((bytes(linea_lista[10] + ' ' + puerto_rtp + ' ' + linea_lista[12], 'utf-8')) + b'\r\n\r\n')
                self.dicc[linea_lista[6].split('=')[1]] = [linea_lista[11], linea_lista[7]]
            
            if linea_lista[0] == 'ACK':
                [puerto_receptor, ip_receptor] = self.dicc[linea_lista[1].split(':')[1]]
                aEjecutar = './mp32rtp -i ' + ip_receptor + ' ' '-p ' + str(puerto_receptor) + ' ' + '< ' + FICH_AUDIO
                print('Vamos a ejecutar', aEjecutar)
                os.system(aEjecutar)

            if linea_lista[0] == 'BYE':
                mensaje = self.wfile.write(b'SIP/2.0 200 OK' + b'\r\n\r\n')
                
                

            
if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip_server, int(puerto_server)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
