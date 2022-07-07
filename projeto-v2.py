from sqlite3 import Timestamp
import tkinter as tk
from tkinter import simpledialog
import cv2
import PIL.Image
import PIL.ImageTk
import time
import datetime as dt
import argparse
import numpy as np
from pymongo import MongoClient
from bson.binary import Binary
from os import startfile, getcwd
import matplotlib.pyplot as plt
import io
import gridfs
from serial import Serial
from requests import post, get
import os
from OsHelper import *


# ! CAMERA 1 (USB DIREITA) SÓ 1 EIXO
# ! CAMERA 2 (USB ESQUERDA DE CIMA) 2 EIXOS

# meu_serial = Serial('COM6', timeout=0.01, baudrate=9600)
texto = 'manual' + '\n'
# meu_serial.write(texto.encode('UTF-8'))

cliente = MongoClient("localhost", 27017)
image_banco = cliente['Im']
video_banco = cliente['Vd']
log_banco = cliente['Log']
icon_vid = cliente['print_vid']
img = gridfs.GridFS(image_banco)
vid = gridfs.GridFS(video_banco)
log = gridfs.GridFS(log_banco)
ico = gridfs.GridFS(icon_vid)

chave = "5509315657:AAHdIY4QS0t_jIqKeBDVtOpgJf02uY3Q20k"
id_da_conversa = "1143595271"
base = "https://api.telegram.org/bot" + chave
endereco = base + "/sendMessage"


def chunks(xs, n):
    n = max(1, n)
    return (xs[i:i+n] for i in range(0, len(xs), n))



