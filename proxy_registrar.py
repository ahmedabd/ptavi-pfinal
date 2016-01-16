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
                log(log_path2, 'Sent to ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join('SIP/2.0 200 OK'.split('\r\n')) + '\r\n')
                self.noncelib[linea_lista[1].split(':')[1]] = nonce

            if linea_lista[0] == 'REGISTER' and len(linea_lista) == 8:
                with open(passwd_path, 'r') as passwords:
                    Linea = passwords.readlines()
                    if Linea[0].split()[1] == linea_lista[1].split(':')[1]:
                        passwd = Linea[0].split()[3]
                        m = hashlib.md5()
                        m.update(bytes(passwd + str(self.noncelib[linea_lista[1].split(':')[1]]), 'utf-8'))
                        response = m.hexdigest()
                        if response == linea_lista[7].split('=')[1]:
                            self.wfile.write(b'SIP/2.0 200 OK' + b'\r\n\r\n')
                        else:
                            print('Usuario no encontrado')
                with open(passwd_path, 'r') as passwords:
                    Linea = passwords.readlines()
                    if Linea[1].split()[1] == linea_lista[1].split(':')[1]:
                        passwd = Linea[1].split()[3]
                        m = hashlib.md5()
                        m.update(bytes(passwd + str(self.noncelib[linea_lista[1].split(':')[1]]), 'utf-8'))
                        response = m.hexdigest()
                        if response == linea_lista[7].split('=')[1]:
                            self.wfile.write(b'SIP/2.0 200 OK' + b'\r\n\r\n')
                        else:
                            print('Usuario no encontrado')

                if linea_lista[4] == '0':
                    (registro, direccion, mensaje, expires, tiempo, autorizacion, digest, response) = linea_lista
                    del self.dicc[direccion]
                    self.register2json()
                elif linea_lista[4] > '0':
                    ip = self.client_address[0]
                    (registro, direccion, mensaje, expires, tiempo, autorizacion, digest, response) = linea_lista
                    self.dicc[direccion] = [ip, time.strftime('%Y-%m-%d %H:%M:%S', time.gmtime(time.time() + int(tiempo)))]
                    self.register2json()
            if linea_lista[0] == 'INVITE':
                with open(data_path, 'r') as fich:
                    lineas = fich.readlines()
                    Found = False
                    count = 0
                    for linea in lineas:
                        if not Found:
                            if linea.find(':') != -1:
                                if linea_lista[1].split(':')[1] == linea.split(':')[1]:
                                    puerto_2 = linea.split(':')[2].split('"')[0]
                                    ip = lineas[count+1].split('        ')[1].split('"')[1]
                                    Found = True
                                else:
                                    [puerto_2, ip] = [' ', ' ']
                            else:
                                pass
                            count = count + 1

                    LINE2 = 'INVITE' + ' ' + 'sip:' + linea_lista[1].split(':')[1] + ':' + puerto_2 + ' ' + 'SIP/2.0\r\n' + 'Content-Type: application/sdp' + '\r\n\r\n'
                    LINE2 += 'v=0' + '\r\n' + 'o=' + linea_lista[6].split('=')[1] + ' ' + ip + '\r\n' + 's=misesion' + '\r\n' + 't=0' + '\r\n' + 'm=audio' + ' ' + linea_lista[11] + ' ' + 'RTP'
                if puerto_2 != ' ' and ip != ' ':
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip, int(puerto_2)))
                    log(log_path2, 'Recived from ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                    log(log_path2, 'Sent to ' + ip + ':' + puerto_2 + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                    print("Enviando: " + 'INVITE')
                    my_socket.send(bytes(LINE2, 'utf-8') + b'\r\n\r\n')
                    data = my_socket.recv(1024)
                    datos = data.decode('utf-8')
                    datos_lista = datos.split('\r\n')
                    print('Recibido -- ', datos)
                    log(log_path2, 'Recived from ' + ip + ':' + (puerto_2) + ' ' + ' '.join(datos_lista) + '\r\n')
                    RCV = datos_lista[0:5]
                    if RCV == ['SIP/2.0 100 Trying', '', 'SIP/2.0 180 Ring', '', 'SIP/2.0 200 OK']:
                        log(log_path2, 'Sent to ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(datos_lista) + '\r\n')
                        mensaje = self.wfile.write(b'SIP/2.0 100 Trying' + b'\r\n\r\n' + b'SIP/2.0 180 Ring' + b'\r\n\r\n' + b'SIP/2.0 200 OK' + b'\r\n')
                        mensaje += self.wfile.write((bytes(datos_lista[5], 'utf-8')) + b'\r\n\r\n')
                        mensaje += self.wfile.write((bytes(datos_lista[7], 'utf-8')) + b'\r\n')
                        mensaje += self.wfile.write((bytes(datos_lista[8], 'utf-8')) + b'\r\n')
                        mensaje += self.wfile.write((bytes(datos_lista[9], 'utf-8')) + b'\r\n')
                        mensaje += self.wfile.write((bytes(linea_lista[10], 'utf-8')) + b'\r\n')
                        mensaje += self.wfile.write((bytes(linea_lista[11], 'utf-8')) + b'\r\n\r\n')
                else:
                    self.wfile.write(b'SIP/2.0 404 User not Found' + b'\r\n\r\n')

            if linea_lista[0] == 'ACK':
                with open(data_path, 'r') as fich:
                    lineas = fich.readlines()
                    Found = False
                    count = 0
                    for linea in lineas:
                        if not Found:
                            if linea.find(':') != -1:
                                if linea_lista[1].split(':')[1] == linea.split(':')[1]:
                                    puerto_2 = linea.split(':')[2].split('"')[0]
                                    ip = lineas[count+1].split('        ')[1].split('"')[1]
                                    Found = True
                                else:
                                    [puerto_2, ip] = [' ', ' ']
                            else:
                                pass
                            count = count + 1

                LINE3 = 'ACK ' + 'sip:' + linea_lista[1].split(':')[1] + ' ' + 'SIP/2.0' + '\r\n\r\n'
                if puerto_2 != ' ' and ip != ' ':
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip, int(puerto_2)))
                    log(log_path2, 'Recived from ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                    print("Enviando: " + 'ACK')
                    my_socket.send(bytes(LINE3, 'utf-8') + b'\r\n\r\n')
                    log(log_path2, 'Sent to ' + ip + ':' + puerto_2 + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
            if linea_lista[0] == 'BYE':
                with open(data_path, 'r') as fich:
                    lineas = fich.readlines()
                    Found = False
                    count = 0
                    for linea in lineas:
                        if not Found:
                            if linea.find(':') != -1:
                                if linea_lista[1].split(':')[1] == linea.split(':')[1]:
                                    puerto_2 = linea.split(':')[2].split('"')[0]
                                    ip = lineas[count+1].split('        ')[1].split('"')[1]
                                    Found = True
                                else:
                                    [puerto_2, ip] = [' ', ' ']
                            else:
                                pass
                            count = count + 1
                LINE4 = 'BYE ' + 'sip:' + linea_lista[1].split(':')[1] + ' ' + 'SIP/2.0' + '\r\n\r\n'
                if puerto_2 != ' ' and ip != ' ':
                    my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                    my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                    my_socket.connect((ip, int(puerto_2)))
                    log(log_path2, 'Recived from ' + ip_cliente + ':' + str(puerto_cliente) + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                    log(log_path2, 'Sent to ' + ip + ':' + puerto_2 + ' ' + ' '.join(linea.split('\r\n')) + '\r\n')
                    print("Enviando: " + 'BYE')
                    my_socket.send(bytes(LINE4, 'utf-8') + b'\r\n\r\n')
                    data = my_socket.recv(1024)
                    datos = data.decode('utf-8')
                    datos_lista = datos.split('\r\n')
                    print('Recibido -- ', datos)
                    log(log_path2, 'Recived from ' + ip + ':' + puerto_2 + ' ' + ' '.join(datos_lista) + '\r\n')
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
            with open(data_path, 'r') as data_base:
                self.dicc = json.loads(data_base)
        except:
            pass

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip_proxy2, int(puerto_proxy2)), EchoHandler)
    print("Listening...")
    serv.serve_forever()
