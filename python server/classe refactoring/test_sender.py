import socket
import threading
import time
import math
import random
global udp_listener
from flask import Flask
udp_listener=[]

from pymitter import EventEmitter
from flask import request

from gevent.pywsgi import WSGIServer
from classes.point_list import Route

global droni
droni={}

global num
num=0


def move(percorso,route_obj,name):
    punto=percorso.pop()
    percorso.passed(route_obj)
    
    punto=percorso.pop()
    
    
    if punto[1]=="takeoff":
        print(name,":","decollo")
        time.sleep(2)
        percorso.passed(route_obj)
    else:
        print(name,":","errore posizione di decollo")
        return 0
    
    while True:
        punto=percorso.pop()
        
        if punto[1]=="landing":
            time.sleep(2)
            print(name,":","atteraggio")
            return
        elif(punto[1]=="base"):
            print(name,":","vado al punto:",punto[0][0],punto[0][2],punto[0][1])
            time.sleep(2)
        elif(punto[1]=="meeting"):
            print(name,":","vado al punto:",punto[0][0],punto[0][2],punto[0][1])
            print(punto[1])
            time.sleep(2)
        else:
            print(name,":","vado al punto:",punto[0][0],punto[0][2],punto[0][1])
            print(punto[1])
            time.sleep(2)
            
        
        percorso.passed(route_obj)


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
    
    while True:
        
        info={}
        global num
        global droni
        for url,drone in droni.items():
            pos_tupla=(random.uniform(1,-1),1,random.uniform(-1,0.1))
            
            
            info[url]["position"]=str(pos_tupla)
            info[url]["status"]="connected"
            info[url]["battery"]=100
        for dest in udp_listener:
            UDPServerSocket.sendto(str.encode(str(info)), dest)
            
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
        

@app.route("/route",methods = ['POST'])
def route():
    data=request.get_json()
    
    
    eventi=EventEmitter()
    
    uav={"100":"cose1","200":"cose"}
    
    test=Route(data["drone_0"],uav,"100",eventi)
    test2=Route(data["drone_1"],uav,"200",eventi)
    
    route_dict={"100":test,"200":test2}
    
    th = threading.Thread(target=move, args=(test,route_dict,"drone_0",))
    th.start()
        
    th1 = threading.Thread(target=move, args=(test2,route_dict,"drone_1",))
    th1.start()
    
    return "ok"

@app.route('/connect_to/url/<url>')
def url_connect(url):
    url=url.replace("_","/")
    print(url)
    #uavTest = UAV('radio://0/102/2M/E7E7E7E705')
    
    global droni
    
    global num
    num=num+1
    droni[url]=num
    
    return "tutto fatto"

if __name__ == '__main__':
    th = threading.Thread(target=UDP_listener, args=())
    th.start()
    
    th2 = threading.Thread(target=UDP_sender, args=())
    th2.start()
    

http=WSGIServer(("",5000),app)
http.serve_forever()
 
#app.run()