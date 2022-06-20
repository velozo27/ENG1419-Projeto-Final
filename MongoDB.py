from pymongo import MongoClient, ASCENDING, DESCENDING
from datetime import datetime, timedelta
from PIL import Image
from bson.binary import Binary
import matplotlib.pyplot as plt
import io

cliente = MongoClient("localhost", 27017)

banco = cliente["Projeto_Final"]
colecao = banco["PF"]

def salvar_dados():
    
    im = Image.open("./image.jpg")
    image_bytes = io.BytesIO()
    im.save(image_bytes, format='JPEG')
    
    tempo = datetime.now()
    texto = tempo.strftime("%d/%m/%Y %H:%M")
    
    dados = {"Data": texto, "Imagem": image_bytes.getvalue()}
    
    colecao.insert_one(dados)
    
def obter_dados():
    busca = {"chave1": valor1, "chave2": {"$gt": valor2}}
    ordenacao = [ ["idade", DESCENDING] ]
    documento = colecao.find_one(busca, sort=ordenacao)
    
    pil_img = Image.open(io.BytesIO(documento['Imagem']))
    plt.imshow(pil_img)
    plt.show()