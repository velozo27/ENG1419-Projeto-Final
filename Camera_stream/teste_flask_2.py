from flask import Flask, render_template, Response, jsonify
import cv2
import time
import threading

app = Flask(__name__)

global camera
global caputre_image

@app.before_first_request
def camera_thread():
    def gen_frames():
        global capture_image
        while capture_image:
            success, frame = camera.read()  # read the camera frame
            if not success:
                break
            else:
                ret, buffer = cv2.imencode('.jpg', frame)
                frame = buffer.tobytes()
                yield (b'--frame\r\n'
                       b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
    thread = threading.Thread()
    thread.start()
           
@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Camera<int:x>')
def camera(x):
    capture_image = True
    global camera
    camera = cv2.VideoCapture(x-1)
    return render_template('cameras.html')

@app.route('/')
def index():
    capture_image = False
    return render_template('index.html')