from pymongo import MongoClient
from PIL import Image
from datetime import datetime
from bson.binary import Binary
from os import startfile, remove, getcwd
import matplotlib.pyplot as plt
import io
import gridfs
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

def salvar_imagem(image_path, file_name):
    im = Image.open(image_path)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='JPEG')
    
    a = img.put(image_bytes.getvalue(), filename=file_name)
    
def salvar_icon(icon_path, file_name):
    im = Image.open(image_path)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='JPEG')
    
    a = ico.put(image_bytes.getvalue(), filename=file_name)
    
def abrir_imagem(filename):
    b = img.put(img.find_one({"filename": filename}))
    out = img.get(b)
    base64_data = codecs.encode(out.read(), 'base64')
    image = base64_data.decode('utf-8')
    img.delete(b)

def salvar_video(video_path, file_name):
    video_file = open(video_path, "rb")
    data = video_file.read()
    vid.put(data, filename=file_name)
    
def abrir_video(filename):
    b = vid.put(vid.find_one({"filename": filename}))
    out = vid.get(b)
    download_path = getcwd()
    output = open(download_path, "wb")
    output.write(out.read())
    output.close()
    startfile(download_path)
    vid.delete(b)
    
def salvar_evento(tipo_evento):
    date = datetime.now()
    str_date = date.strftime("%d/%m/%Y %H:%M")
    log.put(b"so_pra_por_algo", filename=str_date, message=tipo_evento)