#!/usr/bin/python
# -*- coding: utf-8 -*-

import socket
import sys
import os
import time
import hashlib


def log(File, Mensaje):
    with open(File, 'r') as fich:
        lineas = fich.readlines()

    lineas.append(str(time.time()) + ' ' + Mensaje)
    with open(File, 'w') as fich:
        fich.write(''.join(lineas))


try:
    CONFIG = sys.argv[1]
    METODO = sys.argv[2]
    OPCION = sys.argv[3]
    FICH_AUDIO = 'cancion.mp3'
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

    dicc = {}

# Contenido que vamos a enviar
LINE1 = METODO + ' ' + 'sip:' + usuario + ':' + puerto_server
LINE1 += ' ' + 'SIP/2.0\r\n'
AUTORIZACION = 'Authorization: response="123123"'
LINE2 = METODO + ' ' + 'sip:' + OPCION
LINE2 += ' ' + 'SIP/2.0\r\n' + 'Content-Type: application/sdp' + '\r\n\r\n'
LINE2 += 'v=0' + '\r\n' + 'o=' + usuario + ' ' + ip_server + '\r\n'
LINE2 += 's=misesion' + '\r\n' + 't=0' + '\r\n'
LINE2 += 'm=audio' + ' ' + puerto_rtp + ' ' + 'RTP'
LINE3 = 'ACK ' + 'sip:' + OPCION + ' ' + 'SIP/2.0' + '\r\n\r\n'
LINE4 = 'BYE ' + 'sip:' + OPCION + ' ' + 'SIP/2.0' + '\r\n\r\n'
# Creamos el socket, lo configuramos y lo atamos a un servidor/puerto
my_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
my_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
my_socket.connect((ip_proxy, int(puerto_proxy)))


if METODO == 'REGISTER':
    log(log_path, 'Starting ... \r\n')
    log(log_path, 'Sent to ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(LINE1.split('\r\n')) + '\r\n')
    print("Enviando: " + METODO)
    my_socket.send((bytes(LINE1, 'utf-8') + bytes('Expires:' + ' ' + str(OPCION), 'utf-8') + b'\r\n\r\n'))
    data = my_socket.recv(1024)
    datos = data.decode('utf-8')
    datos_lista = datos.split('\r\n')
    RCV = datos_lista[0:1]
    print('Recibido -- ', datos)

    if RCV == ['SIP/2.1 401 Unauthorized']:
        print("Enviando: " + METODO)
        nonce = datos_lista[1].split('=')[1].split()[0]
        m = hashlib.md5()
        m.update(bytes(passwd + nonce, 'utf-8'))
        response = m.hexdigest()
        my_socket.send((bytes(LINE1, 'utf-8') + bytes('Expires:' + ' ' + str(OPCION), 'utf-8') + b'\r\nAuthorization: Digest response=' + bytes(response, 'utf-8') + b'\r\n\r\n'))
        data = my_socket.recv(1024)
        datos = data.decode('utf-8')
        datos_lista = datos.split('\r\n')
        print('Recibido -- ', datos)
        log(log_path, 'Recived from ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(datos_lista[0].split('\r\n')) + '\r\n')

if METODO == 'INVITE':
    log(log_path, 'Sent to ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(LINE2.split('\r\n')) + '\r\n')
    print("Enviando: " + METODO)
    my_socket.send(bytes(LINE2, 'utf-8') + b'\r\n\r\n')
    data = my_socket.recv(1024)
    datos = data.decode('utf-8')
    datos_lista = datos.split('\r\n')
    log(log_path, 'Recived from ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(datos_lista) + '\r\n')
    print('Recibido -- ', datos)
    RCV = datos_lista[0:5]

    if datos_lista[0:1] == ['SIP/2.0 404 User not Found']:
        log(log_path, 'Recived from' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(datos_lista) + '\r\n')

    if RCV == ['SIP/2.0 100 Trying', '', 'SIP/2.0 180 Ring', '', 'SIP/2.0 200 OK']:
        dicc[datos_lista[8].split()[0]] = [datos_lista[11], datos_lista[8].split()[1]]
        log(log_path, 'Sent to ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(LINE3.split('\r\n')) + '\r\n')
        print("Enviando: " + 'ACK')
        my_socket.send(bytes(LINE3, 'utf-8'))
        data = my_socket.recv(1024)
        datos = data.decode('utf-8')
        datos_lista = datos.split('\r\n')
        print('Recibido -- ', datos)
        [puerto_receptor, ip_receptor] = dicc[LINE2.split()[1].split(':')[1]]
        aEjecutar = './mp32rtp -i ' + ip_receptor + ' ' '-p ' + str(puerto_receptor) + ' ' + '< ' + FICH_AUDIO
        print('Vamos a ejecutar', aEjecutar)
        os.system(aEjecutar)


if METODO == 'BYE':
    log(log_path, 'Sent to ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(LINE4.split('\r\n')) + '\r\n')
    print("Enviando: " + METODO)
    my_socket.send(bytes(LINE4, 'utf-8'))
    data = my_socket.recv(1024)
    datos = data.decode('utf-8')
    datos_lista = datos.split('\r\n')
    log(log_path, 'Recived from ' + ip_proxy + ':' + puerto_proxy + ' ' + ' '.join(datos_lista) + '\r\n')
    print('Recibido -- ', datos)
print("Terminando socket...")
# Cerramos todo
my_socket.close()
print("Fin.")
