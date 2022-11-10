
#from classes.uav.UAV_ciccio import UAV
from cflib.crazyflie import Crazyflie
from classes.uav.unict_swarm import * 
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie

import time

import threading

class MyUAV(UAV):
    def behave(self):
        print("partenza tra 2 sec")
        time.sleep(2)
        self.take_off(0.5)
        print("mi sto muovendo")
        
        self.move_to(-1,0)
        self.move_to(0,+1)
    
        self.move_to(+1,0)
        
        self.move_to(0,-1)
        
        print("atterro")
        time.sleep(1)
        self.land()

def testTakeLand(uav: UAV):
    
    print("partenza tra 2 sec")
    time.sleep(2)
    uav.take_off(0.5)
    print("mi sto muovendo")
    
    uav.move_to(-1,0)
    uav.move_to(0,+1)
   
    uav.move_to(+1,0)
    
    uav.move_to(0,-1)
    print("atterro")
    time.sleep(1)
    uav.land()
    print(uav.x, uav.y, uav.z)



URI5 = 'radio://0/102/2M/E7E7E7E705'



if __name__ == '__main__':
    SW.create_swarm([(URI5, MyUAV) ])
    time.sleep(5)
    #SW.create_meeting_point('start')
    
    SW.run_swarm(use_remote=False)
