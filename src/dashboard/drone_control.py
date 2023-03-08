# Tello documentation: https://djitellopy.readthedocs.io/en/latest/

import _thread
import threading
from djitellopy import Tello
import cv2
import time
import numpy as np
from datetime import datetime
from PIL import Image

class DroneControl():

    def __init__(self):

        print("CREATE DRONE_CONTROL OBJECT")

        # Load default image
        self.DEFAULT_FRAME = Image.open('DEFAULT.jpg')
        self.DEFAULT_BATTERY = -1

        self.is_flying = False
        self.is_connected = False

        self.routine = [
            {'take_off': None},
            {'move_up': 50},
            # {'move_forward': 40},
            # {'rotate_clockwise': 90},
            # {'move_forward': 40},
            # {'rotate_clockwise': 90},
            # {'move_forward': 40},
            # {'rotate_clockwise': 90},
            # {'move_forward': 40},
            # {'rotate_clockwise': 90},
            {'land': None}
        ]
        self.battery_life = self.DEFAULT_BATTERY
        self.drone = Tello()
        self.drone.retry_count = 1
        self._connect()
        self.check_connection()
        self.get_current_state_thread = threading.Thread(target = self.get_current_state, args = (), daemon = True)
        self.get_current_state_thread.start()
        
    def _connect(self):
        try:
            self.drone.connect()
            self.drone.streamoff()
            self.drone.streamon()
            return True
        except:
            return False

    def get_current_frame(self):
        self.check_connection()
        if self.is_connected:
            frame_read = self.drone.get_frame_read()
            frame = frame_read.frame
        else:
            frame = self.DEFAULT_FRAME
            frame = np.asarray(frame)

        # Fallback solution:    
        # try:
        #     frame_read = self.drone.get_frame_read()
        #     frame = frame_read.frame
        # except:
        #     frame = self.DEFAULT_FRAME
        #     frame = np.asarray(frame)
            
        frame = cv2.resize(frame, (640, 480))
        return frame

    def fly_routine(self):
        if self.is_flying:
            return False

        self.is_flying = True

        try:
            for step in self.routine:
                action = list(step.keys())[0]
                direction = step[action]
                if action == 'take_off':
                    self.drone.takeoff()
                elif action == 'move_up':
                    self.drone.move_up(direction)
                elif action == 'rotate_clockwise':
                    self.drone.rotate_clockwise(direction)
                elif action == 'move_forward':
                    self.drone.move_forward(direction)
                elif action == 'move_down':
                    self.drone.move_down(direction)
                else:
                    self.drone.land()
        except:
            try:
                self.drone.land()
            except:
                pass
            self.is_flying = False
            return False

        self.is_flying = False
        time.sleep(15)
        return True
            
    def check_connection(self):
        response = self.drone.send_command_with_return('wifi?')

        try:
            response = str(response)
            if not any(word in response.lower() for word in ('error', 'false', 'warning', 'aborting')):
                self.is_connected = True
                return
        except:
            pass
        self.is_connected = False

    def get_current_state(self):
        while True:
            try:
                self.check_connection()
                self.battery_life = self.drone.get_current_state()['bat']
                time.sleep(3)
            except:
                self.battery_life = self.DEFAULT_BATTERY
                self._connect()
                self.check_connection()
                if not self.is_connected:
                    time.sleep(20)

    def get_battery_life(self):
        date = datetime.today().strftime("%Y-%m-%d")
        return date, self.battery_life