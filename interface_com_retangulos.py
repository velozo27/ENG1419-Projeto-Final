# Import required Libraries
import tkinter as tk
from PIL import Image, ImageTk
import cv2
import time
import numpy as np
from serial import Serial
from VideoResolutionHelper import VideoResolutionHelper


#====================== SETUP =========================#

global is_recording, out, camera_index, cap, previous_frame, angulo_servo, avisar_movimento
previous_frame = None
is_recording = False
out = None
avisar_movimento = False

camera_index = 0  # diz qual camera estamos vendo
cap = cv2.VideoCapture(camera_index)
# cap = cv2.VideoCapture(camera_index, cv2.CAP_DSHOW)
videoResolutionHelper = VideoResolutionHelper(cap)
# setting the video capture definition
videoResolutionHelper.make_720p()

angulo_servo = 0

# dimensoes da janela
WIDTH = 1200
HEIGHT = 750

# Serial
# meu_serial = Serial("COM3", baudrate=9600)

# Create an instance of TKinter Window or frame
window = tk.Tk()

# Set the size of the window
window.geometry(f"{WIDTH}x{HEIGHT}")

# Create a Label to capture the Video frames
video_label = tk.Label(window)
video_label.config(width=1000, height=650)
video_label.pack()

# funcao auxiliar para centralizar a interface na tela


def center_window(width=WIDTH, height=HEIGHT):
    # get screen width and height
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()

    # calculate position x and y coordinates
    x = (screen_width/2) - (width/2)
    y = (screen_height/2) - (height/2)
    window.geometry('%dx%d+%d+%d' % (width, height, x, y - 50))

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

    # PARA TESTES
    ########################
    if camera_index == 0:
        camera_index = 1
    else:
        camera_index = 0
    ########################

    # mudando a camera
    cap = cv2.VideoCapture(camera_index)

    # mostrando a camera nova na tela
    show_frames()


def vira_para_esquerda():
    # TODO
    print('Virando para a esquerda...')
    texto = 'esquerda' + '\n'
    # meu_serial.write(texto.encode('UTF-8'))


def vira_para_direita():
    # TODO
    print('Virando para a direita...')
    texto = 'direita' + '\n'
    # meu_serial.write(texto.encode('UTF-8'))


def modo_varredura():
    # TODO
    print('Começando modo varredura...')
    texto = 'esquerda' + '\n'
    # meu_serial.write(texto.encode('UTF-8'))


def salvar_preferencias():
    # TODO: ver que preferencias salvar: posicao da camera por exemplo
    print('Salvando as preferências...')

    # por enquanto só estou salvando a posição atual da camera
    f = open("preferencias.txt", "w")
    f.write(str(angulo_servo) + "\n")
    f.close()


def carregar_preferencias():
    global angulo_servo
    # TODO
    print('Carregando as preferências...')

    # lendo o angulo de servo e alterando o seu valor
    f = open("preferencias.txt", "r")
    data = f.read()
    angulo_servo = data[0]
    texto = 'direita' + '\n'
    # meu_serial.write(texto.encode('UTF-8'))


def modo_avisar_movimento():
    global avisar_movimento
    avisar_movimento = not avisar_movimento


#========================================================#


#====================== BOTOES =========================#
ALUTRA_BOTOES = HEIGHT - 50

botao_foto = tk.Button(window, text="TIRAR FOTO", command=tira_foto)
botao_foto.place(x=350, y=ALUTRA_BOTOES)

botao_salva_video = tk.Button(
    window, text="COMEÇAR GRAVAÇÃO", command=grava_video)
botao_salva_video.place(x=450, y=ALUTRA_BOTOES)

botao_fechar = tk.Button(window, text="FECHAR", command=quit, bg='red')
botao_fechar.place(x=WIDTH - 100, y=ALUTRA_BOTOES)

botao_esquerda = tk.Button(
    window, text="VIRAR PARA A ESQUERDA", command=vira_para_esquerda)
botao_esquerda.place(x=50, y=ALUTRA_BOTOES-15)

botao_direita = tk.Button(
    window, text="VIRAR PARA A DIREITA      ", command=vira_para_direita)
botao_direita.place(x=50, y=ALUTRA_BOTOES+10)

botao_varredua = tk.Button(
    window, text="MODO VARREDUTA", command=modo_varredura)
botao_varredua.place(x=210, y=ALUTRA_BOTOES)

botao_mudar_camera = tk.Button(
    window, text="MUDAR CAMERA", command=mudar_camera)
