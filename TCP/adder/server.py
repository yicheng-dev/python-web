import socket
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.bind(('127.0.0.1', 8080))
sock.listen(1)
while True:
    print 'waiting for connecting...'
    connection,address = sock.accept()
    print '...connected from: %s:%i'%(address[0],address[1])
    while True:
        data = connection.recv(1024)
        if not data:
            break
        result = int(data[0]) + int(data[1])
        connection.send('%i + %i = %i'%(int(data[0]),int(data[1]),result))
    connection.close()
sock.close()
