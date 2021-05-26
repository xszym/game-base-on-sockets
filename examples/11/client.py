'''
client.py

Zaprojektuj i zaimplementuj własny protokół uploadu plików tekstowych na zdalny serwer.
 Napisz program serwera, który działając pod adresem 127.0.0.1 oraz na określonym porcie TCP, 
 będzie komunikował się z klientem, odbierał od niego pliki, i zapisywał na dysku. 
 Napisz program klienta, który połączy się z przygotowanym serwerem, i wyśle do niego plik. 
 Zarówno klient, jak i serwer, powinni komunikować się przy pomocy zaprojektowanego protokołu. 
'''

import socket
import threading
import base64
import os
from glob import glob


MAIN_DIR = 'client_files/'


def get_files():
    res = [x.split('\\', 1)[1].replace("\\\\", '\\') for x in glob(MAIN_DIR + '**', recursive=True) if x.split('\\', 1)[1] != '' and '.' in x]
    return res


def open_file_as_base64(filename):
    with open(MAIN_DIR + filename, "rb") as _file:
        return base64.b64encode(_file.read())


def decode_msg(msg_buffor):
    received_msg = msg_buffor.decode('utf-8')
    received_msg = str(received_msg).split('/r/n/r/n', 1)
    return received_msg[0]    


def send_msg(soc, msg):
    pass


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    
    s.connect(('localhost', 1769))
    file_list = get_files()
    file_to_send_name = ''
    while True:
        action = int(input("What action (0-for file sending, 1-for download img, 9-exit): "))
        if action == 0:
            while file_to_send_name not in file_list:
                file_to_send_name = input("Which file send? (" + ' '.join(file_list) + "): ")

            file_in_base64 = open_file_as_base64(file_to_send_name)
            headers = ["SEND", file_to_send_name, "LENGHT:" + str(len(file_in_base64))]
            headers = [x + "," for x in headers]
            headers = ''.join(headers)
            s.send((headers + '/r/n/r/n').encode('utf-8') + file_in_base64)

            data_buffor = b''
            while b'/r/n/r/n' not in data_buffor:
                data_buffor += s.recv(1)
            received_msg = decode_msg(data_buffor)

            received_msg = received_msg.split(",")
            if "OK" in received_msg[0]:
                print(received_msg[0], received_msg[1])
                break
            elif "ERR" in received_msg[0]:
                print(received_msg[0], received_msg[1], "try again!")
        elif action == 1:
            
            headers = ["GET_IMAGE"]
            headers = [x + "," for x in headers]
            headers = ''.join(headers)
            s.send((headers + '/r/n/r/n').encode('utf-8'))
            print(1)
            data_buffor = b''
            while b'/r/n/r/n' not in data_buffor:
                data_buffor += s.recv(1024)
            received_msg = decode_msg(data_buffor)
            received_msg = received_msg.split(",")
            print(received_msg)
            if "OK" in received_msg[0]:
                filename = received_msg[1]
                lenght = int(received_msg[2].split(":")[1])
                img = s.recv(lenght)

                if len(img) != lenght:
                    print("Wrong img size")
                    break

                with open(MAIN_DIR + filename, 'wb') as f:
                    f.write(img) 
                print("Image saved")
                break
            elif "ERR" in received_msg[0] :
                print(received_msg[0], received_msg[1], "try again!")
        
            print(received_msg)
        elif action == 9:
            break

    s.close()
except socket.error:
    print ('socket error')
