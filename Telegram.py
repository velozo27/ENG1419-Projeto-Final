from requests import post, get

chave = "5509315657:AAHdIY4QS0t_jIqKeBDVtOpgJf02uY3Q20k"
id_da_conversa = "1143595271"
base = "https://api.telegram.org/bot" + chave
endereco = base + "/sendMessage"

def mandar_aviso(path_foto):
    endereco = base + "/sendMessage"
    dados = {"chat_id": id_da_conversa, "text": "Movimento na camera"}
    post(endereco, json=dados)
    
    endereco = base + "/sendPhoto"
    arquivo = {"photo": open(path_foto, "rb")}
    post(endereco, data=dados, files=arquivo)
    

#mandar_aviso("imagem.jpg")