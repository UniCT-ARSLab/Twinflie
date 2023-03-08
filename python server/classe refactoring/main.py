import threading

from flask import Flask
import socket
from gevent.pywsgi import WSGIServer

from flask import request

from classes.drones_collection import drones_collection as Drone_collector

global udp_listener
udp_listener=[]

lock_udp=threading.Lock()
#drone collector contiene tutta la collezione di droni e gli oggetti che servono al loro movimento.
drones=Drone_collector()

app = Flask(__name__)
#permette la connessione di un drone di cui viene specificato l'url, il drone connesso verra inserito nella classe collector.
@app.route('/connect_to/url/<url>')
def url_connect(url):
    url=url.replace("_","/")
    
    drone=drones.add_drone(url)

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
        
        msg_to_send=drones.generate_json_all_drones_positions()
        
        lock_udp.acquire()
        for dest in udp_listener:
            UDPServerSocket.sendto(str.encode(msg_to_send), dest)
        lock_udp.release()
        
        
@app.route("/get_anchor_pos")
def anchor():
    return drones.get_anchor_pos()

     
@app.route("/falli_partire")
def falli_partire():
    
    drones.start_all_drones()

    return "guarda i droni"


@app.route("/route",methods = ['POST'])
def route():
    data=request.get_json()
    
    drones.add_route(data)

    return "ok"

@app.route("/set_anchor_pos",methods = ['POST'])
def set_anchor_pos():
    print("set ancore")
    data=request.get_json()
    response=drones.set_anchor_position(data)
    
    return str(response)

@app.route("/reset_estimation")
def reset_estimation():
    drones.reset_estimation_for_all_drone_connected()   
    return "ok"
    
if __name__ == '__main__':
    th = threading.Thread(target=UDP_listener, args=())
    th.start()
    
    
    th2 = threading.Thread(target=UDP_sender, args=())
    th2.start()
    
    
http=WSGIServer(("",5000),app)

http.serve_forever()
    
    