from flask import Flask, render_template, Response, redirect
from pymongo import MongoClient
from PIL import Image
from os import startfile, remove, getcwd
import easygui
import cv2
import gridfs
import io
import matplotlib.pyplot as plt

cliente = MongoClient("localhost", 27017)
banco = cliente['PF']
fs = gridfs.GridFS(banco)

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
    data = gen_frames()
    return Response(data, mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/Camera<int:x>')
def camera(x):
    global camera
    camera = cv2.VideoCapture(x-1)
    return render_template('cameras.html')

@app.route('/imagem')
def selecionar_imagem():
    filename = easygui.enterbox("Insira o filename da imagem:")
    return redirect('/imagem/' + filename)

@app.route('/imagem/<string:filename>')
def abrir_imagem(filename):
    b = fs.put(fs.find_one({"filename": filename}))
    out = fs.get(b)

    pil_img = Image.open(io.BytesIO(out.read()))
    fig = plt.imshow(pil_img)
    fig.set_cmap('hot')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.show()
    fs.delete(b)
    return redirect('/')

@app.route('/video')
def selecionar_video():
    filename = easygui.enterbox("Insira o filename do vídeo:")
    return redirect('/video/' + filename)

@app.route('/video/<string:filename>')
def abrir_video(filename):
    b = fs.put(fs.find_one({"filename": filename}))
    out = fs.get(b)
    download_path = getcwd() + '\\teste.mp4'
    output = open(download_path, "wb")
    output.write(out.read())
    output.close()
    startfile(download_path)
    fs.delete(b)
    return redirect('/')

@app.route('/')
def index():
    return render_template('index.html')