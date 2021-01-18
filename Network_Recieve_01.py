import socket

hostMACAddress = 'E4:B3:18:95:C3:2D'
port = 3
backlog = 1
size = 1024
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind((hostMACAddress,port))
s.listen(backlog)
try:
    client, address = s.accept()
    while 1:
        data = client.recv(size)
        if data:
            print(data)
            client.send(data)
except:	
    print("Closing socket")	
    client.close()
    s.close()