#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
import socket
import time
import json
import random
import hashlib


def log(File, Mensaje):
    with open(File, 'r') as fich:
        lineas = fich.readlines()

    lineas.append(str(time.time()) + ' ' + Mensaje)
    with open(File, 'w') as fich:
        fich.write(''.join(lineas))

CONFIG = sys.argv[1]
FICH_AUDIO = 'cancion.mp3'

with open(CONFIG, 'r') as fich_proxy:
    lineas2 = fich_proxy.readlines()
    nombre_proxy = lineas2[1].split()[1].split('"')[1]
    ip_proxy2 = lineas2[1].split()[2].split('"')[1]
    puerto_proxy2 = lineas2[1].split()[3].split('"')[1]
    data_path = lineas2[2].split()[1].split('"')[1]
    passwd_path = lineas2[2].split()[2].split('"')[1]
    log_path2 = lineas2[3].split()[1].split('"')[1]

with open('ua2.xml', 'r') as fich_serv:
    lineas3 = fich_serv.readlines()
    usuario3 = lineas3[1].split()[1].split('"')[1]
    passwd3 = lineas3[1].split()[2].split('"')[1]
    ip_server3 = lineas3[2].split()[1].split('"')[1]
    puerto_server3 = lineas3[2].split()[2].split('"')[1]
    puerto_rtp3 = lineas3[3].split()[1].split('"')[1]
    ip_proxy3 = lineas3[4].split()[1].split('"')[1]
    puerto_proxy3 = lineas3[4].split()[2].split('"')[1]
    log_path3 = lineas3[5].split()[1].split('"')[1]
    audio_path3 = lineas3[6].split()[1].split('"')[1]

with open('ua1.xml', 'r') as fich_client:
    lineas = fich_client.readlines()
    usuario = lineas[1].split()[1].split('"')[1]
    passwd = lineas[1].split()[2].split('"')[1]
    ip_server = lineas[2].split()[1].split('"')[1]
    puerto_server = lineas[2].split()[2].split('"')[1]
    puerto_rtp = lineas[3].split()[1].split('"')[1]
    ip_proxy = lineas[4].split()[1].split('"')[1]
    puerto_proxy = lineas[4].split()[2].split('"')[1]
    log_path = lineas[5].split()[1].split('"')[1]
    audio_path = lineas[6].split()[1].split('"')[1]

LINE2 = 'INVITE' + ' ' + 'sip:' + usuario3 + ':' + puerto_proxy3 + ' ' + 'SIP/2.0\r\n' + 'Content-Type: application/sdp' + '\r\n\r\n'
LINE2 += 'v=0' + '\r\n' + 'o=' + usuario3 + ' ' + ip_server3 + '\r\n' + 's=misesion' + '\r\n' + 't=0' + '\r\n' + 'm=audio' + ' ' + puerto_rtp + ' ' + 'RTP'
LINE3 = 'ACK ' + 'sip:' + usuario3 + ' ' + 'SIP/2.0' + '\r\n\r\n'
LINE4 = 'BYE ' + 'sip:' + usuario3 + ' ' + 'SIP/2.0' + '\r\n\r\n'


