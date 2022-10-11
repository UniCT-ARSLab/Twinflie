from concurrent.futures import thread
from multiprocessing.connection import Listener
import time
from classes.uav.UAV_ciccio import UAV
from classes.uav.UAVEvents import UAVEvents
import threading

from cflib.crazyflie.mem.memory_element import MemoryElement
from flask import Flask
import socket

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
droni=[]

def testTakeLand(uav: UAV):
    print("partenza tra 2 sec")
    time.sleep(2)
    uav.take_off()
    print("mi sto muovendo")
    time.sleep(1)
    uav.go_to(uav.x,uav.y+0.5 )
    print("atterro")
    time.sleep(1)
    uav.land()
    print(uav.x, uav.y, uav.z)

def launchthread(uav: UAV):
    th = threading.Thread(target=testTakeLand, args=(uav,))
    th.start()

def connesso(uav:UAV):
    droni.append(uav)

app = Flask(__name__)

@app.route('/connect_to/url/<url>')
def url_connect(url):
    url=url.replace("_","/")
    print(url)
    #uavTest = UAV('radio://0/102/2M/E7E7E7E705')

    uavTest = UAV(url)

    uavTest.events.on(UAVEvents.CONNECTED,
                      lambda uri:
                      print("Drone Connected!", uri)
                      )
    uavTest.events.on(UAVEvents.CONNECTED, connesso)
    # uavTest.events.on(UAVEvents.CONTROLLER_READY,launchthread)

    uavTest.connect()
    return "tutto fatto"
    

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
        
        global droni
        lock_droni.acquire()
        pos={}
        
        if(len(droni)==0):
            msg_to_send="no drone connected"
        else:
            for x in range(len(droni)):
                pos_tupla=(droni[x].x,droni[x].y,droni[x].z)
                pos["drone_"+str(x)]=str(pos_tupla)
            msg_to_send=str(pos)
        
        lock_udp.acquire()
        for dest in udp_listener:
            UDPServerSocket.sendto(str.encode(msg_to_send), dest)
        lock_udp.release()
        lock_droni.release()
        time.sleep(0.2)
        
@app.route("/get_anchor_pos")
def anchor():
    
    lock_droni.acquire()
    json={}
    if len(droni)==0:
        lock_droni.release()
        json["status"]="no drone connected"
        return json
    
    test_loco(droni[0])
    
    lock_dati_2.acquire()
    global dati
    json["status"]="drone correctly connected"
    for x in range(len(dati)):
        json[str(x)]={"pos":str(dati[x])}

    lock_droni.release()
    
    lock_dati_1.release()
    return json

def test_loco(uav: UAV):
    mems_loco = uav.scf.cf.mem.get_mems(MemoryElement.TYPE_LOCO)
    if len(mems_loco) > 0:
        mems_loco[0].update(_anchor_position_signal)
    
    #lock_droni.release()

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
    
    for drone in droni:
        launchthread(drone)
    

    return "guarda i droni"



if __name__ == '__main__':
    th = threading.Thread(target=UDP_listener, args=())
    th.start()
    
    th2 = threading.Thread(target=UDP_sender, args=())
    th2.start()
app.run()
