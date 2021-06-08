'''
server.py
'''
import socket
import asyncio
from concurrent.futures import ThreadPoolExecutor 


FIB = [0, 1, 1, 2]
clients = []


def recur_fibo(n):
   if n <= 1:
       return n
   else:
       return(recur_fibo(n-1) + recur_fibo(n-2))


def parse_recvd_data(data):
    """ Break up raw received data into messages, delimited
        by null byte """
    parts = data.split(b'\0')
    msgs = parts[:-1]
    rest = parts[-1]
    return (msgs, rest)


def prep_msg(msg):
    """ Prepare message """
    msg += '\0'
    return msg.encode('utf-8')


def calculate_and_response(transport, n):
    msg = str(recur_fibo(int(n)))


class FibServerProtocol(asyncio.Protocol):
    def connection_made(self, transport):
        """ Called on instantiation, when new client connects """
        self.transport = transport
        self.addr = transport.get_extra_info('peername')
        self._rest = b''
        self.name = None
        clients.append(self)
        print('Connection from {}'.format(self.addr))
    
    def data_received(self, data):
        """ Handle data as it's received. Broadcast complete
        messages to all other clients """
        data = self._rest + data
        (msgs, rest) = parse_recvd_data(data)
        self._rest = rest
        for msg in msgs:
            msg = msg.decode('utf-8')
            if msg.isdigit():
                n = int(msg)
                task = asyncio.create_task(self.async_fib(n))
            else:
                msg = "Input digit"
                msg = prep_msg(msg)
                self.transport.write(msg)
        
    def connection_lost(self, ex):
        """ Called on client disconnect. Clean up client state """
        print('Client {} disconnected'.format(self.addr))
        clients.remove(self)

    async def async_fib(self, n):
        task = await loop.run_in_executor(thread_pool, recur_fibo, n)
        response = str(task).encode()
        msg = f"fib({n})={response}"
        msg = prep_msg(msg)
        self.transport.write(msg)



thread_pool = ThreadPoolExecutor()


loop = asyncio.get_event_loop()
# Create server and initialize on the event loop
coroutine = loop.create_server(FibServerProtocol, host='0.0.0.0', port=1769)
server = loop.run_until_complete(coroutine)
# print listening socket info
for socket in server.sockets:
    addr = socket.getsockname()
    print('Listening on {}'.format(addr))
# Run the loop to process client connections
try:
    loop.run_forever()
except KeyboardInterrupt:
    pass

server.close()
# loop.wait_until(server)