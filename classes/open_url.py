import os
import socket

s = socket.socket()
host = socket.gethostname()
port = 5000
s.bind((host, port))
print("Server started at: ", host)
s.listen(1)
conn,addr = s.accept()
print(addr, "connected")