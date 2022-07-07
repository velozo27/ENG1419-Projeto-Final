from flask import Flask, render_template, Response, redirect
from pymongo import MongoClient
from PIL import Image
from os import startfile, remove, getcwd
import easygui
import cv2
import gridfs
import io
import matplotlib.pyplot as plt
import requests
import codecs

cliente = MongoClient("localhost", 27017)
imagem = cliente['Im']
video = cliente['Vd']
log_eventos = cliente['Log']
icon_vid = cliente['print_vid']
img = gridfs.GridFS(imagem)
vid = gridfs.GridFS(video)
log = gridfs.GridFS(log_eventos)
ico = gridfs.GridFS(icon_vid)

app = Flask(__name__)

all_vid = []
image_list = []
log_list = []
icon_list = []

global cam_ind



@app.route('/Camera<int:x>')
def select_camera(x):
    cam_ind = x-1
    camera = cv2.VideoCapture(x-1)
    return render_template('cameras.html', cam_ind=cam_ind)  

@app.route('/imagem/<string:filename>')
def abrir_imagem(filename):
    image_list.clear()
    b = img.put(img.find_one({"filename": filename}))
    out = img.get(b)
    base64_data = codecs.encode(out.read(), 'base64')
    imagem = base64_data.decode('utf-8')
    img.delete(b)
    return render_template('imagem_grande.html', imagem=imagem)

@app.route("/imagem")
def abrir_10_imagens():
    image_list.clear()
    for b in img.find().sort("uploadDate", -1).limit(10):
        if b.filename is not None:
            base64_data = codecs.encode(b.read(), 'base64')
            image = base64_data.decode('utf-8')
            image_list.append([image, b.filename])
    
    return render_template('lista_img.html', image_list=image_list)

@app.route('/video')
def abrir_10_icons():
    icon_list.clear()
    for b in ico.find().sort("uploadDate", -1).limit(10):
        if b.filename is not None:
            base64_data = codecs.encode(b.read(), 'base64')
            icon = base64_data.decode('utf-8')
            icon_list.append([icon, b.filename])
    
    return render_template('lista_icon.html', icon_list=icon_list)

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

@app.route('/log')
def exibe_log():
    log_list.clear()
    for b in log.find().sort("uploadDate", -1):
        if b.filename is not None:
            print(b.read())
            log_list.append([b.message, b.filename])
    
    return render_template('lista_log.html', log_list=log_list)
    

@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
      app.run(host='0.0.0.0', port=5000)