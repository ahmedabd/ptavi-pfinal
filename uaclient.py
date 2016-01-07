#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys

try:
    CONFIG = sys.argv[1]
    METODO = sys.argv[2]
    OPCION = sys.argv[3]
except IndexError:
    sys.exit('Usage: python3 uaclient.py config method option')

with open(CONFIG, 'r') as file1:
    lineas = file1.readlines()
    usuario = lineas[1].split()[1].split('"')[1]
    passwd = lineas[1].split()[2].split('"')[1]
    ip_server = lineas[2].split()[1].split('"')[1]
    puerto_server = lineas[2].split()[2].split('"')[1]
    puerto_rtp = lineas[3].split()[1].split('"')[1]
    ip_proxy = lineas[4].split()[1].split('"')[1]
    puerto_proxy = lineas[4].split()[2].split('"')[1]
    log_path = lineas[5].split()[1].split('"')[1]
    audio_path = lineas[6].split()[1].split('"')[1]

# Contenido que vamos a enviar
LINE1 = METODO + ' ' + 'sip:' + usuario + ':' + puerto_proxy + ' ' + 'SIP/2.0\r\n'
AUTORIZACION = 'Authorization: response="123123"'
LINE2 = METODO + ' ' + 'sip:' + usuario + ':' + puerto_proxy + ' ' + 'SIP/2.0\r\n' + 'Content-Type: application/sdp' + '\r\n\r\n'
LINE2 += 'v=0' + '\r\n' + 'o=' + usuario + '\r\n' +  's=misesion' + '\r\n' +  't=0' + '\r\n' + 'm=audio' + ' ' + puerto_rtp + ' ' + 'RTP'
LINE3 = 'ACK ' + 'sip:' + usuario + ' ' + 'SIP/2.0' + '\r\n\r\n'
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((ip_proxy, int(puerto_proxy)))

if METODO == 'REGISTER':
    print("Enviando: " + METODO)
    my_socket.send((bytes(LINE1, 'utf-8') + bytes('Expires:' + ' ' + str(OPCION), 'utf-8') + b'\r\n\r\n'))
    data = my_socket.recv(1024)
    datos = data.decode('utf-8')
    datos_lista = datos.split('\r\n')
    RCV = datos_lista[0:2]
    print('Recibido -- ', datos)

    if RCV == ['SIP/2.1 401 Unauthorized', 'WWW Authenticate: nonce ="898989"']:
        print("Enviando: " + METODO)
        my_socket.send((bytes(LINE1, 'utf-8') + bytes('Expires:' + ' ' + str(OPCION), 'utf-8') + b'\r\n' + bytes(AUTORIZACION, 'utf-8') + b'\r\n\r\n'))
        data = my_socket.recv(1024)
        datos = data.decode('utf-8')
        print('Recibido -- ', datos)

if METODO == 'INVITE':
    print("Enviando: " + METODO)
    my_socket.send(bytes(LINE2, 'utf-8') + b'\r\n\r\n')
    data = my_socket.recv(1024)
    datos = data.decode('utf-8')
    datos_lista = datos.split('\r\n')
    print('Recibido -- ', datos)
    RCV = datos_lista[0:12]

    if RCV == ['SIP/2.0 100 Trying', '', 'SIP/2.0 180 Ring', '', 'SIP/2.0 200 OK', 'Content-Type:application/sdp', '', 'v=0', 'o=ahmed@gmail.es', 's=misesion', 't=0', 'm=audio 7000 RTP']:
        print("Enviando: " + 'ACK')
        my_socket.send(bytes(LINE3, 'utf-8'))
        data = my_socket.recv(1024)
        datos = data.decode('utf-8')
        datos_lista = datos.split('\r\n')
        print('Recibido -- ', datos)

print("Terminando socket...")

# Cerramos todo
my_socket.close()
print("Fin.")
