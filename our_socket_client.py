import socket
import os.path
import random 
import time
from config import *
from utils import prepare_message, recv_msg_from_socket
from time import sleep


try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))

    mess = prepare_message(command='REGISTER')
    s.sendall(mess)
    headers, data = recv_msg_from_socket(s)

    mess = prepare_message(command='START_CHANNEL',auth='')
    s.sendall(mess)
    headers, data = recv_msg_from_socket(s)

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))

    mess = prepare_message(command='JOIN_CHANNEL',data=data)
    s.sendall(mess)
    headers, data = recv_msg_from_socket(s)

    port = data
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, int(port)))

    mess = prepare_message(command='START_GAME',data=data)
    s.sendall(mess)
    headers, data = recv_msg_from_socket(s)

    while True:
        headers, data = recv_msg_from_socket(s)
        s.sendall(mess)

except socket.error:
    print ('Error')    