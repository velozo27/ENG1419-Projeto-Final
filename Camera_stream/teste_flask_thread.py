from flask import Flask, render_template, Response
import cv2
import threading

app = Flask(__name__)

global camera

def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result

@app.route('/video_feed')
def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Camera<int:x>')
def camera(x):
    global camera
    camera = cv2.VideoCapture(x-1)
    return render_template('cameras.html')

@app.route('/')
def index():
    return render_template('index.html')
