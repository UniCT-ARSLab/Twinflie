# -*- coding: utf-8 -*-
#
#  UNICT CRAZYFLIE SWARM LIBRARY
#
#  Copyright (C) Corrado Santoro, santoro@dmi.unict.it
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.

#  You should have received a copy of the GNU General Public License along with
#  this program; if not, write to the Free Software Foundation, Inc., 51
#  Franklin Street, Fifth Floor, Boston, MA  02110-1301, USA.


import os
import time
import math
import threading
import traceback
import types
#import pygame
import serial

import cflib.crtp
from cflib.crazyflie.log import LogConfig
from cflib.crazyflie.swarm import CachedCfFactory
from cflib.crazyflie.swarm import Swarm
from cflib.crazyflie.syncLogger import SyncLogger


X_THRESHOLD = 0.1 # 10cm
Y_THRESHOLD = 0.1 # 10cm
Z_THRESHOLD = 0.2 # 20cm

QFE_THRESHOLD = 0.5

LANDING_VZ = -0.5 #50cm/s

TX_DELAY = 0.2
LOGGING_PERIOD = 1000

def normalize_angle(angle):
    while angle >= 360:
        angle = angle - 360
    while angle <= 360:
        angle = angle + 360
    return angle


class ForceLandingException(Exception):
    pass


