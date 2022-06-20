from requests import post, get

chave = ""
base = "https://api.telegram.org/bot" + chave
endereco = base + "/sendMessage"

def mandar_aviso():
    dados = {"chat_id": id_da_conversa, "text": "Olá!"}
    resposta = post(endereco, json=dados)