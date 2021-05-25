while True:
    client, addr = s.accept()
    print("Connected: " + addr[0])

    data = ''
    code = ''
    size_of_file = 0
    file_content = b''
    boat_number = 10
    life = boat_number
    score = 0
    pos_list = [(10,10)]
    boat_list = [(10,10)]
    winner = ''

    while code != 'WINNER: SERVER':

        
        data_rec = b''
        while b'\r\n\r\n' not in data_rec:
            data_rec = data_rec + client.recv(1)

        data_rec = data_rec.decode('utf-8')
        code = data_rec.split('\r\n\r\n')[0]
        print('I recive: ' + code)

        if life <= 0:
            data = b'WINNER: CLIENT'
            winner = 'Client'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))
            time.sleep(1)
            data = b'END GAME'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))

            for i in range(0,10):
                print(battleField[i])
        
        

        elif code == 'JOIN GAME REQUEST':
            data = b'REQUEST ACCEPTED'
            for i in range(0,boat_number):
                x = random.randint(0,9)
                y = random.randint(0,9)
                  flag1 = True

                while flag1:
                    flag2 = False
                    for i in boat_list:
                        if i == (x,y):
                            flag2 = True
                
                    if flag2:
                        x = random.randint(0,9)
                        y = random.randint(0,9)
                    else:
                        flag1 = False

                boat_list.append((x,y))
            
                battleField[x][y] = 'o'
            for i in range(0,10):
                print(battleField[i])
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))
            time.sleep(1)

            data = b'YOUR TURN'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))

        elif code == 'SENDING POS':
            
            pos = b''
            while b'\r\n\r\n' not in pos:
                pos = pos + client.recv(1)
                
            pos = pos.decode('utf-8')
            pos = pos.split(' : ')
            x = int(pos[0])
            y = pos[1]
            y = int(y[:-4])
            pos = int(size_of_file)
            print('POSITION : ' + str(x) + ' ' + str(y))

            if x >= 10:
                data = b'INVALID POSITION'
                client.sendall(data + b'\r\n\r\n')
                print('I send: ' + data.decode('utf-8'))

            elif y >= 10:
                data = b'INVALID POSITION'
                client.sendall(data + b'\r\n\r\n')
                print('I send: ' + data.decode('utf-8')) 

            elif battleField[x][y] == '-':
                data = b'FAIL: EMPTY FIELD'
                battleField[x][y] = 'x'
                client.sendall(data + b'\r\n\r\n')
                print('I send: ' + data.decode('utf-8'))

            elif battleField[x][y] == 'x':
                data = b'FAIL: FIELD WAS SHOOT ALREADY'
                client.sendall(data + b'\r\n\r\n')
                print('I send: ' + data.decode('utf-8'))

            elif battleField[x][y] == 'o':
                data = b'SUCCESS: BOAT DESTROYED'
                battleField[x][y] = 'x'
                life = life - 1
                client.sendall(data + b'\r\n\r\n')
                print('I send: ' + data.decode('utf-8'))
            
            

        elif code == 'SUCCESS: BOAT DESTROYED':
            score = score + 1
            data = b'YOUR TURN'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))
        
        elif code == 'FAIL: FIELD WAS SHOOT ALREADY':
            data = b'YOUR TURN'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))

        elif code == 'FAIL: EMPTY FIELD':
            data = b'YOUR TURN'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))
        
        elif code == 'INVALID POSITION':
            data = b'YOUR TURN'
            client.sendall(data + b'\r\n\r\n')
            print('I send: ' + data.decode('utf-8'))

        elif code == 'YOUR TURN':
            x = random.randint(0,9)
            y = random.randint(0,9)


import uuid

def get_random_uuid_for_player():
    return str(uuid.uuid4())
    'f50ec0b7-f960-400d-91f0-c42a6d44e3d0'

def niegroew_zapytania(zapytnie):
    komenda = ''
    if komenda == 'REG':
        return get_random_uuid_for_player()
    elif komenda == 'START_NEW_GAME':
        join_key = start_new_game()
        return join_key

def growe_zpaytania():