botao_mudar_camera.place(x=600, y=ALUTRA_BOTOES)


botao_salvar_preferencias = tk.Button(
    window, text="SALVAR PREFERÊNCIAS  ", command=salvar_preferencias)
botao_salvar_preferencias.place(x=720, y=ALUTRA_BOTOES-15)

botao_salvar_preferencias = tk.Button(
    window, text="CARREGAR PREFERÊNCIAS", command=carregar_preferencias)
botao_salvar_preferencias.place(x=720, y=ALUTRA_BOTOES+10)

botao_salvar_preferencias = tk.Button(
    window, text="AVISAR MOVIMENTO", command=modo_avisar_movimento)
botao_salvar_preferencias.place(x=900, y=ALUTRA_BOTOES)

#========================================================#

#======================= TEXTOS NA TELA =======================#

texto_movimento_na_tela = tk.Label(window, text='')
texto_movimento_na_tela.place(x=900, y=ALUTRA_BOTOES-40)

#==============================================================#


#======================= MENU BAR ===============================#

# create a menubar
menubar = tk.Menu(window)
window.config(menu=menubar)

# create a menu
file_menu = tk.Menu(menubar, tearoff=False)

# add a menu item to the menu
file_menu.add_command(
    label='Fechar',
    command=window.destroy
)

# add the File menu to the menubar
menubar.add_cascade(
    label="Arquivo",
    menu=file_menu
)

#========================================================#

#======================= FUNCOES RELACIONADAS A CAMERA E VIDEO ===============================#


def show_frames():
    global out, is_recording, cap, previous_frame, angulo_servo

    # funcao que mostra o video na tela
    # eh chamada dentro dela msm atualizando o frame mostrado

    # Get the latest frame and convert into Image
    #cv2image = cv2.cvtColor(cap.read()[1], cv2.COLOR_BGR2RGB)
    _, img_rgb = cap.read()

    img_rgb = cv2.cvtColor(src=img_rgb, code=cv2.COLOR_BGR2RGB)

    prepared_frame = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
    prepared_frame = cv2.GaussianBlur(
        src=prepared_frame, ksize=(5, 5), sigmaX=0)

    if (previous_frame is None):
        previous_frame = prepared_frame
        pass

    diff_frame = cv2.absdiff(src1=previous_frame, src2=prepared_frame)
    previous_frame = prepared_frame

    kernel = np.ones((5, 5))
    diff_frame = cv2.dilate(diff_frame, kernel, 1)

    thresh_frame = cv2.threshold(
        src=diff_frame, thresh=20, maxval=255, type=cv2.THRESH_BINARY)[1]

    contours, _ = cv2.findContours(
        image=thresh_frame, mode=cv2.RETR_EXTERNAL, method=cv2.CHAIN_APPROX_SIMPLE)

    for contour in contours:
        if cv2.contourArea(contour) < 500:
          # too small: skip!
            pass
        (x, y, w, h) = cv2.boundingRect(contour)
        if (w > 200 or h > 200):
            # print(x, y, w, h)
            cv2.rectangle(img=img_rgb, pt1=(x, y), pt2=(
                x + w, y + h), color=(0, 255, 0), thickness=2)

    if is_recording:
        out.write(cv2)

    img = Image.fromarray(img_rgb)
    # Convert image to PhotoImage
    imgtk = ImageTk.PhotoImage(image=img)
    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)

    #================ Serial ==================#

    # texto_recebido = meu_serial.readline().decode().strip()
    # if texto_recebido is not None:
    #     # Servo 1: 90Servo 2: 90
    #     print(texto_recebido)

    #     # angulo_servo = int(texto_recebido.split()[-1])
    #     print(angulo_servo)
    #======================================================#

    #================ Sensor de Movimento =================#
    # ideia:
    # https://create.arduino.cc/projecthub/biharilifehacker/arduino-with-pir-motion-sensor-fd540a
    # usar o sensor de movimento pelo arduino e pegar pela serial se teve moviemento
    # se sim (e o modo de avisar_movimento estivar verdadeiro) avisar com uma messagebox

    # TODO: esse if para olhar a serial
    if avisar_movimento:
        if True:  # aqui botar a serial, algo como 'if texto_recebido == "movimento"'
            texto_movimento_na_tela.config(text='Movimento Detectado!')
    else:
        texto_movimento_na_tela.config(text='')

    #======================================================#

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
center_window(WIDTH, HEIGHT)
window.mainloop()
