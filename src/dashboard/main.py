from flask import Flask, request, render_template, Response, redirect, url_for
from dotenv import load_dotenv
from PIL import Image
from detector import Detector
from drone_control import DroneControl
import numpy as np
import time
import json
import os
import io
import torch
import warnings


warnings.filterwarnings('ignore')

load_dotenv()

app = Flask(__name__)

app.config['SECRET_KEY']=os.getenv('SECRET_KEY')
app.config['ADMIN_USERNAME']=os.getenv('ADMIN_USERNAME')
app.config['ADMIN_PASSWORD']=os.getenv('ADMIN_PASSWORD')


model = torch.hub.load('yolov5', 'custom', path='yolov5s.pt', source='local')
model.classes = [0] #only humans

drone = DroneControl()
detector = Detector()

fly = True

def get_activation_state():
    start_flight = False
    while True:
        aware_mode, motion_detected = detector.get_detector_state()
        current_state = ''

        if aware_mode:
            current_state += 'You are absent.'
            if motion_detected:
                current_state += '\n\n'
                current_state += 'Motion was detected.'
                if fly:
                    start_flight = True
                    current_state += '\n\n'
                    current_state += 'Drone is flying.'
        elif not aware_mode:
            current_state += 'You are at home.'
        else:
            current_state += 'Connection Error'
        
        json_data = json.dumps({'current_state': current_state})
        yield f"data:{json_data}\n\n"

        # start flight if all conditions are met
        if start_flight:
            start_flight = False
            flight_result = drone.fly_routine()
            print("FLIGHT RESULT", flight_result)

        time.sleep(0.1)

def get_video_stream():
    time.sleep(3)

    while True:        

        frame = drone.get_current_frame()

        result = model(frame)
        result = np.asarray(result.render()[0])
        result = Image.fromarray(result)

        img_byte_arr = io.BytesIO()
        result.save(img_byte_arr, format='jpeg') # save image to variable as jpeg
        img_byte_arr = img_byte_arr.getvalue() # get bytes

        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + img_byte_arr + b'\r\n')
        time.sleep(0.15)

def get_energy_level():
    while True:
        date, value = drone.get_battery_life() 
        json_data = json.dumps({'date': date, 'value': value})
        yield f"data:{json_data}\n\n"
        time.sleep(3)

def valid_login(username:str, password:str):
    return (username == app.config.get('ADMIN_USERNAME')) and (password == app.config.get('ADMIN_PASSWORD'))

@app.route('/')
def index():
    return render_template('dashboard.html', labels=[], values=[])

@app.route('/login', methods=['POST', 'GET'])
def login():
    error = None
    if request.method == 'POST':
        username = request.form['username']
        if valid_login(username, request.form['password']):
            return redirect(url_for('index'))
        else:
            error = 'Invalid username/password'
    return render_template('login.html', error=error)

@app.route('/video-feed', methods=['GET'])
def video_feed():
    return Response(get_video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/energy-feed', methods=['GET'])
def energy_feed():
    return Response(get_energy_level(), mimetype='text/event-stream')

@app.route('/activation-feed', methods=['GET'])
def activiation_feed():
    return Response(get_activation_state(), mimetype='text/event-stream')

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True, use_reloader=False)