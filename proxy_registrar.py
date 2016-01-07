#!/usr/bin/python
# -*- coding: utf-8 -*-

import socketserver
import sys
import os
import socket

CONFIG = sys.argv[1]

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

LINE2 = 'INVITE' + ' ' + 'sip:' + usuario + ':' + puerto_proxy + ' ' + 'SIP/2.0\r\n' + 'Content-Type: application/sdp' + '\r\n\r\n'
LINE2 += 'v=0' + '\r\n' + 'o=' + usuario + '\r\n' +  's=misesion' + '\r\n' +  't=0' + '\r\n' + 'm=audio' + ' ' + puerto_rtp + ' ' + 'RTP' 


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
            if linea_lista[0] == 'INVITE':
                my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
                my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                my_socket.connect((ip_server3, int(puerto_server3)))
                print("Enviando: " + 'INVITE')
                my_socket.send(bytes(LINE2, 'utf-8') + b'\r\n\r\n')
                data = my_socket.recv(1024)
                datos = data.decode('utf-8')
                datos_lista = datos.split('\r\n')
                print('Recibido -- ', datos)
                RCV = datos_lista[0:12]
                print(datos_lista)

                if RCV == ['SIP/2.0 100 Trying', '', 'SIP/2.0 180 Ring', '', 'SIP/2.0 200 OK', 'Content-Type:application/sdp', '', 'v=0', 'o=ahmed@gmail.es', 's=misesion', 't=0', 'm=audio 7000 RTP']:
                    mensaje = self.wfile.write(b'SIP/2.0 100 Trying' + b'\r\n\r\n' + b'SIP/2.0 180 Ring' + b'\r\n\r\n' + b'SIP/2.0 200 OK' + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[3] + linea_lista[4], 'utf-8')) + b'\r\n\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[5], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[6], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[7], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[8], 'utf-8')) + b'\r\n')
                    mensaje += self.wfile.write((bytes(linea_lista[9] + ' ' + linea_lista[10] + ' ' + linea_lista[11], 'utf-8')) + b'\r\n\r\n')

                    
                    

                

if __name__ == "__main__":
    # Creamos servidor de eco y escuchamos
    serv = socketserver.UDPServer((ip_proxy2, int(puerto_proxy2)), EchoHandler)
    print("Listening...")
    serv.serve_forever()