class EchoHandler(socketserver.DatagramRequestHandler):
    """
    Recibimos peticiones SIP y enviamos mensajes o servicios
    """

    dicc = {}
    noncelib = {}

    def handle(self):
        while 1:
            line = self.rfile.read()
            linea = line.decode('utf-8')
            linea_lista = linea.split()
            ip_cliente = self.client_address[0]
            puerto_cliente = self.client_address[1]
            nonce = random.getrandbits(100)
            print("El cliente nos manda " + line.decode('utf-8'))
            if not line:
                break
            if linea_lista[0] == 'REGISTER' and len(linea_lista) == 5:
                log(log_path2, 'Starting ... \r\n')
                log(log_path2, 'Recived from ' + ip_cliente + ':' + linea_lista[1].split(':')[2] + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                self.wfile.write(b'SIP/2.1 401 Unauthorized' + b'\r\n')
                self.wfile.write(b'WWW Authenticate: nonce = ' + bytes(str(nonce), 'utf-8') + b'\r\n\r\n')
                self.noncelib[linea_lista[1].split(':')[1]] = nonce
            if linea_lista[0] == 'REGISTER' and len(linea_lista) == 7:
                log(log_path2, 'Recived from ' + ip_cliente + ':' + linea_lista[1].split(':')[2] + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                self.wfile.write(b'SIP/2.0 200 OK' + b'\r\n\r\n')
                log(log_path2, 'Sent to ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join('SIP/2.0 200 OK'.split('\r\n')) + '\r\n')
                if linea_lista[4] == '0':
                    (registro, direccion, mensaje, expires, tiempo, autorizacion, response) = linea_lista
                    del self.dicc[direccion]
                    print(self.dicc)
                    self.register2json()
                elif linea_lista[4] > '0':
                    ip = self.client_address[0]
                    (registro, direccion, mensaje, expires, tiempo, autorizacion, response) = linea_lista
                    self.dicc[direccion] = [ip, time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + int(tiempo)))]
                    self.register2json()
            if linea_lista[0] == 'INVITE':
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((ip_server3, int(puerto_server3)))
                print(linea_lista)
                log(log_path2, 'Recived from ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                log(log_path2, 'Sent to ' + ip_server3 + ':' + puerto_server3 + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                print("Enviando: " + 'INVITE')
                my_socket.send(bytes(LINE2, 'utf-8') + b'\r\n\r\n')
                data = my_socket.recv(1024)
                datos = data.decode('utf-8')
                datos_lista = datos.split('\r\n')
                print('Recibido -- ', datos)
                log(log_path2, 'Recived from ' + ip_server3 + ':' + (puerto_server3) + ' ' + ' '.join(datos_lista) + '\r\n')
                RCV = datos_lista[0:5]

                if RCV == ['SIP/2.0 100 Trying', '', 'SIP/2.0 180 Ring', '', 'SIP/2.0 200 OK']:
                    log(log_path2, 'Sent to ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(datos_lista) + '\r\n')
                    mensaje = self.wfile.write(b'SIP/2.0 100 Trying' + b'\r\n\r\n' + b'SIP/2.0 180 Ring' + b'\r\n\r\n' + b'SIP/2.0 200 OK' + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[3] + ' ' + linea_lista[4], 'utf-8')) + b'\r\n\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[5], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[6] + ' ' + linea_lista[7], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[8], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[9], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[10] + ' ' + puerto_rtp3 + ' ' + linea_lista[12], 'utf-8')) + b'\r\n\r\n')

            if linea_lista[0] == 'ACK':
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((ip_server3, int(puerto_server3)))
                log(log_path2, 'Recived from ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                print("Enviando: " + 'ACK')
                my_socket.send(bytes(LINE3, 'utf-8') + b'\r\n\r\n')
                log(log_path2, 'Sent to ' + ip_server3 + ':' + puerto_server3 + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
            if linea_lista[0] == 'BYE':
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((ip_server3, int(puerto_server3)))
                log(log_path2, 'Recived from ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                log(log_path2, 'Sent to ' + ip_server3 + ':' + puerto_server3 + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                print("Enviando: " + 'BYE')
                my_socket.send(bytes(LINE4, 'utf-8') + b'\r\n\r\n')
                data = my_socket.recv(1024)
                datos = data.decode('utf-8')
                datos_lista = datos.split('\r\n')
                print('Recibido -- ', datos)
                log(log_path2, 'Recived from ' + ip_server3 + ':' + puerto_server3 + ' ' + ' '.join(datos_lista) + '\r\n')
                log(log_path2, 'Sent to ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(datos_lista) + '\r\n')
                RCV = datos_lista[0:1]
                if RCV == ['SIP/2.0 200 OK']:
                    mensaje = self.wfile.write(b'SIP/2.0 200 OK' + b'\r\n\r\n')

    def register2json(self):
        """
        Registra usuarios en un fichero json
        """
        with open(data_path, 'w') as data_base:
            json.dump(self.dicc, data_base, indent=4, separators=(',', ':'))

    def json2register(self):
        """
        Dependiendo de si exista o no el fichero el método ejecutará una cosa u otra
        """
        try:
            with open(data_path, 'w') as data_base:
                self.dicc = json.loads(data_base)
        except:
            pass

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip_proxy2, int(puerto_proxy2)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
