import threading
import time

from classes.uav.UAVEvents import UAVEvents
from classes.uav.UAV_ciccio import UAV

from cflib.crazyflie.mem.memory_element import MemoryElement

from classes.point_list import Route as Route_class
from pymitter import EventEmitter

from lpslib.lopoanchor import LoPoAnchor

class drones_collection():

    #la classe fa uso di diversi lock per evitare race condition sulle strutture dati condivise
    lock_drones=threading.Lock()
    
    #drones è un dizionario che conterra le informazioni sui droni nella forma "url": ogetto uav
    drones={}

    #anchor sarà un json che conterrà le posizione sulle ancore 
    anchor_pos={}
    
    #rout collection conterra tutte le route per tutti i droni connessi
    route_collection={}
    lock_route=threading.Lock()
    
    #i seguenti due lock servono per scrivere in maniera appropiata le informazione sulle ancore
    lock_anchor_writing_data=threading.Lock()
    lock_anchor_data_are_ready=threading.Lock()

    lock_anchor_data_are_ready.acquire()

    #callback per la connessione
    def _connesso(self,uav:UAV):
        self.drones[uav.uri]=uav
        uav.events.on(UAVEvents.DISCONNECTED, self.remove_drone_thread)
        uav.events.on(UAVEvents.CONNECTION_LOST, self.remove_drone_thread)
        self.lock_drones.release()

    def remove_drone_thread(self,uav):
        th = threading.Thread(target=self.remove_drone, args=([uav]))
        th.start()
        #time.sleep(10)
        #th._stop()
        

    #callback per segnalare che io motori sono pronti
    def _pronto_a_partire(self, uav:UAV):
        pass
    def failed(self,uav,dummy):

        self.lock_drones.release()

    #procedura che aggiunge un drone alla collezzione dei droni connessi se esso non è connesso e ritorna il drone appena connesso.
    def add_drone(self,url):
        
        self.lock_drones.acquire()
        if url in self.drones:
            self.lock_drones.release()
            return self.drones[url]    
        self.lock_drones.release()
    
        uavTest = UAV(url)

        uavTest.events.on(UAVEvents.CONNECTED,
                      lambda uri:
                      print("Drone Connected!", uri)
                      )
        self.lock_drones.acquire()
        uavTest.events.on(UAVEvents.CONNECTED, self._connesso)
        uavTest.events.on(UAVEvents.CONTROLLER_READY, self._pronto_a_partire)
        uavTest.events.on(UAVEvents.CONNECTION_FAILED, self.failed)
        uavTest.connect()

        while not uavTest.connected:
            time.sleep(0.1)


        if url in self.drones:
            print("tutto ok")
            return "tutto ok"
        else:
            return "connection to "+ url + " failed"

    def remove_drone(self,uav):
        print("1")
        time.sleep(3)
        print("2")
        self.lock_drones.acquire()
        self.drones.pop(uav.uri, None)
        self.lock_drones.release()
        print("3")

    #la funzione genera un json con tutte le posizioni attualmente connessi
    def generate_json_all_drones_positions(self):
        self.lock_drones.acquire()
        info={}
        
        if(len(self.drones)==0):
            all_drones_pos="no drone connected"
        else:
            for key,uav in self.drones.items():
                
                info[key]={}
                pos_tupla=(uav.x,uav.y,uav.z)
                info[key]["position"]=str(pos_tupla)
                info[key]["status"]=uav.status
                info[key]["battery"]=uav.battery

                if uav.status=="disconnected":
                    print("disconnected")

            all_drones_pos=str(info)
        self.lock_drones.release()
        return all_drones_pos
    

    #funzione per predere le posizione delle ancore, fa uso di due call back 
    def get_anchor_pos(self):
        self.lock_drones.acquire()
        json={}
        if len(self.drones)==0:
            self.lock_drones.release()
            json["status"]="no drone connected"
            return json
    
        self._get_loco_positions(list(self.drones.values())[0])
   
        #serve che qui il flusso si blocchi perche bisogno aspettare che i dati siano pronti nella "_anchor_position_signal" 
        #che sara un'evento asincrono,
        #quindi il flusso si blocca sul lock "lock_dati_2" che verra liberato solo alla fine di "_anchor_position_signal"
        self.lock_anchor_data_are_ready.acquire()
    
        #ora i dati saranno sicuramente pronti

        json["status"]="drone correctly connected"
        for x in range(len(self.anchor_pos)):
            json[str(x)]={"pos":str(self.anchor_pos[x])}
            
        self.lock_anchor_writing_data.release()
        
        return json

    #la prima callback effettua la richiesta a un drone collegato e sblocca il lock sui droni  
    def _get_loco_positions(self,uav: UAV):
        mems_loco = uav.scf.cf.mem.get_mems(MemoryElement.TYPE_LOCO)
        if len(mems_loco) > 0:
            mems_loco[0].update(self._anchor_position_signal)
    
        self.lock_drones.release()

    #la seconda callback avviene quando i dati provenienti dai droni sono pronti
    def _anchor_position_signal(self,mem):
    
        self.lock_anchor_writing_data.acquire()
        for anchor_number, anchor_data in enumerate(mem.anchor_data):
            if anchor_data.is_valid:
                self.anchor_pos[anchor_number]=anchor_data.position
        self.lock_anchor_data_are_ready.release()


    #questa funzione permette di creare i percorsi per i droni
    def add_route(self, data):

        eventi=EventEmitter()
        
        self.lock_drones.acquire()
        lista_drones=self.drones.items()
        self.lock_drones.release()

        self.lock_route.acquire()

        for url,drone in lista_drones:    
           self.route_collection[drone.uri]=Route_class(data[url],self.drones,url,eventi)

        self.lock_route.release()

        return "ok"
    

    def start_all_drones(self):

        self.lock_drones.acquire()

        for url,drone in self.drones.items():
            if drone.mc!=None:
                self.launchthread(drone)
            
            else:
                print("drone:",drone.uri,"not ready")
            
        self.lock_drones.release()

    def movement(self,uav: UAV):
        print("mi muovo")
        time.sleep(1)
        
        percorso=self.route_collection[uav.uri]
        
        punto=percorso.pop()
        percorso.passed(self.route_collection)
        
        punto=percorso.pop()
        
        
        if punto[1]=="takeoff":
            print("decollo")
            uav.take_off(float(punto[0][1]))
            percorso.passed(self.route_collection)
        else:
            print("errore posizione di decollo")
            return 0
        
        while True:
            punto=percorso.pop()
            
            if punto[1]=="landing":
                
                print("atteraggio")
                uav.land()
                return
            
            elif(punto[1]=="base"):
                print("vado al punto:",punto[0][0],punto[0][2],punto[0][1])
                uav.go_to(float(punto[0][0]),float(punto[0][2]),float(punto[0][1]))
            else:
                print(punto[1])
                print("vado al punto:",punto[0][0],punto[0][2],punto[0][1])
                uav.go_to(float(punto[0][0]),float(punto[0][2]),float(punto[0][1]))
                
            
            percorso.passed(self.route_collection)
        
    def launchthread(self,uav: UAV):
        th = threading.Thread(target=self.movement, args=(uav,))
        th.start()

    def set_anchor_position(self, data):
        
        self.lock_drones.acquire()
        
        json={}
        if len(self.drones)==0:
            self.lock_drones.release()
            json["status"]="no drone connected"
            return json

        
        ancore = LoPoAnchor(list(self.drones.values())[0].scf.cf)
        
        for id, pos in data.items():
            ancore.set_position(int(id), (float(pos["x"]), float(pos["z"]), float(pos["y"])))

        self.lock_drones.release()
        json["status"]="successfully anchor setted"
        return json


    def reset_estimation_for_all_drone_connected(self):
        for url,drone in self.drones.items():
            drone.reset_estimator()  