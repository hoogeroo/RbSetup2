import socket

TCP_IP = '130.216.50.91'
#TCP_IP='130.216.51.179'
TCP_PORT = 
BUFFER_SIZE = 50

class afg():
    def __init__(self,addr):
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.s.connect((TCP_IP, TCP_PORT))
        ml='INIT'
        #print(ml)
        self.s.send(ml.encode())
        #s.recv(5)
    def close():
        self.s.close()
    def setfreq(freq):
        ml='FREQ'+str(freq)
        self.s.send(ml.encode)
        #self.s.recv(5)


if __name__=='__main__':
    myafg=afg(TCPIP)
    myafg.setfreq(1000000.0)
    myafg.close()


