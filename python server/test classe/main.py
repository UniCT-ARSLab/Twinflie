from concurrent.futures import thread
from multiprocessing.connection import Listener
import re
import time
from classes.uav.UAV_ciccio import UAV
from classes.uav.UAVEvents import UAVEvents
import threading

from cflib.crazyflie.mem.memory_element import MemoryElement
from flask import Flask
import socket

from gevent.pywsgi import WSGIServer

from flask import request

from classes.point_list import Route as Route_class
from pymitter import EventEmitter

global udp_listener
udp_listener=[]

lock_udp=threading.Lock()

lock_dati_1=threading.Lock()
lock_dati_2=threading.Lock()
lock_dati_2.acquire()

global dati
dati=[[],[],[],[],[],[],[],[]]

lock_droni=threading.Lock()
global droni
droni={}

global route_obj
route_obj={}

def movement(uav: UAV):
    print("mi muovo")
    time.sleep(1)
    global route_obj
    print(route_obj)
    
    percorso=route_obj[uav.uri]
    
    punto=percorso.pop()
    percorso.passed(route_obj)
    
    punto=percorso.pop()
    
    
    if punto[1]=="takeoff":
        print("decollo")
        uav.take_off(float(punto[0][1]))
        percorso.passed(route_obj)
    else:
        print("errore posizione di decollo")
        return 0
    
    while True:
        punto=percorso.pop()
        
        if punto[1]=="landing":
            uav.land()
            print("atteraggio")
            return
        elif(punto[1]=="base"):
            print("vado al punto:",punto[0][0],punto[0][2],punto[0][1])
            uav.go_to(float(punto[0][0]),float(punto[0][2]),float(punto[0][1]))
        elif(punto[1]=="meeting"):
            print(punto[1])
            print("vado al punto:",punto[0][0],punto[0][2],punto[0][1])
            uav.go_to(float(punto[0][0]),float(punto[0][2]),float(punto[0][1]))
        else:
            print(punto[1])
            print("vado al punto:",punto[0][0],punto[0][2],punto[0][1])
            uav.go_to(float(punto[0][0]),float(punto[0][2]),float(punto[0][1]))
            
        
        percorso.passed(route_obj)
    
    

def launchthread(uav: UAV):
    th = threading.Thread(target=movement, args=(uav,))
    th.start()

def connesso(uav:UAV):
    droni[uav.uri]=uav
    lock_droni.release()

def pronto_a_partire(uav:UAV):
    pass

app = Flask(__name__)

@app.route('/connect_to/url/<url>')
def url_connect(url):
    url=url.replace("_","/")
    #print(url)
    #uavTest = UAV('radio://0/102/2M/E7E7E7E705')
    
    global droni
    lock_droni.acquire()
    if url in droni:
        lock_droni.release()
        return "tutto fatto"      
    lock_droni.release()
    
    uavTest = UAV(url)

    uavTest.events.on(UAVEvents.CONNECTED,
                      lambda uri:
                      print("Drone Connected!", uri)
                      )
    lock_droni.acquire()
    uavTest.events.on(UAVEvents.CONNECTED, connesso)
    uavTest.events.on(UAVEvents.CONTROLLER_READY, pronto_a_partire)
    # uavTest.events.on(UAVEvents.CONTROLLER_READY,launchthread)

    uavTest.connect()
    return "tutto fatto"
    

def UDP_listener():
    localIP     = "127.0.0.1"
    localPort   = 20003
    bufferSize  = 1024
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
            lock_udp.acquire()
            udp_listener.append(address)
            lock_udp.release()
            print("aggiunto:"+str(address))
            
        if(message=="stop"):
            print(address)
            lock_udp.acquire()
            udp_listener.remove(address)
            lock_udp.release()
            print("rimosso:"+str(address))
        
        
def UDP_sender():
    localIP     = "127.0.0.1"
    localPort   = 20004
    
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
    UDPServerSocket.bind((localIP, localPort))
    
    while True:
        
        time.sleep(0.2)
        global droni
        lock_droni.acquire()
        pos={}
        
        if(len(droni)==0):
            msg_to_send="no drone connected"
        else:
            #i=0
            for key,uav in droni.items():
                pos_tupla=(uav.x,uav.y,uav.z)
                #pos["drone_"+str(i)]=str(pos_tupla)
                pos[key]=str(pos_tupla)
                #i=i+1
                
            msg_to_send=str(pos)
        
        lock_udp.acquire()
        for dest in udp_listener:
            UDPServerSocket.sendto(str.encode(msg_to_send), dest)
            
        #print(msg_to_send)
        lock_udp.release()
        lock_droni.release()
        
        
@app.route("/get_anchor_pos")
def anchor():
    
    lock_droni.acquire()
    json={}
    if len(droni)==0:
        lock_droni.release()
        json["status"]="no drone connected"
        return json
    
    test_loco(list(droni.values())[0])
    #lock_droni.release()
    
    #serve che qui il flusso si blocchi perche bisogno aspettare che i dati siano pronti nella "_anchor_position_signal" che sara un'evento asincrono,
    #quindi il flusso si blocca sul lock "lock_dati_2" che verra liberato solo alla fine di "_anchor_position_signal"
    lock_dati_2.acquire()
    
    #ora i dati saranno sicuramente pronti
    global dati
    json["status"]="drone correctly connected"
    for x in range(len(dati)):
        json[str(x)]={"pos":str(dati[x])}
        
    lock_dati_1.release()
    
    return json

def test_loco(uav: UAV):
    mems_loco = uav.scf.cf.mem.get_mems(MemoryElement.TYPE_LOCO)
    if len(mems_loco) > 0:
        mems_loco[0].update(_anchor_position_signal)
    
    lock_droni.release()

def _anchor_position_signal(mem):
    
    global dati
    lock_dati_1.acquire()
    for anchor_number, anchor_data in enumerate(mem.anchor_data):
        if anchor_data.is_valid:
            dati[anchor_number]=anchor_data.position
    lock_dati_2.release()

     
@app.route("/falli_partire")
def movimento():
    
    global droni
    
    for url,drone in droni.items():
        if drone.mc!=None:
            launchthread(drone)
        
        else:
            print("drone:",drone.uri,"not ready")
    return "guarda i droni"


@app.route("/route",methods = ['POST'])
def route():
    data=request.get_json()
    
    #i=0
    eventi=EventEmitter()
    
    for url,drone in droni.items():    
        #route_obj[drone.uri]=Route_class(data["drone_"+str(i)],droni,url,eventi)
        route_obj[drone.uri]=Route_class(data[url],droni,url,eventi)
        #i=i+1
    return "ok"

    
if __name__ == '__main__':
    th = threading.Thread(target=UDP_listener, args=())
    th.start()
    
    
    th2 = threading.Thread(target=UDP_sender, args=())
    th2.start()
    
    
http=WSGIServer(("",5000),app)

http.serve_forever()
    
    