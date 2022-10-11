import socket
import threading
import time
import math
import random
global udp_listener
from flask import Flask
udp_listener=[]

from gevent.pywsgi import WSGIServer


def UDP_listener():
    localIP     = "127.0.0.1"
    localPort   = 20003
    bufferSize  = 1024
    msgFromServer       = "Hello UDP Client"
    bytesToSend         = str.encode(msgFromServer)
    global udp_listener
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))

    print("UDP server up and listening")

    while(True):

        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        
        message = bytesAddressPair[0].decode('UTF-8')
        address = bytesAddressPair[1]
        print(message)
        if(message=="subscribe"):
            print(address)
            udp_listener.append(address)
            print("aggiunto:"+str(address))
            
        if(message=="stop"):
            print(address)
            udp_listener.remove(address)
            print("rimosso:"+str(address))
        
        
def UDP_sender():
    localIP     = "127.0.0.1"
    localPort   = 20004
    
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    i=0
    while True:
        
        pos={}
        for x in range(1):
            pos_tupla=(random.uniform(-0.1,-0.1),random.uniform(-1,0.1),1)
            pos["drone_"+str(x)]=str(pos_tupla)
        
        for dest in udp_listener:
            UDPServerSocket.sendto(str.encode(str(pos)), dest)
            
        i=i+1
        time.sleep(1)
        
        
  
app = Flask(__name__)

@app.route("/get_anchor_pos")
def anchor():
    json={}
    dati=[(2,2,0),(2,-2,0),(-2,2,0),(-2,-2,0),
          (2,2,2),(2,-2,2),(-2,2,2),(-2,-2,2)]
    json["status"]="drone correctly connected"
    for x in range(len(dati)):
        json[str(x)]={"pos":str(dati[x])}

    return json
        
        

@app.route('/connect_to/url/<url>')
def url_connect(url):
    url=url.replace("_","/")
    print(url)
    #uavTest = UAV('radio://0/102/2M/E7E7E7E705')

    return "tutto fatto"

if __name__ == '__main__':
    th = threading.Thread(target=UDP_listener, args=())
    th.start()
    
    th2 = threading.Thread(target=UDP_sender, args=())
    th2.start()
    

http=WSGIServer(("",5000),app)
http.serve_forever()
 
#app.run()