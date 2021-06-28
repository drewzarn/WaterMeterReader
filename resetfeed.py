import time, socket

message = str(time.time())+' 62162001 0\r\n'
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.connect(('172.24.84.122', 8080))
s.send(message.encode())