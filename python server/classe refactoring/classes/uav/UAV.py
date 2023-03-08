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

X_THRESHOLD = 0.1 # 10cm
Y_THRESHOLD = 0.1 # 10cm
Z_THRESHOLD = 0.2 # 20cm

class UAV :

    DEFAULT_HEIGHT = 0.4
    DEFAULT_SPEED = 0.2

    def __init__(self, uri) -> None:
        cflib.crtp.init_drivers(enable_serial_driver=True)

        self.uri = uri
        self.events = EventEmitter()
        self.crazyflie = Crazyflie()
        self.scf = None
        self.mc = None
        self.pc = None

        self.positionEstimated = False

        self.logConf = LogConfig(name='Position', period_in_ms=250)
        self.logConf.add_variable('kalman.stateX', 'float')
        self.logConf.add_variable('kalman.stateY', 'float')
        self.logConf.add_variable('kalman.stateZ', 'float')
        self.logConf.add_variable('pm.vbat', 'float')
        self.logConf.add_variable('stabilizer.yaw', 'float')

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

        self.x = None
        self.y = None
        self.z = None
        self.battery = None
        self.roll = None
        self.pitch = None 
        self.yaw = None
        self.origin = None

        self.controller_inizialized=False
        
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

    def take_off(self):
        self.origin = [ self.x, self.y , self.z]
        
        #self.crazyflie.commander.send_position_setpoint(self.origin[0], self.origin[1], UAV.DEFAULT_HEIGHT, self.yaw)
        #self.crazyflie.high_level_commander.set_group_mask()
        #self.crazyflie.high_level_commander.takeoff(absolute_height_m= UAV.DEFAULT_HEIGHT, duration_s= 1)
        #self.pc.go_to(self.x,  self.y, 0.1)
        
        self.scf.cf.high_level_commander.takeoff(0.3,0.3/0.2)
        time.sleep(0.3/0.2)
        
        #self.pc.take_off()
        
        
        #self.pc._is_flying=True
        #print(self.origin[2])
        
    
    def land(self):
        self.pc.land()
        
        #self.crazyflie.commander.send_position_setpoint(self.origin[0], self.origin[1], self.origin[2], self.yaw)
        #self.crazyflie.high_level_commander.land(absolute_height_m= float(self.z), duration_s= 1)

    def move_by(self, x, y, z = None):
        self.target_x = self.x + x
        self.target_y = self.y + y
        
        if z is not None:
            self.target_z = self.z + z
            
        self.pc.go_to(self.target_x,self.target_y,self.target_z)

    def _do_move(self):
        #print("Going to {},{},{}".format(self.target_x, self.target_y, self.target_z))
        
        self.pc.go_to(self.target_x,self.target_y,self.target_z)
        
        """
        while (abs(self.z - self.target_z) > Z_THRESHOLD) \
          or(abs(self.y - self.target_y) > Y_THRESHOLD) \
          or(abs(self.x - self.target_x) > X_THRESHOLD):
            time.sleep(0.2)
            self.pc.go_to(self.target_x,
                                                    self.target_y,
                                                    self.target_z,
                                                    self.target_yaw)"""


    #events
    # Called when the link is established and the TOCs (that are not cached)
    # have been downloaded
    def _on_connected(self, uri):
        print("UAV Connected,classe", uri)
        #self.crazyflie.log.add_config(self.logConf)
        self.scf = SyncCrazyflie(self.uri, self.crazyflie)
        self.crazyflie.log.add_config(self.logConfEstimation)
        if self.logConfEstimation.valid:
            self.events.emit(UAVEvents.CONNECTED, self)
            self.logConfEstimation.start()
        else:
            exit(1)
        pass
    # Called on disconnect, no matter the reason
    def _on_disconnected(self, uri):
        self.events.emit(UAVEvents.DISCONNECTED, self)
        print("Drone Disconnected", uri)
        pass

    # Called on unintentional disconnect only
    def _on_connection_lost(self, uri, message):
        self.events.emit(UAVEvents.CONNECTION_LOST, self)
        print("Connection Lost", uri)
        pass

    # Called when the first packet in a new link is received
    def _on_link_established(self, uri):
        self.events.emit(UAVEvents.LINK_ESTABLISHED, self)
        pass

    # Called if establishing of the link fails (i.e times out)
    def _on_connection_failed(self, uri ,error):
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
        self.roll = 0#data['stabilizer.roll']
        self.pitch = 0# data['stabilizer.pitch']
        
        self.yaw = data['stabilizer.yaw']
        
            
        if self.positionEstimatedEmitted is not True:
            self.positionEstimatedEmitted = True
            self.events.emit(UAVEvents.POSITION_READY)
        #print ("[%d][%s]: %s" % (timestamp, logconf.name, data))
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
        print("Estimation Completed test")
        self.positionEstimated = True
        self.positionEstimatedEmitted = False
        
        self.crazyflie.log.add_config(self.logConf)
        self.logConf.start()
        #self.events.emit(UAVEvents.POSITION_READY, self)
 

    def initialize_controller(self):
        self.mc = MotionCommander(crazyflie = self.scf, default_height = UAV.DEFAULT_HEIGHT)
        """self.pc = PositionHlCommander(crazyflie = self.scf, x=self.x, y=self.y, z=self.z, \
                                    default_height = self.z+UAV.DEFAULT_HEIGHT, default_velocity = UAV.DEFAULT_SPEED,\
                                    default_landing_height=self.z)
       """ 
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