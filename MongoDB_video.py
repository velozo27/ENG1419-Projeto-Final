from pymongo import MongoClient
from PIL import Image
from bson.binary import Binary
from os import startfile, remove, getcwd
import matplotlib.pyplot as plt
import io
import gridfs
import codecs

cliente = MongoClient("localhost", 27017)
imagem = cliente['Im']
video = cliente['Vd']
img = gridfs.GridFS(imagem)
vid = gridfs.GridFS(video)

def salvar_imagem(image_path, file_name):
    global saved
    im = Image.open(image_path)
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='JPEG')
    
    a = img.put(image_bytes.getvalue(), filename=file_name)
    
def abrir_imagem(filename):
    b = img.put(img.find_one({"filename": filename}))
    out = img.get(b)
    base64_data = codecs.encode(out.read(), 'base64')
    image = base64_data.decode('utf-8')
    #pil_img = Image.open(io.BytesIO(out.read()))
    #fig = plt.imshow(pil_img)
    #fig.set_cmap('hot')
    #fig.axes.get_xaxis().set_visible(False)
    #fig.axes.get_yaxis().set_visible(False)
    #plt.show()
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
    
salvar_imagem("./minion.jpg", "min")
#salvar_video("C:\\Users\\micro1\\Downloads\\ENG1419-Projeto-Final-main\\ENG1419-Projeto-Final-main\\Camera_stream\\teste.mp4", "aaa")