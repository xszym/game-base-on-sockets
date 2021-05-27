import socket
import os.path
import random 
import time
from config import *
from utils import prepare_message, recv_msg_from_socket
from time import sleep
from Crypto.Cipher import AES
from Crypto.PublicKey import RSA
from Crypto import Random


def do_encrypt(message):
    obj = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    ciphertext = obj.encrypt(message)
    return ciphertext

def do_decrypt(ciphertext):
    obj2 = AES.new('This is a key123', AES.MODE_CBC, 'This is an IV456')
    message = obj2.decrypt(ciphertext)
    return message

try:
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))

    mess = prepare_message(command='REGISTER')
    s.sendall(do_encrypt(mess))
    headers, data = recv_msg_from_socket(s)

    mess = prepare_message(command='START_CHANNEL',auth='')
    s.sendall(do_encrypt(mess))
    headers, data = recv_msg_from_socket(s)

    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((SERVER_IP, MAIN_SERVER_SOCKET_PORT))

    # mess = prepare_message(command='JOIN_CHANNEL',data=data)
    # s.sendall(mess)
    # headers, data = recv_msg_from_socket(s)

    # port = data
    # s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # s.connect((SERVER_IP, int(port)))

    # mess = prepare_message(command='START_GAME',data=data)
    # s.sendall(mess)
    # headers, data = recv_msg_from_socket(s)

    # while True:
    #     headers, data = recv_msg_from_socket(s)
    #     s.sendall(mess)

except socket.error:
    print ('Error')    