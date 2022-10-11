import socket
import threading


def stopper():
    send=input("")
    UDPClientSocket.sendto(str.encode(send), serverAddressPort)
    

if __name__ == '__main__':
        
    msgFromClient       = "subscribe"
    bytesToSend         = str.encode(msgFromClient)
    serverAddressPort   = ("127.0.0.1", 20003)
    bufferSize          = 1024

    # Create a UDP socket at client side

    UDPClientSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    # Send to server using created UDP socket
    UDPClientSocket.sendto(bytesToSend, serverAddressPort)

    th = threading.Thread(target=stopper, args=())
    th.start()

    while True:
        msgFromServer = UDPClientSocket.recvfrom(bufferSize)

        msg = msgFromServer[0].decode("UTF-8")

        print(msg)
        