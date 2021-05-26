'''
server.py
'''


import socket
import base64
import threading


SECRET_MSG = "Ostatnie sztuki w żabce przy Instytucie Informatyki"


def open_new_connection(port=0):
    sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sock.bind(('localhost', port))
    sock.listen(5)
    return sock
    
    
def send_msg_on_conection(sock):
    _client, _ = sock.accept()
    msg_to_send = SECRET_MSG
    _client.send((msg_to_send + '/r/n').encode('utf-8'))
    _client.close()
    sock.close()


def get_port_of_sock(sock):
    return sock.getsockname()[1]


def decode_msg(msg_buffor):
    received_msg = msg_buffor.decode('utf-8')
    received_msg = str(received_msg).split('/r/n', 1)
    return received_msg[0]


def create_socket_and_serve_msg():
    sock = open_new_connection()
    msg_to_send = str(get_port_of_sock(sock))
    threading.Thread(target=send_msg_on_conection, args=(sock, )).start()
    return msg_to_send


def on_new_client(client):
    while True:
        data_buffor = b''

        while b'/r/n' not in data_buffor:
            new_rec = client.recv(1024)
            if new_rec:
                data_buffor += new_rec

        received_msg = decode_msg(data_buffor)
        print ('Server receive: ' + received_msg)

        if received_msg == 'Velvet':
            msg_to_send = create_socket_and_serve_msg()
        else:
            msg_to_send = "Incorrect password"

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
