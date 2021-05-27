import socket
import os.path
import random 
import time
from config import *
from utils import prepare_message, recv_msg_from_socket


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))

    code = ''
    mess = prepare_message(auth='None', command='REGISTER')
    s.sendall(mess)
    while True:
        headers, data = recv_msg_from_socket(s)
        # print("Recived", headers, data)

        mess = prepare_message(command='JOIN_CHANNEL',data='9Z1D')
        s.sendall(mess)

        headers, data = recv_msg_from_socket(s)
        game_server_port = data
        break


    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, int(game_server_port)))
    mess = prepare_message(command='UPDATE_GAME',data='XDD')
    # print('I send: ' + mess.decode('utf-8').strip())
    s.sendall(mess)

    while True:
        headers, data = recv_msg_from_socket(s)
        s.sendall(mess)

        # print("Recived", headers, data.strip())
        # print("PORT to join", int(data))
        # s.close()
        # s.connect((SERVER_IP, int(data)))

        # mess = prepare_message(command='QUIT GAME',status='SUCC')
        # print('I send: ' + mess.decode('utf-8').strip())
        # s.sendall(mess)
        # break

except socket.error:
    print ('Error')    