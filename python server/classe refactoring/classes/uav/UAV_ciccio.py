from operator import truediv
from turtle import distance
from typing import Counter
from pymitter import EventEmitter
import time
import sys
import math

import cflib.crtp
from cflib.crazyflie import Crazyflie
from cflib.crazyflie.log import LogConfig
from cflib.positioning.motion_commander import MotionCommander
from cflib.positioning.position_hl_commander import PositionHlCommander
from cflib.crazyflie.syncCrazyflie import SyncCrazyflie
from cflib.crazyflie.syncLogger import SyncLogger

from classes.uav.UAVEvents import UAVEvents

X_THRESHOLD = 0.07 # 10cm
Y_THRESHOLD = 0.07 # 10cm
Z_THRESHOLD = 0.14 # 20cm

class UAV :

    DEFAULT_HEIGHT = 0.2
    DEFAULT_SPEED = 0.2

    def __init__(self, uri) -> None:
        cflib.crtp.init_drivers(enable_serial_driver=True)

        self.uri = uri
        self.events = EventEmitter()
        self.crazyflie = Crazyflie()
        self.scf = None
        self.mc = None
        self.pc = None
        #status: connected, disconnected
        self.status="connected"
        self.positionEstimated = False

        self.logConf = LogConfig(name='Position', period_in_ms=100)
        self.logConf.add_variable('kalman.stateX', 'float')
        self.logConf.add_variable('kalman.stateY', 'float')
        self.logConf.add_variable('kalman.stateZ', 'float')
        self.logConf.add_variable('pm.vbat', 'float')
        
        # self.logConf.add_variable('stabilizer.yaw', 'float')
        
        # self.logConf.add_variable('stabilizer.pitch', 'float')
        # self.logConf.add_variable('stabilizer.roll', 'float')
        
        #test gyro.zRaw gyro.yRaw gyro.xRaw
        
        self.logConfEstimation = LogConfig(name='Kalman Variance', period_in_ms=500)
        self.logConfEstimation.add_variable('kalman.varPX', 'float')
        self.logConfEstimation.add_variable('kalman.varPY', 'float')
        self.logConfEstimation.add_variable('kalman.varPZ', 'float')
        self.logConfEstimation.add_variable('pm.vbat', 'float')

        self.var_y_history = [1000] * 10
        self.var_x_history = [1000] * 10
        self.var_z_history = [1000] * 10

        self.target_x = 0
        self.target_y = 0
        self.target_z = 0
        self.target_yaw = 0

        self.x = 0
        self.y = 0
        self.z = 0
        self.starting_z=None
        
        self.battery = 0
        self.roll = None
        self.pitch = None 
        self.yaw = 0
        self.past_yaw=None
        self.origin = None
        self.flag=True
        self.controller_inizialized=False
        self.connected = False
        
        self.events.on(UAVEvents.POSITION_READY,self.initialize_controller)
        
        self._register_callbacks()
    
    

    def connect(self):
        self.crazyflie.open_link(self.uri)
        
    def disconnect(self):
        self.crazyflie.close_link()


    def resetPositionEstimation(self):
        self.crazyflie.param.set_value('kalman.resetEstimation', '1')
        time.sleep(0.5)
        self.crazyflie.param.set_value('kalman.resetEstimation', '0')

    def take_off(self, my_height):
        self.starting_z=self.z
        
        self.origin = [ self.x, self.y , self.z]
        
        self.mc.take_off(height=my_height)
        
        
        
    
    def land(self):
        distance=self.z-self.starting_z
        
        self.mc.down(abs(distance),velocity=0.1)
        
        #this code si copied from the motion controll class 
        
        self.mc._thread.stop()
        self.mc._thread = None
        self.mc._cf.commander.send_stop_setpoint()
        self.mc._is_flying = False
        
        #self.mc.land()


    def go_to(self, x, y, z=0):
        
        distance_x=x - self.x
        distance_y=y - self.y    
        distance_z=z - self.z
        
        counter=0
        # print("devo andare:",x," , ",y," , ",z)
        # print("mi devo muovere di",distance_x," , ",distance_y," , ",distance_z," , ",counter)
        
        # print("x,y distance",((abs(distance_x)>=X_THRESHOLD)or(abs(distance_y)>=Y_THRESHOLD)))
        # print(abs((abs(distance_z)>=Z_THRESHOLD)))
        
        while((counter<=7) and (abs(distance_x)>=X_THRESHOLD) or (abs(distance_y)>=Y_THRESHOLD) or (abs(distance_z)>=Z_THRESHOLD)):
            # print("mi muovo")
            self.mc.move_distance(distance_x,distance_y,distance_z)
            
            distance_x=x - self.x
            distance_y=y - self.y    
            distance_z=z - self.z
            
            #print("mi devo muovere di", distance_x," , ",distance_y," , ",distance_z," , ",counter)
            
            counter=counter+1
        
    def spinning (self):
        self.mc.turn_left(360)
        
    def reset_estimator(self):
         
        self.mc._reset_position_estimator()
        print(self.uri,"estimator resetted")
        
        
    #events
    # Called when the link is established and the TOCs (that are not cached)
    # have been downloaded
    
    def _on_connected(self, uri):
        print("UAV Connected,", uri)
        self.connected = True
        #self.crazyflie.log.add_config(self.logConf)
        self.scf = SyncCrazyflie(self.uri, self.crazyflie)
        self.crazyflie.log.add_config(self.logConfEstimation)
        if self.logConfEstimation.valid:
            print("qui")
            self.events.emit(UAVEvents.CONNECTED, self)
            self.logConfEstimation.start()
        else:
            exit(1)
        pass
    # Called on disconnect, no matter the reason
    
    def _on_disconnected(self, uri):
        self.events.emit(UAVEvents.DISCONNECTED, self)
        self.status="disconnected"
        print("Drone Disconnected", uri)
        pass

    # Called on unintentional disconnect only
    def _on_connection_lost(self, uri, message):
        #self.events.emit(UAVEvents.CONNECTION_LOST, self)
        #self.status="disconnected"
        print("Connection Lost", uri)
        pass

    # Called when the first packet in a new link is received
    def _on_link_established(self, uri):
        self.events.emit(UAVEvents.LINK_ESTABLISHED, self)
        pass

    # Called if establishing of the link fails (i.e times out)
    def _on_connection_failed(self, uri ,error):
        print("errore connessione")
        self.status="disconnected"
        self.events.emit(UAVEvents.CONNECTION_FAILED, self, error)
        print(error)
        pass

    # Called when the link driver updates the link quality measurement
    def _on_link_quality_updated(self, quality):
        self.events.emit(UAVEvents.LINK_QUALITY_UPDATE, self, quality)
        #print(quality)
        pass

    # Called for every packet received
    def _on_packet_received(self, packet):
        pass

    # Called for every packet received
    def _on_data_received(self, timestamp, data, logconf):
        
        self.events.emit(UAVEvents.DATA_RECEIVED, self, data)
        self.x = data['kalman.stateX']
        self.y = data['kalman.stateY']
        self.z = data['kalman.stateZ']
        self.battery = data['pm.vbat']

        pass

    def _on_data_estimation_received(self, timestamp, data, logconf):
        threshold = 0.001
        self.var_x_history.append(data['kalman.varPX'])
        self.var_x_history.pop(0)
        self.var_y_history.append(data['kalman.varPY'])
        self.var_y_history.pop(0)
        self.var_z_history.append(data['kalman.varPZ'])
        self.var_z_history.pop(0)

        min_x = min(self.var_x_history)
        max_x = max(self.var_x_history)
        min_y = min(self.var_y_history)
        max_y = max(self.var_y_history)
        min_z = min(self.var_z_history)
        max_z = max(self.var_z_history)

        print("ricevuta varianza controllo soglia")

        if (max_x - min_x) < threshold and (max_y - min_y) < threshold and (max_z - min_z) < threshold:
            
            self.logConfEstimation.stop()
            self.var_y_history = []
            self.var_x_history = []
            self.var_z_history = []
            
            self._on_position_estimation_finished()
            

    def _on_position_estimation_finished(self):
        print("Estimation Completed")
        self.positionEstimated = True
        self.positionEstimatedEmitted = False
        self.crazyflie.log.add_config(self.logConf)
        self.logConf.start()
        
        self.events.emit(UAVEvents.POSITION_READY)
 

    def initialize_controller(self):
        self.starting_z=self.z
        self.mc = MotionCommander(crazyflie = self.scf, default_height = UAV.DEFAULT_HEIGHT)
        self.events.emit(UAVEvents.CONTROLLER_READY, self)
        

    def _register_callbacks(self):
        self.crazyflie.connected.add_callback(self._on_connected)
        self.crazyflie.disconnected.add_callback(self._on_disconnected)
        self.crazyflie.connection_lost.add_callback(self._on_connection_lost)
        self.crazyflie.connection_failed.add_callback(self._on_connection_failed)
        self.crazyflie.link_established.add_callback(self._on_link_established)
        self.crazyflie.link_quality_updated.add_callback(self._on_link_quality_updated)
        self.crazyflie.packet_received.add_callback(self._on_packet_received)
        self.logConf.data_received_cb.add_callback(self._on_data_received)
        self.logConfEstimation.data_received_cb.add_callback(self._on_data_estimation_received)

    def _set_initial_position(self, x, y, z, yaw):
        self.crazyflie.param.set_value('kalman.initialX', x)
        self.crazyflie.param.set_value('kalman.initialY', y)
        self.crazyflie.param.set_value('kalman.initialZ', z)
        
        yaw_radians = math.radians(yaw)
        self.crazyflie.param.set_value('kalman.initialYaw', yaw_radians)