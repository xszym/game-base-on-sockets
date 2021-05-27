import asyncore

class EchoHandler(asyncore.dispatcher):
    def __init__(self, conn_sock, client_address, server):
        self.server             = server
        self.client_address     = client_address
        self.buffer             = ""
 
        # We dont have anything to write, to start with
        self.is_writable        = False
 
        # Create ourselves, but with an already provided socket
        asyncore.dispatcher.__init__(self, conn_sock)
        log.debug("created handler; waiting for loop")
        
    def handle_read(self):
        data = self.recv(8192)
        if data:
            self.send(data)

    def handle_read(self):
        log.debug("handle_read")
        data = self.recv(SIZE)
        log.debug("after recv")
        if data:
            log.debug("got data")
            self.buffer += data
            self.is_writable = True  # sth to send back now
        else:
            log.debug("got null data")
 
    def handle_write(self):
        log.debug("handle_write")
        if self.buffer:
            sent = self.send(self.buffer)
            log.debug("sent data")
            self.buffer = self.buffer[sent:]
        else:
            log.debug("nothing to send")
        if len(self.buffer) == 0:
            self.is_writable = False
 
    # Will this ever get called?  Does loop() call
    # handle_close() if we called close, to start with?
    def handle_close(self):
        log.debug("handle_close")
        log.info("conn_closed: client_address=%s:%s" % \
                     (self.client_address[0],
                      self.client_address[1]))
        self.close()
        #pass

class EchoServer(asyncore.dispatcher):

    def __init__(self, host, port):
        asyncore.dispatcher.__init__(self)
        self.create_socket()
        self.set_reuse_addr()
        self.bind((host, port))
        self.listen(5)

    def handle_accepted(self, sock, addr):
        print('Incoming connection from %s' % repr(addr))
        handler = EchoHandler(sock)

server = EchoServer('localhost', 8881)
asyncore.loop()
