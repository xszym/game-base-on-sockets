'''
client.py

Po podłączeniu do serwera i dowolnej wiadomości otrzmymamy listę dostępnych plików do pobrania.
Po wysłaniu poprawnej nazwy pliku, która znajduje się na serwerze, pobierze on się do folderu 'client_files'.
'''

import socket
import threading
import base64
import os


CLIENT_DIR = 'client_files/'


def download_file_from_port(filename, port):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.connect(('localhost', port))

    print("Downloading file " + filename)
    data_buffor = b''
    while b'/r/n' not in data_buffor:
        data_buffor += s.recv(1)
    received_msg = (str(data_buffor.decode('utf-8'))).split('/r/n', 1)[0]  
    os.makedirs(os.path.dirname(CLIENT_DIR + filename), exist_ok=True)  
    with open(CLIENT_DIR + filename, "wb") as fh:
        fh.write(base64.decodebytes(received_msg.encode('utf-8')))
    print(filename + " downloaded!")


def decode_msg(msg_buffor):
    received_msg = msg_buffor.decode('utf-8')
    received_msg = str(received_msg).split('/r/n', 1)
    return received_msg[0]    


s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('localhost', 1769))
   
    while True:
        data = input("Input file to download: ")
        s.send((data + '/r/n').encode('utf-8'))

        data_buffor = b''
        while b'/r/n' not in data_buffor:
            data_buffor += s.recv(1)
        
        received_msg = decode_msg(data_buffor)
        if received_msg.isdigit():
            threading.Thread(target=download_file_from_port, args=(data, int(received_msg))).start()
        else:
            print(received_msg)

    s.close()
except socket.error:
    print ('Error')
