
from classes.uav.UAV_ciccio import UAV
#from classes.uav.unict_swarm import UAV 

from classes.uav.UAVEvents import UAVEvents
import time

import threading

def connesso(uav:UAV):
    print("connesso")
    launchthread(uav)
    
def testTakeLand(uav: UAV):
    print("partenza tra 6 sec")
    time.sleep(6)
    
    #print(uav.x, uav.y, uav.z)
    uav.take_off()
    print("mi sto muovendo")
    
    #uav.go_to(uav.x,uav.z,z=0.3)
    
    uav.go_to(-0.5,-0.5,z=0)
    
    uav.go_to(-0.5,0.5,z=0)
   
    uav.go_to(0.5,0.5,z=0)
    
    uav.go_to(0.5,-0.5,z=0)
    
    uav.go_to(0,0,z=0)
    
    print("atterro")
    time.sleep(1)
    uav.land()
    print(uav.x, uav.y, uav.z)
    
    
    
    


def launchthread(uav: UAV):
    th = threading.Thread(target=testTakeLand, args=(uav,))
    th.start()

uavTest = UAV('radio://0/102/2M/E7E7E7E705')

uavTest.events.on(UAVEvents.CONNECTED, connesso)

uavTest.connect()