class App:
    def __init__(self, window, window_title, video_source=0):
        # comeca deletando o conteudo do diretorio 'dataset'. Fazemos isso para a deteccao facial funcionar corretamente
        clear_dir('dataset')

        # Path for face image database
        self.path = 'dataset'

        self.nomes = ['None']
        # Define min window size to be recognized as a face
        self.minW = 64
        self.minH = 48

        self.recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_detector = cv2.CascadeClassifier(
            'Cascades/haarcascade_frontalface_default.xml')
        self.face_id = 1
        self.face_detector_count = 0

        self.movement_detected = False
        self.window = window
        self.window.title(window_title)
        self.video_source = video_source  # index da camera selecionada
        self.ok = False

        self.esta_dia = True
        self.msg_dia_ou_noite = tk.Label(window, text="")
        self.msg_dia_ou_noite.place(x=10, y=200)

        # timer
        self.timer = ElapsedTimeClock(self.window)

        # open video source (by default this will try to open the computer webcam)
        self.vid = VideoCapture(self.video_source)

        self.number_of_cameras = self.vid.get_amount_of_cameras()

        # self.camera_options == ['camera #0', 'camera #1']
        self.camera_options = [f'camera #{number}' for
                               number in range(self.number_of_cameras)]

        self.selected_camera = tk.StringVar(window)
        self.selected_camera.set(self.camera_options[0])  # default value
        # self.index_camera_selecionada = 0

        # self.previous_selected_camera = tk.StringVar(window)
        # self.previous_selected_camera.set(
        #     self.camera_options[0])  # default value

        print('self.selected_camera =', self.selected_camera.get())

        # videoResolutionHelper = VideoResolutionHelper(self.vid)
        # videoResolutionHelper.make_720p()

        # Create a canvas that can fit the above video source size
        self.canvas = tk.Canvas(
            window, width=self.vid.width, height=self.vid.height)
        self.canvas.pack()

        self.previous_frame = None

        # Button that lets the user take a snapshot
        self.btn_snapshot = tk.Button(
            window, text="FOTO", command=self.snapshot)
        self.btn_snapshot.pack(side=tk.LEFT)

        # video control buttons

        self.btn_start = tk.Button(
            window, text='START', command=self.open_camera)
        self.btn_start.pack(side=tk.LEFT)

        self.btn_stop = tk.Button(
            window, text='STOP', command=self.close_camera)
        self.btn_stop.pack(side=tk.LEFT)

        self.btn_next_camera = tk.Button(
            window, text='PRÓXIMA CAMERA', command=self.next_camera)
        self.btn_next_camera.pack(side=tk.LEFT)

        self.btn_face_detector = tk.Button(
            window, text='INICIAR DETECTOR FACIAL', command=self.inicia_detector_facial)
        self.btn_face_detector.pack(side=tk.LEFT)
        self.btn_face_detector_apertado = False

        self.btn_stop_face_detector = tk.Button(
            window, text='PARAR DETECTOR FACIAL', command=self.para_detector_facial)
        self.btn_stop_face_detector.pack(side=tk.LEFT)
        self.btn_stop_face_detector_apertado = False

        self.option_menu = tk.OptionMenu(
            window, self.selected_camera, *self.camera_options)
        self.option_menu.pack(side=tk.LEFT)

        self.btn_change_to_selected_camera = tk.Button(
            window, text='IR PARA CAMERA SELECIONADA', command=self.change_to_selected_camera)
        self.btn_change_to_selected_camera.pack(side=tk.LEFT)

        # quit button
        self.btn_quit = tk.Button(window, text='QUIT', command=quit, bg='red')
        self.btn_quit.pack(side=tk.RIGHT)

        self.btn_carregar_preferencias = tk.Button(
            window, text="CARREGAR PREFERÊNCIAS", command=self.carregar_preferencias)
        self.btn_carregar_preferencias.pack(side=tk.RIGHT)

        self.btn_salvar_preferencias = tk.Button(
            window, text="SALVAR PREFERÊNCIAS  ", command=self.salvar_preferencias)
        self.btn_salvar_preferencias.pack(side=tk.RIGHT)

        # opcoes para cada camera
        self.camera_atual = tk.Label(text=f'Camera atual: {self.video_source}')
        self.camera_atual.pack(side=tk.TOP)

        self.btn_go_right = tk.Button(
            window, text='Ir para esquerda', command=self.vira_para_esquerda)
        self.btn_go_right.pack(side=tk.TOP)

        self.btn_go_left = tk.Button(
            window, text='Ir para direita', command=self.vira_para_direita)
        self.btn_go_left.pack(side=tk.TOP)

        self.btn_go_left = tk.Button(
            window, text='Ir para cima', command=self.vira_para_cima)
        self.btn_go_left.pack(side=tk.TOP)

        self.btn_go_left = tk.Button(
            window, text='Ir para baixo', command=self.vira_para_baixo)
        self.btn_go_left.pack(side=tk.TOP)

        # **********MENSAGEM DE MOVIMENTO DETECTADO*********
        self.movement_indicator = tk.Label(
            window, text='Detecção de movimento:')
        self.movement_indicator.place(x=1000, y=250)

        self.movement_indicator = tk.Label(
            window, height=1, width=5, bg='grey')
        self.movement_indicator.place(x=1050, y=300)
        # ****************************************

        # saving camera preferences
        self.camera_preferences = [
            {'VARREDURA': 0, 'MOVIMENTO': 0, 'POSICAO': 0}] * self.number_of_cameras
        # fica assim:
        # self.camera_preferences = [{'VARREDURA': False, 'MOVIMENTO': False}, {'VARREDURA': False, 'MOVIMENTO': False}] se tiver 2 cameras por exemplo

        # checkboxes
        self.varredura_is_marked = tk.IntVar()
        self.movimento_is_marked = tk.IntVar()

        self.box_varredura = tk.Checkbutton(
            window, text='Varredura', variable=self.varredura_is_marked, onvalue=1, offvalue=0, command=self.modo_varredura)
        self.box_varredura.pack(side=tk.BOTTOM)

        self.box_movimento = tk.Checkbutton(
            window, text='Detecção de Movimento', variable=self.movimento_is_marked, onvalue=1, offvalue=0, command=self.modo_movimento)
        self.box_movimento.pack(side=tk.BOTTOM)

        # After it is called once, the update method will be automatically called every delay milliseconds
        self.delay = 10
        self.update()

        self.window.mainloop()

    def inicia_detector_facial(self):
        # the input dialog
        USER_INP = simpledialog.askstring(title="Detector facial",
                                          prompt="Digite o seu nome abaixo:")
        # check it out
        print("NOME: ", USER_INP)

        if USER_INP is not None or len(self.nomes) > 1:
            self.nomes.append(USER_INP)
            self.btn_face_detector_apertado = True

    def para_detector_facial(self):
        self.btn_face_detector_apertado = False

    # salva imagem no Banco de Dados
    def salvar_imagem(self, image_path, file_name):
        global saved
        im = PIL.Image.open(image_path)
        image_bytes = io.BytesIO()
        im.save(image_bytes, format='JPEG')

        a = img.put(image_bytes.getvalue(), filename=file_name)

    # abre imagem do banco de dados
    def abrir_imagem(self, filename):
        b = img.put(im.find_one({"filename": filename}))
        out = img.get(b)

        pil_img = PIL.Image.open(io.BytesIO(out.read()))
        fig = plt.imshow(pil_img)
        fig.set_cmap('hot')
        fig.axes.get_xaxis().set_visible(False)
        fig.axes.get_yaxis().set_visible(False)
        plt.show()
        im.delete(b)

    # salva video no banco de dados
    def salvar_video(video_path, file_name):
        video_file = open(video_path, "rb")
        data = video_file.read()
        vid.put(data, filename=file_name)

    # abre video do banco de dados
    def abrir_video(filename):
        b = vid.put(vid.find_one({"filename": filename}))
        out = vid.get(b)
        download_path = getcwd()
        output = open(download_path, "wb")
        output.write(out.read())
        output.close()
        startfile(download_path)
        vid.delete(b)

    # function to get the images and label data

    def getImagesAndLabels(self, path):

        imagePaths = [os.path.join(path, f) for f in os.listdir(path)]
        faceSamples = []
        ids = []

        for imagePath in imagePaths:

            PIL_img = PIL.Image.open(imagePath).convert(
                'L')  # convert it to grayscale
            img_numpy = np.array(PIL_img, 'uint8')

            id = int(os.path.split(imagePath)[-1].split(".")[1])
            faces = self.face_detector.detectMultiScale(img_numpy)

            for (x, y, w, h) in faces:
                faceSamples.append(img_numpy[y:y+h, x:x+w])
                ids.append(id)

        return faceSamples, ids

    def train_face_detector(self):
        print("\n [INFO] Training faces. It will take a few seconds. Wait ...")
        faces, ids = self.getImagesAndLabels(self.path)
        self.recognizer.train(faces, np.array(ids))

        # Save the model into trainer/trainer.yml
        self.recognizer.write('trainer/trainer.yml')
        # recognizer.save() worked on Mac, but not on Pi

        # Print the numer of faces trained and end program
        print("\n [INFO] {0} faces trained. Exiting Program".format(
            len(np.unique(ids))))

    def mandar_aviso(self, path_foto):
        endereco = base + "/sendMessage"
        dados = {"chat_id": id_da_conversa, "text": "Movimento na camera"}
        post(endereco, json=dados)

        endereco = base + "/sendPhoto"
        arquivo = {"photo": open(path_foto, "rb")}
        post(endereco, data=dados, files=arquivo)

    def salvar_evento(date, tipo_evento):
        log.put(b"so_pra_por_algo", filename=date, message=tipo_evento)

    def snapshot(self):
        if not self.esta_dia:
            self.msg_dia_ou_noite.config(text='NÃO É POSSÍVEL FOTOGRAFAR')

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            date = time.strftime("%d-%m-%Y-%H-%M-%S")
            image_file = date + ".jpg"
            cv2.imwrite(image_file, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            self.salvar_imagem("./"+image_file, image_file)

    def snap_movement(self):
        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        if ret:
            date = time.strftime("%d-%m-%Y-%H-%M-%S")
            image_file = date + ".jpg"
            cv2.imwrite(image_file, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            self.salvar_imagem("./"+image_file, image_file)
            self.mandar_aviso("./"+image_file)
            self.salvar_evento(date, "Movimento Detectado")

    def open_camera(self):

        if not self.esta_dia:
            self.msg_dia_ou_noite.config(
                text="NÃO É POSSÍVEL GRAVAR")
            return

        self.msg_dia_ou_noite.config(
            text="")
        self.ok = True
        self.timer.start()
        print("camera opened => Recording")

    def close_camera(self):
        self.ok = False
        self.timer.stop()
        print("camera closed => Not Recording")

    def handle_serial(self):
        texto_recebido = ''
        # texto_recebido = meu_serial.readline().decode().strip()
        if texto_recebido != '':
            print(texto_recebido)

            if texto_recebido == 'noite':
                self.esta_dia = False

            if texto_recebido == 'dia':
                self.esta_dia = True

            if self.movimento_is_marked.get():
                if texto_recebido == 'Movimento detectado':
                    self.movement_indicator.config(bg='red')
                    if (self.movement_detected == False):
                        self.snap_movement()
                        self.movement_detected = True

                elif texto_recebido == 'Sem movimento':
                    self.movement_indicator.config(bg='grey')
                    self.movement_detected = False

    def update(self):
        # serial
        self.handle_serial()

        # Get a frame from the video source
        ret, frame = self.vid.get_frame()

        # **********************************

        if (self.btn_face_detector_apertado):
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self.face_detector.detectMultiScale(gray, 1.3, 5)

            for (x, y, w, h) in faces:

                cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)

                self.face_detector_count += 1

                # Save the captured image into the datasets folder
                cv2.imwrite("dataset/User." + str(self.face_id) +
                            '.' + str(self.face_detector_count) + ".jpg", gray[y:y+h, x:x+w])

                if self.face_detector_count >= 30:  # Take 30 face sample and stop video

                    self.train_face_detector()

                    self.face_id += 1
                    self.face_detector_count = 0
                    self.btn_face_detector_apertado = False
                    break

            # TODO: rosto aqui
            self.recognizer.read('trainer/trainer.yml')
            faces_2 = self.face_detector.detectMultiScale(
                gray,
                scaleFactor=1.2,
                minNeighbors=5,
                minSize=(int(self.minW), int(self.minH)),
            )

            for(x, y, w, h) in faces_2:

                cv2.rectangle(frame, (x, y), (x+w, y+h),
                              (0, 255, 0), 2)

                id, confidence = self.recognizer.predict(
                    gray[y:y+h, x:x+w])

                # Check if confidence is less them 100 ==> "0" is perfect match
                if (confidence < 100):
                    id = self.nomes[id]
                    confidence = "  {0}%".format(
                        round(100 - confidence))
                else:
                    id = "unknown"
                    confidence = "  {0}%".format(
                        round(100 - confidence))

                font = cv2.FONT_HERSHEY_SIMPLEX

                cv2.putText(frame, str(id), (x+5, y-5),
                            font, 1, (255, 255, 255), 2)
                cv2.putText(frame, str(confidence),
                            (x+5, y+h-5), font, 1, (255, 255, 0), 1)

                # cv2.imshow('image', frame)

        # **********************************

        img_rgb = frame
        if self.ok:
            self.vid.out.write(cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            pass
        if ret:
            # img_rgb = cv2.cvtColor(src=img_rgb, code=cv2.COLOR_BGR2RGB)

            prepared_frame = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            prepared_frame = cv2.GaussianBlur(
                src=prepared_frame, ksize=(5, 5), sigmaX=0)

            if (self.previous_frame is None):
                self.previous_frame = prepared_frame
                pass

            previous_frame = self.previous_frame

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

            self.photo = PIL.ImageTk.PhotoImage(
                image=PIL.Image.fromarray(img_rgb))
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)

            self.previous_frame = prepared_frame
        self.window.after(self.delay, self.update)

    def next_camera(self,
                    #   new_video_source
                    ):
        if self.video_source + 1 == self.number_of_cameras:
            self.video_source = 0
        else:
            self.video_source += 1

        self.vid = VideoCapture(self.video_source)

        self.reset_checkboxes()

        # atualiza o label de qual camera esta na tela
        self.camera_atual.config(text=f'Camera atual: {self.video_source}')

        # self.videoResolutionHelper.change_capture(self.video_source)
        # self.videoResolutionHelper.make_720p()

        # self.vid = VideoCapture(new_video_source)

    def change_to_selected_camera(self):
        self.video_source = int(self.selected_camera.get()[-1])
        self.vid = VideoCapture(self.video_source)

        # atualiza o label de qual camera esta na tela
        self.camera_atual.config(text=f'Camera atual: {self.video_source}')

        # TODO: carregar as preferencias da camera selecionada

    def salvar_preferencias(self):
        print('Salvando as preferências...')

        # por enquanto só estou salvando a posição atual da camera

        f = open("preferencias.txt", "w")
        f.write(f'NUMERO DE CAMERAS: {self.number_of_cameras}\n\n')

        for camera_index in range(self.number_of_cameras):
            f.write(f'CAMERA NUMERO {camera_index}\n')
            f.write(
                f'VARREDURA: {self.camera_preferences[camera_index]["VARREDURA"]}\n')
            f.write(
                f'MOVIMENTO: {self.camera_preferences[camera_index]["MOVIMENTO"]}\n')
            f.write(
                f'POSICAO: {self.camera_preferences[camera_index]["POSICAO"]}\n')
            f.write('\n')

        f.close()

    def carregar_preferencias(self):
        print('Carregando preferencias...')

        f = open('preferencias.txt', 'r')
        lines = f.readlines()
        lines = [s.rstrip('\n') for s in lines]

        numero_linhas = int(lines[0][-1])

        lines = [string for string in lines if string !=
                 '' and 'CAMERA' not in string]

        # lines = lines[1:]

        print('lines =', lines)

        number_of_preferences_per_camera = len(self.camera_preferences[0])

        print(self.camera_preferences)

        print('NUMERO DE LINHAS =', numero_linhas)

        # TODO: RESOLVER ISSO AQUI
        preferences_list = list(
            chunks(lines, number_of_preferences_per_camera))

        print('preferences_list =', preferences_list)

        # TODO RESOLVER O CARREGAMENTO
        preferences_dict = dict()
        for value in preferences_list:
            # for value
            print('value =', value)
            print('value[1] =', value[1])
            print('value[1][0] =', value[1][0])
            print('value[1][1] =', value[1][1])
            preferences_dict[value[1][0]] = int(value[1][1])

        print(preferences_dict)

    def vira_para_esquerda(self):
        # TODO
        print('Virando para a esquerda...')

        numero_camera = int(self.selected_camera.get()[-1])
        texto = f'esquerda {numero_camera}' + '\n'

        print(texto)

        # meu_serial.write(texto.encode('UTF-8'))

    def vira_para_direita(self):
        # TODO
        print('Virando para a direita...')

        numero_camera = int(self.selected_camera.get()[-1])
        texto = f'direita {numero_camera}' + '\n'
        # meu_serial.write(texto.encode('UTF-8'))

    def vira_para_cima(self):
        # TODO
        print('Virando para a cima...')

        numero_camera = int(self.selected_camera.get()[-1])
        texto = f'cima {numero_camera}' + '\n'

        # meu_serial.write(texto.encode('UTF-8'))

    def vira_para_baixo(self):
        # TODO
        print('Virando para a baixo...')

        numero_camera = int(self.selected_camera.get()[-1])
        texto = f'baixo {numero_camera}' + '\n'
        # meu_serial.write(texto.encode('UTF-8'))

    def modo_varredura(self):
        # TODO

        print('self.varredura_is_marked.get() =',
              self.varredura_is_marked.get())

        if self.varredura_is_marked.get():
            texto = 'varredura' + '\n'
        else:
            texto = 'manual' + '\n'

        # manda o comando para o arduino pela Serial
        print('Começando modo varredura...', texto)
        # meu_serial.write(texto.encode('UTF-8'))

        # salva na lista de prefrencias que foi marcado
        self.atualiza_preferencias()

    def modo_movimento(self):
        # TODO
        print('Começando modo movimento')

        # salva na lista de prefrencias que foi marcado
        self.atualiza_preferencias()

    def atualiza_preferencias(self):
        self.camera_preferences[self.video_source] = {
            # TODO: mudar esse valor
            'VARREDURA': self.varredura_is_marked.get(), 'MOVIMENTO': self.movimento_is_marked.get(), 'POSICAO': 0
        }
        print(f'Preferências atualizada: {self.camera_preferences}')

    def reset_checkboxes(self):
        self.box_movimento.selection_clear()
        self.box_varredura.selection_clear()


class VideoCapture:
    def __init__(self, video_source=0):
        # Open the video source
        self.vid = cv2.VideoCapture(video_source)
        if not self.vid.isOpened():
            raise ValueError("Unable to open video source", video_source)

        print(f'w = {self.vid.get(cv2.CAP_PROP_FRAME_WIDTH)}')
        print(f'h = {self.vid.get(cv2.CAP_PROP_FRAME_HEIGHT)}')

        # Command Line Parser
        args = CommandLineParser().args

        # create videowriter

        # 1. Video Type
        VIDEO_TYPE = {
            'avi': cv2.VideoWriter_fourcc(*'XVID'),
            # 'mp4': cv2.VideoWriter_fourcc(*'H264'),
            'mp4': cv2.VideoWriter_fourcc(*'XVID'),
        }

        self.fourcc = VIDEO_TYPE[args.type[0]]

        # 2. Video Dimension
        STD_DIMENSIONS = {
            '480p': (640, 480),
            '720p': (1280, 720),
            '1080p': (1920, 1080),
            '4k': (3840, 2160),
        }
        res = STD_DIMENSIONS[args.res[0]]
        print(args.name, self.fourcc, res)
        self.out = cv2.VideoWriter(
            args.name[0]+'.'+args.type[0], self.fourcc, 10, res)

        # set video sourec width and height
        self.vid.set(3, res[0])
        self.vid.set(4, res[1])

        # Get video source width and height
        self.width, self.height = res

    def make_1080p(self):
        self.vid.set(3, 1920)
        self.vid.set(4, 1080)

    def make_720p(self):
        self.vid.set(3, 1280)
        self.vid.set(4, 720)

    def make_480p(self):
        self.vid.set(3, 640)
        self.vid.set(4, 480)

    def change_res(self, width, height):
        self.vid.set(3, width)
        self.vid.set(4, height)

    def change_capture(self, cap):
        self.vid = cap

    def get_amount_of_cameras(self):
        '''Returns int value of available camera devices connected to the host device'''
        camera = 0
        while True:
            if (cv2.VideoCapture(camera).grab()) is True:
                camera = camera + 1
            else:
                cv2.destroyAllWindows()
                return(int(camera))

    # To get frames

    def get_frame(self):
        if self.vid.isOpened():
            ret, frame = self.vid.read()
            if ret:
                # Return a boolean success flag and the current frame converted to BGR
                return (ret, cv2.cvtColor(frame, cv2.COLOR_RGB2BGR))
            else:
                return (ret, None)
        else:
            return (ret, None)

    # Release the video source when the object is destroyed
    def __del__(self):
        if self.vid.isOpened():
            self.vid.release()
            self.out.release()
            cv2.destroyAllWindows()


class ElapsedTimeClock:
    def __init__(self, window):
        self.T = tk.Label(window, text='00:00:00', font=(
            'times', 20, 'bold'), bg='green')
        self.T.pack(fill=tk.BOTH, expand=1)
        self.elapsedTime = dt.datetime(1, 1, 1)
        self.running = 0
        self.lastTime = ''
        t = time.localtime()
        self.zeroTime = dt.timedelta(hours=t[3], minutes=t[4], seconds=t[5])
        # self.tick()

    def tick(self):
        # get the current local time from the PC
        self.now = dt.datetime(1, 1, 1).now()
        self.elapsedTime = self.now - self.zeroTime
        self.time2 = self.elapsedTime.strftime('%H:%M:%S')
        # if time string has changed, update it
        if self.time2 != self.lastTime:
            self.lastTime = self.time2
            self.T.config(text=self.time2)
        # calls itself every 200 milliseconds
        # to update the time display as needed
        # could use >200 ms, but display gets jerky
        self.updwin = self.T.after(100, self.tick)

    def start(self):
        if not self.running:
            self.zeroTime = dt.datetime(1, 1, 1).now()-self.elapsedTime
            self.tick()
            self.running = 1

    def stop(self):
        if self.running:
            self.T.after_cancel(self.updwin)
            self.elapsedTime = dt.datetime(1, 1, 1).now()-self.zeroTime
            self.time2 = self.elapsedTime
            self.running = 0
            date = dt.datetime.now()
            self.salvar_video("./output.mp4", date.strftime("%d-%m-%Y-%H-%M-%S"))


class CommandLineParser:

    def __init__(self):

        # Create object of the Argument Parser
        parser = argparse.ArgumentParser(description='Script to record videos')

        # Create a group for requirement
        # for now no required arguments
        # required_arguments=parser.add_argument_group('Required command line arguments')

        # Only values is supporting for the tag --type. So nargs will be '1' to get
        parser.add_argument('--type', nargs=1, default=[
                            'avi'], type=str, help='Type of the video output: for now we have only AVI & MP4')

        # Only one values are going to accept for the tag --res. So nargs will be '1'
        parser.add_argument('--res', nargs=1, default=[
                            '480p'], type=str, help='Resolution of the video output: for now we have 480p, 720p, 1080p & 4k')

        # Only one values are going to accept for the tag --name. So nargs will be '1'
        ts = dt.datetime.now()
        ts.strftime("%d-%m-%Y-%H-%M-%S")
        parser.add_argument(
            '--name', nargs=1, default=['output'], type=str, help='Enter Output video title/name')

        # Parse the arguments and get all the values in the form of namespace.
        # Here args is of namespace and values will be accessed through tag names
        self.args = parser.parse_args()


def main():
    # Create a window and pass it to the Application object
    App(tk.Tk(), 'Video Recorder')


main()
