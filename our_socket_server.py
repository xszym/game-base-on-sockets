import socket
import os.path
import random 
import time
import uuid

def get_random_uuid_for_player():
    return str(uuid.uuid4())



def prepare_message(cm, st, data):
    comm = 'Command: '
    stat = 'Status: '
    leng = 'Lenght: '
    soft_end = '\r\n' 
    hard_end = '\r\n\r\n'

    mess = comm + cm + soft_end + stat + st + soft_end + leng + str(len(data)) + hard_end + data + hard_end
    return mess.encode('utf-8')



s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("localhost", 43226))
s.listen(5)

player_list = ['']

while True:
    client, addr = s.accept()
    print("Connected: " + addr[0])

    code = ''

    while code != 'QUIT GAME':

        data_rec = b''
        while b'\r\n\r\n' not in data_rec:
            data_rec = data_rec + client.recv(1)
        data_rec = data_rec.decode('utf-8')
        print("data_rec", data_rec)
        code2 = data_rec.split('\r\n\r\n')[0]
        print('I recive: ' + code2)

        data = data_rec
        x = data.split('Lenght:')
        print(x)
        print(x[1])
        x = x[1].split('\r\n\r\n')
        x = int(x[0])
    
        length = len(data.split('\r\n\r\n')[0]) + 4
        
        data2 = ''
        while len(data) < length + x:
            data = data + client.recv(1)

        code = data_rec
        split_code = code.split('Command:',1)
        code = split_code[1].split('\r\n',1)

        print(code)

        auth_code = data_rec
        split_auth_code = auth_code.split('Auth:',1)
        auth_code = split_auth_code[1].split('\r\n',1)

        print(auth_code)

        status = data_rec
        split_status = status.split('Auth:',1)
        status = split_status[1].split('\r\n',1)

        print(status)
            
        if code == 'JOIN GAME REQ':
            login = get_random_uuid_for_player()
            player_list.append(login)

            if auth_code == 'None':
                mess = prepare_message('REGISTER','SUCC',login)

            else:
                mess = prepare_message('REGISTER','ERR','')

            client.sendall(mess)

        else:
            mess = prepare_message('INVALID MESSAGE','ERR','') 
            client.sendall(mess)
        

            

