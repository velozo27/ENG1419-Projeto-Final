# Import required Libraries
from curses import baudrate
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time
from serial import Serial


#====================== SETUP =========================#

global is_recording, out, camera_index, cap1, cap2
is_recording = False
out = None
camera_index = 0  # diz qual camera estamos vendo
# cap = cv2.VideoCapture(camera_index)
cap1 = cv2.VideoCapture(0)
cap2 = cv2.VideoCapture(1)

# Serial
meu_serial = Serial("COM3", baudrate=9600)

# dimensoes da janela
WIDTH = 850
HEIGHT = 575

# Create an instance of TKinter Window or frame
window = tk.Tk()

# Set the size of the window
window.geometry(f"{WIDTH}x{HEIGHT}")

# Create a Label to capture the Video frames
video_label = tk.Label(window)
video_label.pack()

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


def mudar_camera():
    global camera_index, cap

    print('Mudando a camera...')

    # cap.release()

    # PARA TESTES
    ########################
    if camera_index == 0:
        camera_index = 1
    else:
        camera_index = 0
    ########################

    # cap.release()
    # cv2.destroyAllWindows()

    # mudando a camera
    # cap = cv2.VideoCapture(camera_index)

    # mostrando a camera nova na tela
    show_frames()


def vira_para_esquerda():
    # TODO
    print('Virando para a esquerda...')
    texto = 'esquerda' + '\n'
    meu_serial.write(texto.encode('UTF-8'))


def vira_para_direita():
    # TODO
    print('Virando para a direita...')
    texto = 'direita' + '\n'
    meu_serial.write(texto.encode('UTF-8'))


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
botao_fechar.place(x=750, y=ALUTRA_BOTOES)

botao_esquerda = tk.Button(
    window, text="VIRAR PARA A ESQUERDA", command=vira_para_esquerda)
botao_esquerda.place(x=50, y=ALUTRA_BOTOES+10-25)

botao_direita = tk.Button(
    window, text="VIRAR PARA A DIREITA      ", command=vira_para_direita)
botao_direita.place(x=50, y=ALUTRA_BOTOES+10)

botao_varredua = tk.Button(
    window, text="MODO VARREDUTA", command=modo_varredura)
botao_varredua.place(x=210, y=ALUTRA_BOTOES)

botao_mudar_camera = tk.Button(
    window, text="MUDAR CAMERA", command=mudar_camera)
botao_mudar_camera.place(x=600, y=ALUTRA_BOTOES)

#========================================================#

#======================= FUNCOES RELACIONADAS A CAMERA E VIDEO ===============================#


def show_frames():
    global out, is_recording, cap1, cap2, camera_index

    print('to aqui: ', camera_index)

    if camera_index == 0:
        cv2image = cv2.cvtColor(cap1.read()[1], cv2.COLOR_BGR2RGB)
    else:
        cv2image = cv2.cvtColor(cap2.read()[1], cv2.COLOR_BGR2RGB)

    # funcao que mostra o video na tela
    # eh chamada dentro dela msm atualizando o frame mostrado

    # Get the latest frame and convert into Image
    # if is_recording:
    #     out.write(cv2)

    img = Image.fromarray(cv2image)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    # Repeat after an interval to capture continiously
    video_label.after(20, show_frames)


def get_amount_of_cameras():
    '''Returns int value of available camera devices connected to the host device'''
    camera = 0
    while True:
        if (cv2.VideoCapture(camera).grab()) is True:
            camera = camera + 1
        else:
            cv2.destroyAllWindows()
            return(int(camera))


show_frames()
window.mainloop()
