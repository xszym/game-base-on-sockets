# http://etutorials.org/Programming/Python+tutorial/Part+IV+Network+and+Web+Programming/Chapter+19.+Sockets+and+Server-Side+Network+Protocol+Modules/19.3+Event-Driven+Socket+Programs/


import socket
import select
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('', 8881))
sock.listen(5)

# lists of sockets to watch for input and output events
ins = [sock]
ous = []
# mapping socket -> data to send on that socket when feasible
data = {}
# mapping socket -> (host, port) on which the client is running
adrs = {}


def decode_msg(msg_buffor):
    received_msg = msg_buffor.decode('utf-8')
    received_msg = str(received_msg).split('/r/n', 1)
    return received_msg[0]

try:
    while True:
        i, o, e = select.select(ins, ous, [])  # no excepts nor timeout
        for x in i:
            if x is sock:
                # input event on sock means client trying to connect
                newSocket, address = sock.accept(  )
                print("Connected from", address)
                ins.append(newSocket)
                adrs[newSocket] = address
            else:
                # other input events mean data arrived, or disconnections
                newdata = x.recv(8192)

                # data_buffor = b''
                # while b'/r/n' not in data_buffor:
                #     data_buffor += s.recv(1)
                # received_msg = decode_msg(data_buffor)

                if newdata:
                    newdata = decode_msg(newdata)
                    # data arrived, prepare and queue the response to it
                    print("%d bytes from %s" % (len(newdata), adrs[x]))
                    data[x] = data.get(x, '') + newdata
                    if x not in ous: ous.append(x)
                else:
                    # a disconnect, give a message and clean up
                    print("disconnected from", adrs[x])
                    del adrs[x]
                    try: ous.remove(x)
                    except ValueError: pass
                    x.close(  )
        for x in o:
            # output events always mean we can send some data
            tosend = data.get(x)
            tosend += '/r/n'
            if tosend:
                nsent = x.send(tosend.encode("utf-8"))
                print("%d bytes to %s" % (nsent, adrs[x]))
                # remember data still to be sent, if any
                tosend = tosend[nsent:]
            if tosend: 
                print("%d bytes remain for %s" % (len(tosend), adrs[x]))
                data[x] = tosend
            else:
                try: del data[x]
                except KeyError: pass
                ous.remove(x)
                print("No data currently remain for", adrs[x])
finally:
    sock.close(  )
