"""
DESCRIPTION TODO
"""

import serial
import logging
logging.basicConfig(filename='logs/detector.log', level=logging.INFO)

drone_started = False

if __name__ == '__main__':
    ser = serial.Serial('COM3', 9600, timeout=1)
    ser.reset_input_buffer()
    while True:
        line = ser.readline().decode('utf-8').rstrip()
        if (line == 'motion_detected'):
            logging.info('Motion Detected')
            if not (drone_started):
                drone_started = True
        else:
            logging.warning(f'Unknown command from edge device: {line}')
        ser.flush()