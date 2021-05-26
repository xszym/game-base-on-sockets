'''
client.py
'''

import socket
import threading
import base64
import os


def decode_msg(msg_buffor):
    received_msg = msg_buffor.decode('utf-8')
    received_msg = str(received_msg).split('/r/n', 1)
    return received_msg[0]    


def get_msg_from_port(port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port))

    data_buffor = b''
    while b'/r/n' not in data_buffor:
        data_buffor += s.recv(1024)
    
    received_msg = decode_msg(data_buffor) 
    print("Secret msg is: " + received_msg)


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('localhost', 1769))
   
    while True:
        data = input("Input password: ")
        s.send((data + '/r/n').encode('utf-8'))

        data_buffor = b''
        while b'/r/n' not in data_buffor:
            data_buffor += s.recv(1)
        
        received_msg = decode_msg(data_buffor)
        if received_msg.isdigit():
            get_msg_from_port(int(received_msg))
        else:
            print(received_msg)

    s.close()
except socket.error:
    print ('Error')
