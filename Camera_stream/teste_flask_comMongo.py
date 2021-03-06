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
imagem = cliente['Im']
video = cliente['Vd']
img = gridfs.GridFS(imagem)
vid = gridfs.GridFS(video)

app = Flask(__name__)

all_img = []
all_vid = []

global camera

def gen_frames():
    while True:
        success, frame = camera.read()  # read the camera frame
        if not success:
            print("aaaaa")
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

@app.route('/imagem')
def selecionar_imagem():
    #filename = easygui.enterbox("Insira o filename da imagem:")
    for grid_out in img.find():
        all_img.append(grid_out.filename)
        
        
    return render_template('lista_img.html', all_img=all_img)    
    #return redirect('/imagem/' + filename)

@app.route('/imagem/<string:filename>')
def abrir_imagem(filename):
    b = img.put(img.find_one({"filename": filename}))
    out = img.get(b)

    pil_img = Image.open(io.BytesIO(out.read()))
    fig = plt.imshow(pil_img)
    fig.set_cmap('hot')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.show()
    img.delete(b)
    all_img.clear()
    return redirect('/')

@app.route('/video')
def selecionar_video():
    for grid_out in vid.find():
        all_vid.append(grid_out.filename)
        
        
    return render_template('lista_vid.html', all_vid=all_vid)

@app.route('/video/<string:filename>')
def abrir_video(filename):
    b = vid.put(vid.find_one({"filename": filename}))
    out = vid.get(b)
    download_path = getcwd() + '\\teste.mp4'
    output = open(download_path, "wb")
    output.write(out.read())
    output.close()
    startfile(download_path)
    vid.delete(b)
    all_vid.clear()
    return redirect('/')

@app.route('/')
def index():
    return render_template('index.html')