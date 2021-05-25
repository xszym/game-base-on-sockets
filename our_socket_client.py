import socket
import os.path
import random 
import time


def prepare_message(at, cm, st, data):
    auth = 'Auth:'
    comm = 'Command:'
    stat = 'Status:'
    leng = 'Lenght:'
    soft_end = '\r\n' 
    hard_end = '\r\n\r\n'

    mess = auth + at + soft_end + comm + cm + soft_end + stat + st + soft_end + leng + str(len(data)) + hard_end + data + hard_end
    return mess.encode('utf-8')



s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
try:
    s.connect(('localhost', 43226))

    code = ''
    mess = prepare_message('None','JOIN GAME REQ','SUCC','')
    s.sendall(mess)
    while code != 'END GAME':

        data_rec = b''
        while b'\r\n\r\n' not in data_rec:
            data_rec = data_rec + s.recv(1)

        data_rec = data_rec.decode('utf-8')
        code2 = data_rec.split('\r\n\r\n')[0]
        print('I recive: ' + code2)

        data = data_rec
        x = data.split('Lenght:')
        x = x[1].split('\r\n\r\n')
        x = int(x[0])
    
        length = len(data.split('\r\n\r\n')[0]) + 4
        
        while len(data) < length + x:
            data = data + s.recv(1)

        code = data_rec
        split_code = code.split('Command:',1)
        code = split_code[1].split('\r\n',1)

        print(code)

        auth_code = data_rec
        split_auth_code = auth_code.split('Auth:',1)
        auth_code = split_auth_code[1].split('\r\n',1)

        print(auth_code)

        status = data_rec
        split_status = status.split('Status:',1)
        status = split_status[1].split('\r\n',1)

        print(status)
        
        if code == 'REGISTER':
            login = auth_code

            
            mess = prepare_message(login,'QUIT','SUCC','')
            s.sendall(mess)
except socket.error:
    print ('Error')    