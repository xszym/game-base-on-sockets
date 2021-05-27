import socket
import os.path
import random 
import time
import uuid


def get_random_uuid_for_player():
    print(str(uuid.uuid4()))
    return str(uuid.uuid4())



def prepare_message(command, status, data):
    command_code = 'Command: '
    status_code = 'Status: '
    lenght_code = 'Lenght: '
    soft_end = '\r\n' 
    hard_end = '\r\n\r\n'

    mess = command_code + command + soft_end + status_code + status + soft_end + lenght_code + str(len(data)) + hard_end + data + hard_end
    return mess.encode('utf-8')



s = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
s.bind(("localhost", 43229))
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

        data_rec_second_part = data_rec
        data_rec = data_rec.decode('utf-8')
        #print("data_rec", data_rec)
        code2 = data_rec.split('\r\n\r\n')[0]
        print('I recive: ' + code2)

        data = data_rec
        x = data.split('Lenght:')
        #print(x)
        print(x[1])
        x = x[1].split('\r\n\r\n')
        x = int(x[0])
    
        length = len(data.split('\r\n\r\n')[0]) + 4
        
        data2 = ''
        while len(data_rec_second_part) < length + x + 4:
            data_rec_second_part = data_rec_second_part + client.recv(1)

        code = data_rec
        split_code = code.split('Command: ',1)
        code = split_code[1].split('\r\n',1)[0]

        print('command: ' + code)

        auth_code = data_rec
        split_auth_code = auth_code.split('Auth: ')
        auth_code = split_auth_code[0].split('\r\n',1)[0]

        print('auth code: ' + auth_code)

        status = data_rec
        split_status = status.split('Status: ',1)
        status = split_status[1].split('\r\n',1)[0]

        print('status: ' + status)
            
        if code == 'JOIN GAME REQ':
            login = get_random_uuid_for_player()
            player_list.append(login)
            print('login ' + login)

            if auth_code == 'None':
                mess = prepare_message('REGISTER','SUCC',login)
                print('I send: ' + mess.decode('utf-8'))
            else:
                mess = prepare_message('REGISTER','ERR','')

            client.sendall(mess)
            print('I send: ' + mess.decode('utf-8'))

        else:
            mess = prepare_message('INVALID MESSAGE','ERR','') 
            client.sendall(mess)
            print('I send: ' + mess.decode('utf-8'))
            

s.close()