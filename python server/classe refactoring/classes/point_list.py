import threading
from pymitter import EventEmitter

import time

class Route():

    def sblocca(self):
        if self.active:
            return
        self.mutex.release()
        

    def __init__(self,json,droni,uri_input,Gestore_eventi):
        
        self.lista=[]
        self.iter=0
        self.passed_point=[]
        self.drones=droni
        self.uri=uri_input
        self.mutex=threading.Lock()
        self.mutex.acquire()
        
        self.active=True
        self.locked_on="not a meeting point"
        
        self.event=Gestore_eventi
        self.event.on("unlock_all",self.sblocca)
        
        for x in json:
            print("punto",x)
            item_to_insert={}
            for key,val in x.items():
                item_to_insert[key]=val
                #exec("item_to_insert[key]="+val)
            self.lista.append(item_to_insert) 
        
        print("route:",self.lista)
            
    def pop(self):
        
        dizio=self.lista[self.iter]
        
        cord=dizio["coordinate"]
        cord=cord.replace("(","").replace(")","").replace(" ","")
        cord=cord.split(",")
        #dizio["coordinate"]=cord
        
        tipo=dizio["type"]
        
        return (cord,tipo)
    
    def get_route(self):
        return self.lista
    
    def get_passed_point(self):
        return self.passed_point
    
    def passed(self,route_obj):
        self.passed_point.append(self.lista[self.iter])
        
        flag=False

        #se il punto è di tipo meeting
        if(self.lista[self.iter]["type"]=="meeting"): 
            #si verifica se un altro drone diverso da quello di partenza ha un punto di meeting con lo stesso nome se nessuno lo ha 
            #il drone proseguira il suo percorso
            
            for url,drone in self.drones.items():
                if url is not self.uri:    
                    #tutti i droni tranne se stesso
                    
                    if(not( route_obj[url].active) and route_obj[url].locked_on==self.lista[self.iter]["meeting_name"]):
                        flag=True
                        
                    for point in route_obj[url].get_route():
                        
                        #tutti i punti nella sua route
                        if point["type"]=="meeting" and point["meeting_name"]==self.lista[self.iter]["meeting_name"]:
                            trovato=False
                            
                            #trova un punto di tipo meeting con lo stesso nome di quello che ha appena superato
                            
                            for point2 in route_obj[url].get_passed_point():
                                if(point["meeting_name"]==point2["meeting_name"]):
                                    trovato=True
                                    
                            if not trovato:
                                self.wait(route_obj)
                                self.iter=self.iter+1
                                return
            
        #se il punto è di tipo waiting
        if self.lista[self.iter]["type"]=="waiting":
            print("aspetto",float(self.lista[self.iter]["pause_time"]))
            time.sleep(float(self.lista[self.iter]["pause_time"]))
            
        #se il punto è di tipo spinning
        if self.lista[self.iter]["type"]=="spinning":
            self.drones[self.uri].spinning()
            
            time.sleep(0.1)
            punto=self.pop()
            self.drones[self.uri].go_to(float(punto[0][0]),float(punto[0][2]),float(punto[0][1]))
        
        if(flag):
            
            self.event.emit("unlock_all")
                    
        self.iter=self.iter+1
        
    def wait(self,route_obj):
        
        self.locked_on=self.lista[self.iter]["meeting_name"]
        self.active=False
        print("vado off")
        self.mutex.acquire()
        print("torno on")
        self.locked_on="not a meeting point"
        self.active=True
        
        
        # i=0
        # while true:
        #     for url,drone in self.drones:
        #         if url is not self.url:    
        #             for point in route_obj[url].passed_point:
        #                 if point["meeting_name"]==self.lista[self.iter]["meeting_name"]:
        #                     return
        #     time.sleep(0.2)
        
        

