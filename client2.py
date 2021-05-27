import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect(('localhost', 5667))
print ("Connected to server")
data = """A few lines of data
to test the operation
of both server and client."""
for line in data.splitlines(  ):
    sock.sendall((line+'\n').encode('utf-8'))
    print ("Sent:", line)
    response = sock.recv(8192)
    print ("Received:", response)
sock.close(  )