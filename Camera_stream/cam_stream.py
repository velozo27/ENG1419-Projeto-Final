from flask import Flask, render_template, Response, redirect
import cv2

app = Flask(__name__)

global camera
camera = cv2.VideoCapture(0)

def gen_frames(camera):
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')  # concat frame one by one and show result
            
@app.route('/video_feed<int:x>')
def video_feed(x):
    #global camera
    camera = cv2.VideoCapture(x)
    data = gen_frames(camera)
    return Response(data, mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def camera_stream():
    return render_template('cameras.html')

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5001)
