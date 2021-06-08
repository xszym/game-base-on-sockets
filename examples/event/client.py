import sys
import socket
import threading

from ...config import MAIN_SERVER_SOCKET_PORT

def send_msg(sock, msg):
    """ Send a string over a socket, preparing it first """
    msg += '\0'
    data = msg.encode('utf-8')
    sock.sendall(data)


def parse_recvd_data(data):
  """ Break up raw received data into messages, delimited
    by null byte """
  parts = data.split(b'\0')
  msgs = parts[:-1]
  rest = parts[-1]
  return (msgs, rest)
  

def recv_msg(sock, data=bytes()):
    """ Receive data and break into complete messages on null byte
        delimiter. Block until at least one message received, then
        return received messages """

    msgs = []
    while not msgs:
        recvd = sock.recv(4096)
        if not recvd:
            raise ConnectionError()
        data = data + recvd
        (msgs, rest) = parse_recvd_data(data)
    msgs = [msg.decode('utf-8') for msg in msgs]
    return (msgs, rest)


def handle_input(sock):

    print("Type n to calculate Fibonacci, enter to send. 'q' to quit")
    while True:
        msg = input() # Blocks
        if msg == 'q':
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
            break
        try:
            send_msg(sock, msg) # Blocks until sent
        except (BrokenPipeError, ConnectionError):
            break


if __name__ == "__main__":
    addr = 'localhost'
    port = 1769

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((addr, port))
    print('Connected to {}:{}'.format(addr, port))

    # Create thread for handling user input and message sending
    thread = threading.Thread(target=handle_input, args=[sock], daemon=True)
    thread.start()
    
    rest = bytes()
    addr = sock.getsockname()
    # Loop indefinitely to receive messages from server
    while True:
        try:
            # blocks
            (msgs, rest) = recv_msg(sock, rest)
            for msg in msgs:
                print(msg)
        except ConnectionError:
            print('Connection to server closed')
            sock.close()
            break