from pymitter import EventEmitter
from classes.uav.UAVEvents import UAVEvents
import threading
import time

eventi=EventEmitter()

mutex=threading.Lock()
mutex.acquire()

def rilascia_mutex(mutex):
    mutex.release()

def posizione(eventi,mutex):
    eventi.on("rilascia",rilascia_mutex)

def movement(mutex,eventi):
    time.sleep(3)
    eventi.emit("rilascia",mutex)

    time.sleep(3)
    eventi.emit("rilascia",mutex)
    
def agente_1(eventi,mutex):
    mutex.acquire()
    print("yatta")


def agente_2(eventi,mutex):
    mutex.acquire()
    print("yatta2")



th = threading.Thread(target=movement, args=(mutex,eventi))
th.start()

th1 = threading.Thread(target=agente_1, args=(eventi,mutex))
th1.start()

th2 = threading.Thread(target=agente_2, args=(eventi,mutex))
th2.start()

th3 = threading.Thread(target=posizione(eventi, mutex))
th3.start()

