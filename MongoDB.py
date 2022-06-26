from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime
from PIL import Image
from bson.binary import Binary
import matplotlib.pyplot as plt
import io

cliente = MongoClient("localhost", 27017)
banco = cliente["Projeto_Final"]
colecao = banco["PF"]

def salvar_imagem():
    
    im = Image.open("./imagem.jpg")
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='JPEG')
    
    tempo = datetime.now()
    texto = tempo.strftime("%d/%m/%Y %H:%M")
    
    dados = {"Data": texto, "Imagem": image_bytes.getvalue()}
    
    colecao.insert_one(dados)
    
def obter_imagem():
    #busca = {"chave1": valor1, "chave2": {"$gt": valor2}}
    #ordenacao = [ ["Data", DESCENDING] ]
    documento = colecao.find_one()
    
    pil_img = Image.open(io.BytesIO(documento['Imagem']))
    fig = plt.imshow(pil_img)
    fig.set_cmap('hot')
    fig.axes.get_xaxis().set_visible(False)
    fig.axes.get_yaxis().set_visible(False)
    plt.show()
    
salvar_imagem()