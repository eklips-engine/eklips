## Import components
import classes.singleton as engine
import socket            as sock
from classes.resources   import *
from classes.locals      import *

## Classes
class Packet:
    def __init__(self, data="", header=PACKET_BASIC):
        self.header = header
        self._data  = data
    
    def __repr__(self):
        return self.networking_form.decode()
    
    @property
    def networking_form(self):
        form = f"{self.size}{' '*(3-self.size)}{self.header}{self.data}"
        return form.encode()
    @property
    def size(self): return len(self._data)
    @property
    def data(self): return self._data
    @data.setter
    def data(self, value):
        self._data = value

class NetworkIdentity(Object):
    """Base class for Clients and Servers"""
    def __init__(self, properties={}):
        super().__init__(properties)

        self._limit = 513
        self.sock   = sock.socket(sock.AF_INET, sock.SOCK_STREAM)
        self.ip     = sock.gethostbyname(sock.gethostname())

        self.addr = INTERNET_ADDRESS
    
    def listen(self):
        self.sock.listen(self._limit)
    
    def connect(self, addr):
        self.sock.connect(addr)
    
    def bind(self):
        self.sock.bind(self.addr)
    
    def send(self, data : Packet):
        self.sock.send(data.networking_form)
    
    def recv(self):
        length = int(self.sock.recv(3).decode())
        header = self.sock.recv(2).decode()
        data   = self.sock.recv(length).decode()

        return Packet(data, header)

    def close(self):
        self.sock.close()

class Server(NetworkIdentity):
    """Server. It serves."""
    def __init__(self, properties={}):
        super().__init__(properties)
        self.bind()
        self.listen()
    
    @export(4, "int", "int")
    def limit(self):
        """Client limit."""
        return self._limit
    @limit.setter
    def limit(self, value):
        self._limit = value

        self.close()
        self.bind()
        self.listen()