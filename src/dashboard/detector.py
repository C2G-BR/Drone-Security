import serial
import time
import logging
import json
import threading

class Detector():

    def __init__(self):
        logging.basicConfig(filename='logs/detector.log', level=logging.INFO)

        self.motion_detected = False
        self.aware_mode = None

        self._connect()

        self.get_current_state_thread = threading.Thread(target = self.read_current_state, args = (), daemon = True)
        self.get_current_state_thread.start()

    def _connect(self):
        try:
            logging.info('Connecting to Detector')
            self.ser = serial.Serial('COM3', 9600, timeout=1)
            self.ser.reset_input_buffer()
            return True
        except:
            logging.warn('Connecting to Detector failed')
            self.ser = None
            return False

    def read_current_state(self):
        while True:
            try:
                line = self.ser.readline().decode('utf-8').rstrip()
                line = line.split(',')

                if ('motion_detected' in line):
                    self.motion_detected = True
                    logging.info('Motion Detected')
                elif ('motion_not_detected' in line):
                    self.motion_detected = False
                    logging.info('Motion Not Detected')
                else:
                    logging.warning(f'Unknown command from edge device: {line}')
                if ('aware_mode_activated' in line):
                    logging.info('Aware Mode Activated')
                    self.aware_mode = True
                elif ('aware_mode_deactivated' in line):
                    logging.info('Aware Mode Deactivated')
                    self.aware_mode = False
                else:
                    logging.warning(f'Unknown command from edge device: {line}')
                self.ser.flush()
                time.sleep(0.01)
            except:
                self.aware_mode = None
                self.motion_detected = False
                # reset connection
                try:
                    self.ser.close()
                except:
                    pass
                self.ser = None
                connected = self._connect()
                if not connected:
                    time.sleep(20)
    
    def get_detector_state(self):
        return self.aware_mode, self.motion_detected