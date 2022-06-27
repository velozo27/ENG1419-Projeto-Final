from pymongo import MongoClient
from datetime import datetime
from PIL import Image
from bson.binary import Binary
from os import startfile, remove, getcwd
import matplotlib.pyplot as plt
import io
import gridfs

cliente = MongoClient("localhost", 27017)
banco = cliente['PF']
fs = gridfs.GridFS(banco)

def salvar_imagem(image_path, file_name):
    global saved
    im = Image.open(image_path)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='JPEG')
    
    a = fs.put(image_bytes.getvalue(), filename=file_name)
    
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

def salvar_video(video_path, file_name):
    video_file = open(video_path, "rb")
    data = video_file.read()
    fs.put(data, filename=file_name)
    
def abrir_video(filename):
    b = fs.put(fs.find_one({"filename": filename}))
    out = fs.get(b)
    download_path = getcwd()
    output = open(download_path, "wb")
    output.write(out.read())
    output.close()
    startfile(download_path)
    fs.delete(b)
    
salvar_imagem("./minion.jpg", "minions")
abrir_imagem("minions")
salvar_video("C:\\Users\\thice\\Videos\\Captures\\aaa.mp4", "aaa")
abrir_video("aaa")