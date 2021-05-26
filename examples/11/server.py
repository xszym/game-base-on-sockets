'''
server.py

Zaprojektuj i zaimplementuj własny protokół uploadu plików tekstowych na zdalny serwer.
 Napisz program serwera, który działając pod adresem 127.0.0.1 oraz na określonym porcie TCP, 
 będzie komunikował się z klientem, odbierał od niego pliki, i zapisywał na dysku. 
 Napisz program klienta, który połączy się z przygotowanym serwerem, i wyśle do niego plik. 
 Zarówno klient, jak i serwer, powinni komunikować się przy pomocy zaprojektowanego protokołu. 
'''

import os 
import socket
from glob import glob
from pathlib import Path
import base64
import threading
import requests
import json


DIR = 'server_files/'


def get_files():
    res = [x.split('\\', 1)[1].replace("\\\\", '\\') for x in glob(DIR + '**', recursive=True) if x.split('\\', 1)[1] != '' and '.' in x]
    return res


def get_cat_picture():
    r = requests.get('https://aws.random.cat/meow')
    cat_api_result = json.loads(r.text)
    cat_pic_url = cat_api_result.get('file')
    cat_pic_response = requests.get(cat_pic_url)
    filename = cat_pic_url.split('/')[-1]
    if cat_pic_response.status_code == 200:
        return filename, cat_pic_response.content
    else:
        return None, None


def save_base64_file(filename, base64_msg):
    os.makedirs(os.path.dirname(DIR + filename), exist_ok=True)  
    with open(DIR + filename, "wb") as fh:
        fh.write(base64.decodebytes(base64_msg.encode('utf-8')))
    print(filename + " saved!")


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


def send_msg(client, msg, msg_code):
    # type 0 - OK, 1 - ERR
    msg_msg = "OK"
    if msg_code == 200:
        msg_msg = "OK"
    elif msg_code == 400:
        msg_msg = "ERR"
    client.send(f"{msg_msg} {msg_code}, {msg}/r/n/r/n".encode('utf-8'))


def on_new_client(client):
    while True:

        data_buffor = b''
        while b'/r/n/r/n' not in data_buffor:
            new_rec = client.recv(1)
            if new_rec:
                data_buffor += new_rec

        received_msg = decode_msg(data_buffor)
        print ('Server receive: ' + received_msg)
        received_msg = received_msg.split(",")
        if len(received_msg) < 1:
            send_msg(client, "Bad request", 1)

        if received_msg[0] == "SEND":
            if len(received_msg) < 3:
                send_msg(client, "Bad request", 1)
                break
            filename = received_msg[1]
            file_lenght = int(received_msg[2].split(":")[1])
            new_rec = client.recv(file_lenght).decode('utf-8')
            
            if file_lenght != len(new_rec):
                send_msg(client, "Received different amount of data", 400)
                break

            if filename in get_files():
                send_msg(client, "Filename already exists", 400)
                break

            try:
                save_base64_file(filename, new_rec)
                send_msg(client, "File saved", 200)
            except:
                send_msg(client, "Exception during file saving", 400)
                break
        elif received_msg[0] == "GET_IMAGE":
            filename, img_base_64 = get_cat_picture()
            if filename == None:
                send_msg(client, "Exception during getting img", 400)
                break
            send_msg(client, f"{filename},Lenght:{len(img_base_64)}/r/n/r/n", 200) # {img_base_64}
            client.send(img_base_64)
        else:
            send_msg(client, "Bad msg type", 400)

    client.close()


s = open_new_connection(1769)
while True:
    client, addr = s.accept()
    print("Connected: " + addr[0])
    threading.Thread(target=on_new_client, args=(client, )).start()

s.close()
