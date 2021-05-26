'''
server.py

W katalogu w ktorym uruchamiamy ten plik powinien znaleźć się katalog `server_files`. To te pliki będzie mógł pobrać klient.
'''


import socket
from glob import glob
from pathlib import Path
import base64
import threading


SERVER_DIR = 'server_files/'


def get_server_files():
    res = [x.split('\\', 1)[1].replace("\\\\", '\\') for x in glob(SERVER_DIR + '**', recursive=True) if x.split('\\', 1)[1] != '' and '.' in x]
    return res


def open_file_as_base64(filename):
    with open(SERVER_DIR + filename, "rb") as _file:
        return base64.b64encode(_file.read())


def open_new_connection(port=0):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(5)
    return sock
    
    
def send_file_on_conection(sock, filename):
    _client, _ = sock.accept()
    msg_to_send = open_file_as_base64(filename)
    _client.send((msg_to_send.decode('utf-8') + '/r/n').encode('utf-8'))
    _client.close()
    sock.close()


def get_port_of_sock(sock):
    return sock.getsockname()[1]


def decode_msg(msg_buffor):
    received_msg = msg_buffor.decode('utf-8')
    received_msg = str(received_msg).split('/r/n', 1)
    return received_msg[0]


def create_socket_and_serve_file(filename):
    sock = open_new_connection()
    msg_to_send = str(get_port_of_sock(sock))
    threading.Thread(target=send_file_on_conection, args=(sock, filename)).start()
    return msg_to_send


def on_new_client(client):
    while True:
        data_buffor = b''

        while b'/r/n' not in data_buffor:
            new_rec = client.recv(1)
            if new_rec:
                data_buffor += new_rec

        received_msg = decode_msg(data_buffor)
        print ('Server receive: ' + received_msg)

        file_list = get_server_files()

        if received_msg in file_list:
            msg_to_send = create_socket_and_serve_file(received_msg)
        else:
            msg_to_send = "Server files list: " + str(file_list)
        msg_to_send += '/r/n'
        client.send(msg_to_send.encode('utf-8') )
        print (msg_to_send)
    client.close()


s = open_new_connection(1769)
while True:
    client, addr = s.accept()
    print("Connected: " + addr[0])
    threading.Thread(target=on_new_client, args=(client, )).start()

s.close()