class UAV:

    def __init__(self):
        self.scf = None
        self.cf = None
        self._id = None
        self.flying = False
        self.rtl = [ 0, 0 ]
        self.origin = None
        self.force_landing = False
        self.is_async = False
        self.target_x = 0
        self.target_y = 0
        self.target_z = 0
        self.target_yaw = 0

    def on_start(self):
        pass

    def set_async(self, uVal):
        self.is_async = uVal

    def log(self, _str):
        if self.cf is None:
            print(_str)
        else:
            print("[{}] {}".format(self.cf.link_uri, _str))

    def set_id(self, _id):
        self._id = _id

    def get_id(self):
        return self._id

    def set_scf(self, scf):
        self.scf = scf
        self.cf = self.scf.cf

    def reset_estimator(self):
        self.cf.param.set_value('kalman.resetEstimation', '1')
        time.sleep(TX_DELAY)
        self.cf.param.set_value('kalman.resetEstimation', '0')
        self._wait_for_position_estimator()
        self._start_log_position()
        time.sleep((LOGGING_PERIOD * 2)/1000.0)
        self.log('Estimator OK: Battery {}'.format(self.battery))

    def _wait_for_position_estimator(self):
        print('Waiting for estimator to find position...')

        log_config = LogConfig(name='Kalman Variance', period_in_ms=500)
        log_config.add_variable('kalman.varPX', 'float')
        log_config.add_variable('kalman.varPY', 'float')
        log_config.add_variable('kalman.varPZ', 'float')
        log_config.add_variable('pm.vbat', 'float')

        var_y_history = [1000] * 10
        var_x_history = [1000] * 10
        var_z_history = [1000] * 10

        threshold = 0.001

        with SyncLogger(self.scf, log_config) as logger:
            for log_entry in logger:
                data = log_entry[1]

                var_x_history.append(data['kalman.varPX'])
                var_x_history.pop(0)
                var_y_history.append(data['kalman.varPY'])
                var_y_history.pop(0)
                var_z_history.append(data['kalman.varPZ'])
                var_z_history.pop(0)

                min_x = min(var_x_history)
                max_x = max(var_x_history)
                min_y = min(var_y_history)
                max_y = max(var_y_history)
                min_z = min(var_z_history)
                max_z = max(var_z_history)

                self.battery = data['pm.vbat']

                #print("{} {} {}".
                #    format(max_x - min_x, max_y - min_y, max_z - min_z))

                if (max_x - min_x) < threshold and (
                        max_y - min_y) < threshold and (
                        max_z - min_z) < threshold:
                    break



    def _start_log_position(self):
        self.log_conf = LogConfig(name='Position', period_in_ms=LOGGING_PERIOD)
        self.log_conf.add_variable('kalman.stateX', 'float')
        self.log_conf.add_variable('kalman.stateY', 'float')
        self.log_conf.add_variable('kalman.stateZ', 'float')
        self.log_conf.add_variable('pm.vbat', 'float')
        #self.log_conf.add_variable('stabilizer.roll', 'float')
        #self.log_conf.add_variable('stabilizer.pitch', 'float')
        self.log_conf.add_variable('stabilizer.yaw', 'float')

        self.cf.log.add_config(self.log_conf)
        self.log_conf.data_received_cb.add_callback(self._position_callback)
        self.log_conf.start()


    def _position_callback(self, timestamp, data, logconf):
        self.x = data['kalman.stateX']
        self.y = data['kalman.stateY']
        self.z = data['kalman.stateZ']
        self.battery = data['pm.vbat']
        self.roll = 0#data['stabilizer.roll']
        self.pitch = 0# data['stabilizer.pitch']
        self.yaw = data['stabilizer.yaw']
        print('[{}] Pos: ({}, {}, {}), Battery: {}'.format(self.cf.link_uri, self.x, self.y, self.z, self.battery))
        if self.battery < 3.1:
            self.log('LOW BATTERY, VOLTAGE = {}! LANDING'.format(self.battery))
            SW.force_landing() # land


    def _do_move(self):
        #print("Going to {},{},{}".format(self.target_x, self.target_y, self.target_z))
        for _ in range(0, 2):
            time.sleep(TX_DELAY)
            if self.force_landing:
                raise ForceLandingException()
            self.cf.commander.send_position_setpoint(self.target_x,
                                                    self.target_y,
                                                    self.target_z,
                                                    self.target_yaw)
        if self.is_async:
            return

        while (abs(self.z - self.target_z) > Z_THRESHOLD) \
          or(abs(self.y - self.target_y) > Y_THRESHOLD) \
          or(abs(self.x - self.target_x) > X_THRESHOLD):
            time.sleep(TX_DELAY)
            if self.force_landing:
                raise ForceLandingException()
            self.cf.commander.send_position_setpoint(self.target_x,
                                                    self.target_y,
                                                    self.target_z,
                                                    self.target_yaw)

    #
    # motion methods
    #
    def take_off(self, target_z):
        self.log("Take-off")
        self.QFE = self.z
        self.rtl = [ self.x, self.y ]
        if self.origin is None:
            self.origin = [ self.x, self.y ]
        self.target_x = self.x
        self.target_y = self.y
        self.target_z = target_z
        self.cf.commander.send_position_setpoint(self.target_x,
                                                 self.target_y,
                                                 self.target_z,
                                                 self.target_yaw)
        if self.force_landing:
            raise ForceLandingException()
        self.flying = True
        if self.is_async:
            return

        while abs(self.z - target_z) > Z_THRESHOLD:
            time.sleep(TX_DELAY)
            if self.force_landing:
                raise ForceLandingException()
            self.cf.commander.send_position_setpoint(self.target_x,
                                                    self.target_y,
                                                    self.target_z,
                                                    self.target_yaw)

    def land(self):
        self.log("Land")
        if not(self.flying):
            return
        increment = LANDING_VZ * TX_DELAY
        self.target_z = self.z
        while self.target_z >= (self.QFE - QFE_THRESHOLD):
            time.sleep(TX_DELAY)
            self.cf.commander.send_position_setpoint(self.target_x,
                                                     self.target_y,
                                                     self.target_z,
                                                     self.target_yaw)
            self.target_z = self.target_z + increment
        self.cf.commander.send_stop_setpoint()
        self.flying = False

    def move_by(self, x, y, z = None):
        self.log("Move by {}, {}, {}".format(x,y,z))
        self.target_x = self.x + x
        self.target_y = self.y + y
        if z is not None:
            self.target_z = self.z + z
        self._do_move()

    def move_to(self, x, y, z = None):
        if x is not None:
            self.target_x = x + self.origin[0]

        if y is not None:
            self.target_y = y + self.origin[1]

        #if z is not None:
        #    self.target_z = z

        self.log("Move to {}, {}, {}".format(self.target_x, self.target_y, self.target_z))
        self._do_move()

    def move_to_with_speed(self, x, y, speed):
        self.target_x = x + self.origin[0]
        self.target_y = y + self.origin[1]

        start_x = self.x
        start_y = self.y

        rho = math.hypot(self.target_y - start_y, self.target_x - start_x)
        theta = math.atan2(self.target_y - start_y, self.target_x - start_x)
        increment = speed * TX_DELAY

        self.log("Move to {}, {}, {} with speed {}".format(self.target_x, self.target_y, self.target_z, speed))

        r = 0
        while r < rho:
            x = r * math.cos(theta) + start_x
            y = r * math.sin(theta) + start_y
            time.sleep(TX_DELAY)
            self.cf.commander.send_position_setpoint(x,
                                                     y,
                                                     self.z,
                                                     self.yaw)
            r += increment

        self.log("Position reached {}, {}, {}".format(self.target_x, self.target_y, self.target_z))


    def set_local_speed(self, vx, vy, vz, yawrate):
        (vx, vy) = self.local_to_global_2d(vx, vy)
        self.cf.commander.send_velocity_world_setpoint(vx, vy, vz, yawrate)
        time.sleep(TX_DELAY)

    def set_origin(self, x, y):
        self.origin = [x, y]

    def home(self):
        self.log("Home")
        self.move_to(0, 0, None)

    def return_to_launch(self):
        self.log("Return to Launch")
        self.target_x = self.rtl[0]
        self.target_y = self.rtl[1]
        self.target_z = self.z
        self._do_move()

    def set_yaw(self, yaw):
        self.log("Set yaw")
        #self.target_x = self.x
        #self.target_y = self.y
        #self.target_z = self.z
        self.target_yaw = yaw
        self.cf.commander.send_position_setpoint(self.target_x,
                                                self.target_y,
                                                self.target_z,
                                                self.target_yaw)
        time.sleep(TX_DELAY)

    def spin(self, speed):
        self.log("Spinning")
        increment = abs(speed) * TX_DELAY
        if speed < 0:
            sign = -1
        else:
            sign = +1
        angle = 0.0
        while angle <= 360:
            if self.force_landing:
                raise ForceLandingException()
            self.cf.commander.send_position_setpoint(self.target_x, self.target_y, self.target_z, sign*angle)
            time.sleep(TX_DELAY)
            angle += increment

    # starting pos is current UAV position
    # angle and speed are in degrees
    def rotate_circular(self, centerX, centerY, target_angle, speed):
        self.log("Rotate Circular of {} degrees around {}".format(target_angle, (centerX, centerY)))
        current_angle = math.degrees(math.atan2(self.y - self.origin[1] - centerY,
                                                self.x - self.origin[0] - centerX))
        radius = math.hypot(self.x - self.origin[0] - centerX,
                            self.y - self.origin[1] - centerY)
        #print("Current angle {}, radius {}".format(current_angle, radius))
        increment = abs(speed) * TX_DELAY
        if speed < 0:
            sign = -1
        else:
            sign = +1
        angle = 0.0
        while angle <= target_angle:
            if self.force_landing:
                raise ForceLandingException()
            x = centerX + radius * math.cos(math.radians(current_angle + sign*angle))
            y = centerY + radius * math.sin(math.radians(current_angle + sign*angle))
            self.target_x = x + self.origin[0]
            self.target_y = y + self.origin[1]
            self.cf.commander.send_position_setpoint(self.target_x, self.target_y, self.target_z, self.target_yaw)
            time.sleep(TX_DELAY)
            angle += increment

    def rotate_ellipse(self, centerX, centerY, a, b, target_angle, speed):
        self.log("Rotate Ellipse of {} degrees around {}".format(target_angle, (centerX, centerY)))
        current_angle = math.degrees(math.atan2(self.y - self.origin[1] - centerY,
                                                self.x - self.origin[0] - centerX))
        #print("Current angle {}, radius {}".format(current_angle, radius))
        increment = speed * TX_DELAY
        if target_angle < 0:
            target_angle = - target_angle
            sign = -1
        else:
            sign = +1
        angle = 0.0
        while angle <= target_angle:
            if self.force_landing:
                raise ForceLandingException()
            x = centerX + a * math.cos(math.radians(current_angle + sign*angle))
            y = centerY + b * math.sin(math.radians(current_angle + sign*angle))
            self.target_x = x + self.origin[0]
            self.target_y = y + self.origin[1]
            self.cf.commander.send_position_setpoint(self.target_x, self.target_y, self.target_z, self.target_yaw)
            time.sleep(TX_DELAY)
            angle += increment

    # starting pos (current UAV position) must be at deg = 0, center of the eight
    # angle and speed are in degrees
    def rotate_eight_along_x(self, alpha, speed):
        self.log("Rotate Eight Along X {}, {}".format(alpha, speed))
        centerX = self.target_x - self.origin[0]
        centerY = self.target_y - self.origin[1]
        #print("Current angle {}, radius {}".format(current_angle, radius))
        increment = abs(speed) * TX_DELAY
        if speed < 0:
            sign = -1
        else:
            sign = +1
        angle = 0.0
        while angle <= 360:
            if self.force_landing:
                raise ForceLandingException()
            sn = math.sin(math.radians(sign*angle))
            co = math.cos(math.radians(sign*angle))
            x = centerX + alpha * sn
            y = centerY + alpha * sn * co
            self.target_x = x + self.origin[0]
            self.target_y = y + self.origin[1]
            self.cf.commander.send_position_setpoint(self.target_x, self.target_y, self.target_z, self.target_yaw)
            time.sleep(TX_DELAY)
            angle += increment

    def rotate_eight_along_y(self, alpha, speed):
        self.log("Rotate Eight Along Y {}, {}".format(alpha, speed))
        centerX = self.target_x - self.origin[0]
        centerY = self.target_y - self.origin[1]
        #print("Current angle {}, radius {}".format(current_angle, radius))
        increment = abs(speed) * TX_DELAY
        if speed < 0:
            sign = -1
        else:
            sign = +1
        angle = 0.0
        while angle <= 360:
            if self.force_landing:
                raise ForceLandingException()
            sn = math.sin(math.radians(sign*angle))
            co = math.cos(math.radians(sign*angle))
            x = centerX + alpha * sn * co
            y = centerY + alpha * sn
            self.target_x = x + self.origin[0]
            self.target_y = y + self.origin[1]
            self.cf.commander.send_position_setpoint(self.target_x, self.target_y, self.target_z, self.target_yaw)
            time.sleep(TX_DELAY)
            angle += increment

    def rotate_vertical_eight_along_y(self, alpha, speed):
        self.log("Rotate Vertical Eight Along Y {}, {}".format(alpha, speed))
        centerZ = self.target_z
        centerY = self.target_y - self.origin[1]
        #print("Current angle {}, radius {}".format(current_angle, radius))
        increment = abs(speed) * TX_DELAY
        if speed < 0:
            sign = -1
        else:
            sign = +1
        angle = 0.0
        while angle <= 360:
            if self.force_landing:
                raise ForceLandingException()
            sn = math.sin(math.radians(sign*angle))
            co = math.cos(math.radians(sign*angle))
            z = centerZ + alpha * sn * co
            y = centerY + alpha * sn
            self.target_z = z
            self.target_y = y + self.origin[1]
            self.cf.commander.send_position_setpoint(self.target_x, self.target_y, self.target_z, self.target_yaw)
            time.sleep(TX_DELAY)
            angle += increment

    #
    # synchronization methods
    #
    def meet(self, meeting_point):
        self.log('Meet at {}'.format(meeting_point))
        mp = SW.get_meeting_point(meeting_point)
        #print("object {}, id {}".format(self, self._id))
        mp.set(self._id)
        while not(mp.check()):
            if self.force_landing:
                raise ForceLandingException()
            if (self.cf is not None)and(self.flying):
                self.cf.commander.send_position_setpoint(self.target_x,
                                                        self.target_y,
                                                        self.target_z,
                                                        self.target_yaw)
            time.sleep(TX_DELAY)
        mp.leave(self._id)

    def wait(self, token):
        t = SW.get_token(token)
        while not(t.wait()):
            if self.force_landing:
                raise ForceLandingException()
            if (self.cf is not None)and(self.flying):
                self.cf.commander.send_position_setpoint(self.target_x,
                                                        self.target_y,
                                                        self.target_z,
                                                        self.target_yaw)
            time.sleep(TX_DELAY)

    def give(self, token):
        t = SW.get_token(token)
        t.give()

    def sleep(self, delay_time):
        t = 0
        while t < delay_time:
            if self.force_landing:
                raise ForceLandingException()
            if (self.cf is not None)and(self.flying):
                self.cf.commander.send_position_setpoint(self.target_x,
                                                        self.target_y,
                                                        self.target_z,
                                                        self.target_yaw)
            time.sleep(TX_DELAY)
            t = t + TX_DELAY

    def at(self, minutes, seconds):
        self.log("Waiting timer {}:{}".format(minutes, seconds))
        the_time = minutes * 60 + seconds
        while not(SW.check_timer(the_time)):
            if self.force_landing:
                raise ForceLandingException()
            if (self.cf is not None)and(self.flying):
                self.cf.commander.send_position_setpoint(self.target_x,
                                                        self.target_y,
                                                        self.target_z,
                                                        self.target_yaw)
            time.sleep(TX_DELAY)


    #
    # geometry methods
    #
    def global_to_local_2d(self, x, y):
        cos_t = math.cos(math.radians(self.target_yaw))
        sin_t = math.sin(math.radians(self.target_yaw))
        dx = x - self.x
        dy = y - self.y
        local_x = dx * cos_t + dy * sin_t
        local_y = - dx * sin_t + dy * cos_t
        return (local_x, local_y)

    def local_to_global_2d(self, x, y):
        cos_t = math.cos(math.radians(self.target_yaw))
        sin_t = math.sin(math.radians(self.target_yaw))
        global_point_x = self.x + x * cos_t - y * sin_t
        global_point_y = self.y + x * sin_t + y * cos_t
        return (global_point_x, global_point_y)

    #
    # other methods
    #
    def set_leader(self):
        SW.set_leader(self._id)

    def get_leader(self):
        return SW.get_leader_object()


