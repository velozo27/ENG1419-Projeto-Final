# Import required Libraries
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time


#====================== SETUP =========================#

global is_recording, out
is_recording = False

# dimensoes da janela
WIDTH = 800
HEIGHT = 575

# Create an instance of TKinter Window or frame
window = tk.Tk()

# Set the size of the window
window.geometry(f"{WIDTH}x{HEIGHT}")

# Create a Label to capture the Video frames
video_label = tk.Label(window)
video_label.pack()
cap = cv2.VideoCapture(0)

#========================================================#

#====================== FUNCOES DOS BOTOES =========================#


def tira_foto():
    print('tirando foto...')

    foto = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)

    cv2.imwrite("foto-"+time.strftime("%d-%m-%Y-%H-%M-%S") +
                ".jpg", cv2.cvtColor(foto, cv2.COLOR_RGB2BGR))


def grava_video():
    print('gravando vídeo...')
    # Define the codec and create VideoWriter object
    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter('gravacao.avi', fourcc, 20.0, (640, 480))
    print(out)


def vira_para_esquerda():
    # TODO
    print('Virando para a esquerda...')


def vira_para_direita():
    # TODO
    cap.release()
    print('Virando para a direita...')


def modo_varredura():
    # TODO
    print('Começando modo varredura...')
#========================================================#


#====================== BOTOES =========================#
ALUTRA_BOTOES = HEIGHT - 50

botao_foto = tk.Button(window, text="TIRAR FOTO", command=tira_foto)
botao_foto.place(x=350, y=ALUTRA_BOTOES)

botao_salva_video = tk.Button(
    window, text="COMEÇAR GRAVAÇÃO", command=grava_video)
botao_salva_video.place(x=450, y=ALUTRA_BOTOES)

botao_fechar = tk.Button(window, text="FECHAR", command=quit, bg='red')
botao_fechar.place(x=700, y=ALUTRA_BOTOES)

botao_esquerda = tk.Button(
    window, text="VIRAR PARA A ESQUERDA", command=vira_para_esquerda)
botao_esquerda.place(x=50, y=ALUTRA_BOTOES+10-25)

botao_direita = tk.Button(
    window, text="VIRAR PARA A DIREITA      ", command=vira_para_direita)
botao_direita.place(x=50, y=ALUTRA_BOTOES+10)

botao_varredua = tk.Button(
    window, text="MODO VARREDUTA", command=modo_varredura)
botao_varredua.place(x=210, y=ALUTRA_BOTOES)

#========================================================#


def show_frames():
    global out, is_recording

    # funcao que mostra o video na tela
    # eh chamada dentro dela msm atualizando o frame mostrado

    # Get the latest frame and convert into Image
    cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    if is_recording:
        out.write(cv2)
    img = Image.fromarray(cv2image)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # Repeat after an interval to capture continiously
    video_label.after(20, show_frames)


show_frames()
window.mainloop()