class JoyRemoteController(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        pygame.init()

    def run(self):
        pygame.joystick.Joystick(0).init()
        mp = SW.get_meeting_point('__starter__')
        while True:
            events = pygame.event.get()
            for event in events:
                if event.type == pygame.JOYBUTTONDOWN:
                    #print(event.button)
                    if event.button == 10:
                        print("[RemoteController] Emergency landing")
                        SW.force_landing() # land
                    if event.button == 11:
                        print('[RemoteController] KILLING')
                        os.kill(os.getpid(), 9) # stop-all
                    if event.button == 9:
                        print("[RemoteController] GO!")
                        mp.set(len(SW.uavs))
                        SW.start_timer()
            time.sleep(0.5)


class SerialRemoteController(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.setDaemon(True)
        self.__ser = serial.Serial("/dev/ttyACM0", 115200, 8, "N", 1, 1000)
        self.__ser.write("RST\r")

    def run(self):
        self.__ser.write("RDY\r")
        mp = SW.get_meeting_point('__starter__')
        while True:
            line = self.__ser.readline()
            if line is not None:
                if line[0:5] == "START":
                    print("[RemoteController] GO!")
                    mp.set(len(SW.uavs))
                    SW.start_timer()
                elif line[0:4] == "STOP":
                    print('[RemoteController] KILLING')
                    os.kill(os.getpid(), 9) # stop-all
                elif line[0:4] == "LAND":
                    print("[RemoteController] Emergency landing")
                    SW.force_landing() # land


class MeetingPoint:

    def __init__(self, num):
        self.num = num
        self.value = 0
        self.count = 0
        self.target = 2**num - 1
        self.mutex = threading.Lock()

    def set(self, _id):
        try:
            self.mutex.acquire()
            self.value = self.value | (1 << _id)
            self.count += 1
        finally:
            self.mutex.release()

    def leave(self, _id):
        try:
            self.mutex.acquire()
            self.count -= 1
            if self.count == 0:
                self.value = 0
        finally:
            self.mutex.release()

    def check(self):
        try:
            self.mutex.acquire()
            #print("V: {}, T: {}".format(self.value, self.target))
            if self.value == self.target:
                return True
            else:
                return False
        finally:
            self.mutex.release()


class Token:

    def __init__(self):
        self.sem = threading.Semaphore(0)

    def give(self):
        self.sem.release()

    def wait(self):
        return self.sem.acquire(False)



class SW:

    uris = [ ]
    uavs = { }
    uavs_by_id = { }
    meeting_points = { }
    tokens = { }
    leader_id = None

    @classmethod
    def create(cls, scf):
        uri = scf.cf.link_uri
        uav = UAV()
        uav.set_scf(scf)
        cls.uavs[uri] = uav

    @classmethod
    def create_swarm(cls, all_uavs):
        uris = { }
        classes = [ ]
        idx = 0
        for (radio_url, _class) in all_uavs:
            uris[radio_url] = idx
            classes.append(_class)
            idx = idx + 1
        cls.uris = uris
        for uri in uris.keys():
            idx = uris[uri]
            uav = classes[idx]()
            uav.set_id(idx)
            cls.uavs[uri] = uav
            cls.uavs_by_id[idx] = uav


    # ---------------------------------------
    @classmethod
    def set_leader(cls, leader_id):
        cls.leader_id = leader_id

    @classmethod
    def get_leader_object(cls):
        return cls.get_uav_by_id(cls.leader_id)

    # ---------------------------------------

    @classmethod
    def create_meeting_point(cls, mp, num=None):
        if num is None:
            cls.meeting_points[mp] = MeetingPoint(len(cls.uavs))
        else:
            if type(num) == list:
                the_mp = MeetingPoint(len(cls.uavs))
                the_mp.target = 0
                for v in num:
                    the_mp.target = the_mp.target | (1 << v)
            else:
                the_mp = MeetingPoint(num)
            cls.meeting_points[mp] = the_mp

    @classmethod
    def get_meeting_point(cls, mp):
        return cls.meeting_points[mp]

    @classmethod
    def create_token(cls, tk):
        cls.tokens[tk] = Token()

    @classmethod
    def get_token(cls, tk):
        return cls.tokens[tk]

    # ---------------------------------------

    @classmethod
    def get_uav(cls, scf):
        uri = scf.cf.link_uri
        if (uri in cls.uavs):
            uav = cls.uavs[uri]
        else:
            uav = UAV()
            cls.uavs[uri] = uav
        uav.set_scf(scf)
        return uav

    @classmethod
    def get_uav_by_id(cls, _id):
        if (_id in cls.uavs_by_id):
            return cls.uavs_by_id[_id]
        else:
            return None

    @classmethod
    def force_landing(cls):
        for k in cls.uavs.keys():
            cls.uavs[k].force_landing = True

    @classmethod
    def reset_estimator(cls, scf):
        cls.get_uav(scf).reset_estimator()

    @classmethod
    def take_off(cls, scf, Z):
        cls.get_uav(scf).take_off(Z)

    @classmethod
    def land(cls, scf):
        cls.get_uav(scf).land()

    @classmethod
    def move(cls, scf, x, y, z):
        cls.get_uav(scf).move(x,y,z)

    @classmethod
    def move_to(cls, scf, x, y, z):
        cls.get_uav(scf).move_to(x,y,z)

    @classmethod
    def rotate_circular(cls, scf, radius, z = None, target_angle = 360, increment = 10):
        cls.get_uav(scf).rotate_circular(radius, z, target_angle, increment)

    # ---- swarm control

    @classmethod
    def run(cls, scf, method, args):
        obj = cls.get_uav(scf)
        meth = getattr(obj, method)
        try:
            meth(*args)
        except:
            traceback.print_exc()

    @classmethod
    def run_swarm(cls, use_remote=True):
        cls.create_meeting_point('__starter__', len(cls.uavs) + 1)
        cflib.crtp.init_drivers(enable_debug_driver=False)
        factory = CachedCfFactory(rw_cache='./cache')
        if use_remote:
            #remote_thread = JoyRemoteController()
            remote_thread = SerialRemoteController()
        with Swarm(cls.uris, factory=factory) as swarm:
            swarm.parallel(cls.reset_estimator)
            try:
                if use_remote:
                    remote_thread.start()
                swarm.parallel(cls._run_all)
            finally:
                swarm.parallel(cls.land)

    @classmethod
    def _run_all(cls, scf):
        obj = cls.get_uav(scf)
        try:
            obj.on_start()
            obj.log('Ready to Start')
            obj.meet('__starter__')
            obj.behave()
        except ForceLandingException:
            obj.land()
        except:
            traceback.print_exc()

    @classmethod
    def args_for_all(cls, args):
        result = { }
        for k in cls.uavs.keys():
            result[k] = args
        return result

    @classmethod
    def args(cls, args):
        result = { }
        for k in cls.uavs.keys():
            result[k] = args[cls.uavs[k].get_id()]
        return result

    # ---- timing
    @classmethod
    def start_timer(cls):
        cls.start_time = time.time()

    @classmethod
    def check_timer(cls, t):
        t = t + cls.start_time
        return time.time() >= t

