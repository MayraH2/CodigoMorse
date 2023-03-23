# -*- coding: utf-8 -*-
import tkinter as tk
import functools as ft
import numpy as np
import pyaudio
import wave
from playsound import playsound
from skimage.transform import rescale, resize, downscale_local_mean
from scipy.io import wavfile
import time
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

#  ___           __            _
# | _ \__ _ _ _ /_/_ _ __  ___| |_ _ _ ___ ___
# |  _/ _` | '_/ _` | '  \/ -_)  _| '_/ _ (_-<
# |_| \__,_|_| \__,_|_|_|_\___|\__|_| \___/__/

paquete = 512  # Tamaño del paquete (512 muestras)
sample = pyaudio.paInt16
canales = 1  # Canales de la tarjeta de audio (Estereo)
fs = 20000  # Frecuencia de muestreo
Ts = 1 / fs
segundos = 10  # Tiempo de audio
factor_escalado = 1 / 19000
umbral_sonido = 0.04
ventana_max = 1300
pausa_letras = 300  # en ms
pausa_palabras = 1000  # en ms

longitud_tr = 20  # longitud_tr del texto_tr mostrado
paquete_tr = 1500  # Tamaño del paquete_tr (1300 muestras)
sample_tr = pyaudio.paInt16
canales_tr = 1  # Canales de la tarjeta de audio
fs_tr = 20000  # Frecuencia de muestreo
Ts_tr = 1 / fs_tr
segundos_tr = 13  # Tiempo de audio
umbral_sonido_tr = 15000
ventana_prom_tr = 1800

hamming = np.array(
    [
        0.080000,
        0.102514,
        0.167852,
        0.269619,
        0.397852,
        0.540000,
        0.682148,
        0.810381,
        0.912148,
        0.977486,
        1.000000,
        0.977486,
        0.912148,
        0.810381,
        0.682148,
        0.540000,
        0.397852,
        0.269619,
        0.167852,
        0.102514,
        0.080000,
    ]
)

pasa_bajas = np.array(
    [
        0.026785,
        0.027705,
        0.028543,
        0.029294,
        0.029955,
        0.030521,
        0.030989,
        0.031356,
        0.031619,
        0.031778,
        0.031831,
        0.031778,
        0.031619,
        0.031356,
        0.030989,
        0.030521,
        0.029955,
        0.029294,
        0.028543,
        0.027705,
        0.026785,
    ]
)

fir = hamming * pasa_bajas
fir = fir / np.max(fir)

#  _        _
# | |   ___| |_ _ _ __ _ ___
# | |__/ -_)  _| '_/ _` (_-<
# |____\___|\__|_| \__,_/__/

biblioteca = {
    # Letras en clave morse
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "CH": "----",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "Ñ": "--.--",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": ".--",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
    # numeros en clave morse
    "0": "-----",
    "1": ".----",
    "2": "..---",
    "3": "...--",
    "4": "....-",
    "5": ".....",
    "6": "-....",
    "7": "--...",
    "8": "---..",
    "9": "----.",
    # Símbolos especiales
    ".": ".-.-.-",
    ",": "-.-.--",
    "?": "..--..",
    '"': ".-..-.",
    "!": "--..--",
}

letras = {
    # letras en clave morse
    ".-": "A",
    "-...": "B",
    "-.-.": "C",
    "----": "CH",
    "-..": "D",
    ".": "E",
    "..-.": "F",
    "--.": "G",
    "....": "H",
    "..": "I",
    ".---": "J",
    "-.-": "K",
    ".-..": "L",
    "--": "M",
    "-.": "N",
    "--.--": "Ñ",
    "---": "O",
    ".--.": "P",
    "--.-": "Q",
    ".-.": "R",
    "...": "S",
    "-": "T",
    "..-": "U",
    "...-": "V",
    ".--": "W",
    "-..-": "X",
    "-.--": "Y",
    "--..": "Z",
    # numeros en clave morse
    "-----": "0",
    ".----": "1",
    "..---": "2",
    "...--": "3",
    "....-": "4",
    ".....": "5",
    "-....": "6",
    "--...": "7",
    "---..": "8",
    "----.": "9",
    # Símbolos especiales
    ".-.-.-": ".",
    "-.-.--": ",",
    "..--..": "?",
    ".-..-.": '"',
    "--..--": "!",
}


#### CLASE DE LA VENTANA PRINCIPAL ##########
class MenuPrincipal(tk.Frame):
    def __init__(self, master=None):
        super().__init__(master, width=1011, height=700)
        self.master = master
        self.pack()
        self.widgets()

    def widgets(self):
        self.imagen1 = tk.PhotoImage(file="img/fondoac.png")
        self.imagen2 = tk.PhotoImage(file="img/oido.png")
        self.imagen3 = tk.PhotoImage(file="img/antena.png")
        self.master.title("Decodificador/Codificador clave morse")
        self.master.resizable(0, 0)
        self.label1 = tk.Label(self, image=self.imagen1)
        self.label1.pack(expand=True, fill="both")
        self.label2 = tk.Label(
            self,
            text="Decodificador/Codificador de clave morse",
            font=("Helvetica", 25, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label2.place(x=100, y=30)
        self.label3 = tk.Label(self, image=self.imagen2)  # imagen de la izquierda
        self.label3.place(x=50, y=200)
        self.label4 = tk.Label(self, image=self.imagen3)  # imagen de la derecha
        self.label4.place(x=810, y=200)
        self.boton1 = tk.Button(
            self,
            text="Decodificar",
            font=("Helvetica", 20, "bold"),
            justify="center",
            height=2,
            width=15,
            borderwidth=8,
            bg="goldenrod",
            command=self.VentanaDos,
        )
        self.boton1.place(x=370, y=200)  # boton para decodificar
        self.boton100 = tk.Button(
            self,
            text="Decodificar (Tiempo real)",
            font=("Helvetica", 20, "bold"),
            justify="center",
            height=2,
            width=20,
            borderwidth=8,
            bg="goldenrod",
            command=self.VentanaTres,
        )
        self.boton100.place(x=330, y=350)  # boton para decodificar 2
        self.boton2 = tk.Button(
            self,
            text="Codificar",
            font=("Helvetica", 20, "bold"),
            justify="center",
            height=2,
            width=15,
            borderwidth=8,
            bg="goldenrod",
            command=self.VentanaUno,
        )
        self.boton2.place(x=370, y=500)  # boton para codificar 2
        self.boton3 = tk.Button(
            self,
            text="Salir",
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=2,
            width=10,
            borderwidth=8,
            bg="goldenrod",
            command=self.master.destroy,
        )  # boton para salir del programa
        self.boton3.place(x=870, y=610)

    def VentanaUno(self):
        self.vent1 = tk.Toplevel(self.master)
        self.vent1.resizable(0, 0)
        self.imagen4 = tk.PhotoImage(file="img/fondoac2.png")
        self.vent1.title("Codificador clave morse")
        self.label5 = tk.Label(self.vent1, image=self.imagen4)
        self.label5.pack(expand=True, fill="both")
        self.label6 = tk.Label(
            self.vent1,
            text="Codificador de clave Morse",
            font=("Helvetica", 30, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label6.place(x=240, y=30)
        self.var1 = tk.StringVar()
        self.entry1 = tk.Entry(self.vent1, textvariable=self.var1)
        self.entry1.place(x=550, y=200, height=100, width=400)
        self.entry1.config(font=("Helvetica", 15, "bold"))
        self.label7 = tk.Label(
            self.vent1,
            text="Escriba la palabra a Codificar",
            font=("Helvetica", 15, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label7.place(x=600, y=150)
        self.label8 = tk.Label(
            self.vent1,
            text="Palabra Codificada",
            font=("Helvetica", 15, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label8.place(x=660, y=400)
        self.entry2 = tk.Text(self.vent1)
        self.entry2.config(font=("Helvetica", 15, "bold"))
        self.entry2.place(x=550, y=450, height=200, width=400)
        self.label9 = tk.Label(
            self.vent1,
            text="Grafica de la palabra Codificada",
            font=("Helvetica", 15, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label9.place(x=120, y=150)
        self.boton4 = tk.Button(
            self.vent1,
            text="Codificar",
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=2,
            width=15,
            borderwidth=8,
            bg="dark orange",
            command=self.Codificar,
        )  # boton para salir del programa
        self.boton4.place(x=680, y=310)
        self.imagen5 = tk.PhotoImage(file="img/icono3.png")
        self.boton5 = tk.Button(
            self.vent1,
            image=self.imagen5,
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=50,
            width=150,
            borderwidth=5,
            command=self.escuchar,
        )
        self.boton5.place(x=200, y=600)
        self.boton6 = tk.Button(
            self.vent1,
            text="Volver",
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=2,
            width=10,
            borderwidth=8,
            bg="goldenrod",
            command=self.vent1.destroy,
        )  # boton para salir del programa
        self.boton6.place(x=50, y=605)

    def escuchar(self):
        n = 1
        self.x = [0]
        self.y = [0]
        for i in range(len(self.codificado)):
            self.recoger = self.codificado[i]
            for j in range(len(self.recoger)):
                self.sonido = self.recoger[j]
                for z in self.sonido:
                    if z == ".":
                        playsound("short.mp3")
                        self.x.append(n)
                        self.y.append(1)
                        self.x.append(n + 1)
                        self.y.append(1)
                        self.x.append(n + 2)
                        self.y.append(0)
                        n += 3
                    elif z == "-":
                        playsound("long.mp3")
                        self.x.append(n + 1)
                        self.y.append(1)
                        self.x.append(n + 2)
                        self.y.append(1)
                        self.x.append(n + 3)
                        self.y.append(1)
                        self.x.append(n + 4)
                        self.y.append(0)
                        n += 4
                time.sleep(0.4)
            time.sleep(0.7)
        self.secundario = tk.Frame(self.vent1)
        self.secundario.place(x=50, y=210, height=350, width=450)
        self.figure = Figure(figsize=(8, 6.05), dpi=58)
        ax = self.figure.add_subplot(1, 1, 1)
        line = FigureCanvasTkAgg(self.figure, self.secundario)
        line.get_tk_widget().place(x=0, y=0)
        ax.clear()
        ax.plot(self.x, self.y), ax.grid(True)
        ax.set_xlabel("$tiempo$"), ax.set_ylabel("$duración$")
        line.draw()

    def Codificar(self):
        self.frase = str(self.var1.get())
        self.palabras = self.frase.split()
        self.codificado = [0] * len(self.palabras)
        self.texto = []
        for i in range(len(self.palabras)):
            self.text = self.palabras[i]
            for j in self.text:
                if j.upper() in biblioteca:
                    self.texto.append(biblioteca[j.upper()])
            self.codificado[i] = self.texto
            self.texto = []
        self.entry2.delete("1.0", "end")
        for z in range(len(self.codificado)):
            self.entry2.insert(
                tk.INSERT, ("{}: {}\n").format(self.palabras[z], self.codificado[z])
            )

    def VentanaDos(self):
        self.vent2 = tk.Toplevel(self.master)
        self.vent2.resizable(0, 0)
        self.imagen6 = tk.PhotoImage(file="img/fondoac2.png")
        self.vent2.title("Decodificador clave morse")
        self.label10 = tk.Label(self.vent2, image=self.imagen6)
        self.label10.pack(expand=True, fill="both")
        self.label11 = tk.Label(
            self.vent2,
            text="Decodificador de clave Morse",
            font=("Helvetica", 30, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label11.place(x=220, y=30)
        self.imagen7 = tk.PhotoImage(file="img/icono4.png")
        self.boton7 = tk.Button(
            self.vent2,
            image=self.imagen7,
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=75,
            width=200,
            borderwidth=3,
            command=self.Grabar,
        )  # boton para salir del programa
        self.boton7.place(x=150, y=150)
        self.boton8 = tk.Button(
            self.vent2,
            text="Volver",
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=2,
            width=10,
            borderwidth=8,
            bg="goldenrod",
            command=self.vent2.destroy,
        )  # boton para salir del programa
        self.boton8.place(x=700, y=600)
        self.label12 = tk.Label(
            self.vent2,
            text="Grafica de sonido",
            font=("Helvetica", 15, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label12.place(x=666, y=100)
        self.label13 = tk.Label(
            self.vent2,
            text="Palabras Decodificadas",
            font=("Helvetica", 15, "bold"),
            bg="DarkGoldenrod3",
        )
        self.label13.place(x=150, y=300)
        # self.secundario=tk.Frame(self.vent2)
        # self.secundario.place(x=840,y=220,height=500, width=700)
        self.deco = tk.Text(self.vent2)
        self.deco.config(font=("Helvetica", 15, "bold"))
        self.deco.place(x=50, y=350, height=300, width=450)
        # self.mensaje=tk.StringVar()
        self.mesage = tk.Label(
            self.vent2,
            text="Presione el boton para grabar y decodificar",
            font=("Helvetica", 15, "bold"),
            bg="DarkGoldenrod3",
        )
        # textvariable=self.mensaje)
        self.mesage.place(x=60, y=100)

    def Grabar(self):
        obj_audio = pyaudio.PyAudio()  # Objeto de audio
        time.sleep(1)
        self.mesage.config(text="Grabacion Iniciada....")
        self.mesage.update()
        streaming = obj_audio.open(
            format=sample,
            channels=canales,
            rate=fs,
            frames_per_buffer=paquete,
            input=True,
        )
        self.tramas = []
        self.sonido = []
        for i in range(0, int(fs / paquete * segundos)):
            self.datos = streaming.read(paquete)
            self.tramas.append(self.datos)
            self.sonido.append(np.frombuffer(self.datos, dtype=np.int16))

        streaming.stop_stream()
        streaming.close()
        obj_audio.terminate()  # Cerrar objeto de audio
        self.mesage.config(text="Grabacion Finalizada")
        self.mesage.update()
        time.sleep(1)
        self.decodificar()

    def VentanaTres(self):
        global t_duracion_tr
        global contador_tr
        global secuencia_tr
        global paquete_tr
        global streaming
        global fir
        global estado_viejo_tr
        global texto_tr
        texto_tr = "                         "
        self.vent3 = tk.Toplevel(self.master)
        self.vent3.resizable(0, 0)
        self.imagen6 = tk.PhotoImage(file="img/fondoac2.png")
        self.vent3.title("Decodificador clave morse en tiempo real")
        self.label101 = tk.Label(self.vent3, image=self.imagen6)
        self.label101.pack(expand=True, fill="both")
        self.foco = tk.Button(self.vent3, text=" ", state="disabled", bg="#400010")
        self.foco.place(x=50, y=195)
        self.tit_1 = tk.Label(
            self.vent3,
            text="Decodificador en tiempo real",
            font=("Helvetica", 30, "bold"),
            bg="DarkGoldenrod3",
        )
        self.tit_1.place(x=160, y=30)
        # boton para salir del programa
        self.boton_sal = tk.Button(
            self.vent3,
            text="Volver",
            font=("Helvetica", 10, "bold"),
            justify="center",
            height=2,
            width=10,
            borderwidth=8,
            bg="goldenrod",
            command=self.vent3.destroy,
        )
        self.boton_sal.place(x=460, y=600)
        self.traduccion = tk.Label(
            self.vent3,
            font=("Courier", 35),
            text="                         ",
        )
        self.traduccion.place(x=50, y=300)
        self.sec_tit = tk.Label(self.vent3, font=("Courier", 30), text="Subsecuencia: ")
        self.sec_tit.place(x=100, y=184)
        self.sec = tk.Label(self.vent3, font=("Courier", 30), text="")
        self.sec.place(x=500, y=184)
        obj_audio_tr = pyaudio.PyAudio()  # Objeto de audio
        streaming_tr = obj_audio_tr.open(
            format=sample_tr,
            channels=canales_tr,
            rate=fs_tr,
            frames_per_buffer=paquete_tr,
            input=True,
        )
        estado_viejo_tr = 0
        t_duracion_tr = 0
        contador_tr = 0
        secuencia_tr = ""

        def loop_grabar_tr(self):
            global t_duracion_tr
            global contador_tr
            global secuencia_tr
            global paquete_tr
            global streaming
            global fir
            global estado_viejo_tr
            global texto_tr
            datos_tr = streaming_tr.read(paquete_tr)
            region_tr = np.frombuffer(datos_tr, dtype=np.int16)
            region_tr = np.hstack(region_tr)  # nos da los datos_tr que necesitamos
            aa_norm_tr = np.abs(region_tr)  # Sacamos valor absoluto de la señal
            suavizada_tr = []
            for i in range(len(aa_norm_tr) - len(fir) - 1):
                suavizada_tr.append(np.dot(aa_norm_tr[i : i + len(fir)], fir))
            maximo = np.max(suavizada_tr)
            estado = maximo >= umbral_sonido_tr  # nos dirá si el máximo pasa el umbral
            # t_duracion_tr += time.time() - t_inicio_tr
            # print(maximo)
            # print(estado)
            # print(t_duracion_tr)
            # print(secuencia_tr)
            # t_inicio_tr = time.time()
            # print(str(estado) + "\t" + str(contador_tr))
            contador_tr += 1
            if estado != estado_viejo_tr:
                if estado == False:
                    if contador_tr <= 2:
                        secuencia_tr = secuencia_tr + "."
                    else:
                        secuencia_tr = secuencia_tr + "-"
                else:
                    if contador_tr > 6:
                        if secuencia_tr in letras:
                            texto_tr = (
                                texto_tr[1 : len(texto_tr)] + letras[secuencia_tr]
                            )
                            secuencia_tr = ""
                        if contador_tr > 12:
                            texto_tr = texto_tr[1 : len(texto_tr)] + " "
                            secuencia_tr = ""
                contador_tr = 0
            else:
                if contador_tr > 6:
                    if secuencia_tr in letras:
                        texto_tr = texto_tr[1 : len(texto_tr)] + letras[secuencia_tr]
                        secuencia_tr = ""
                    if contador_tr > 12:
                        texto_tr = texto_tr[1 : len(texto_tr)] + " "
                        secuencia_tr = ""
                        contador_tr = 0
            estado_viejo_tr = estado
            self.sec.configure(text=secuencia_tr)
            if estado == True:
                self.foco.configure(bg="#FF0000")
            else:
                self.foco.configure(bg="#300010")
            self.traduccion.configure(text=texto_tr)
            # print(
            # activo
            # + " Texto: "
            # + texto_tr
            # + "\t\tSecuencia: "
            # + secuencia_tr
            # + "                     ",
            # end="\r",
            # )
            # print(estado)
            self.vent3.after(1, lambda: loop_grabar_tr(self))

        loop_grabar_tr(self)

    def decodificar(self):
        self.mesage.config(text="Procesando audio.....")
        self.mesage.update()
        self.sonido = np.hstack(self.sonido)
        self.aa_norm = []
        for m in self.sonido:
            self.aa_norm.append(np.sqrt(m ** 2))
        self.aa_norm = np.array(self.aa_norm)
        self.suavizada = []
        for i in range(len(self.aa_norm) - ventana_max - 1):
            self.suavizada.append(np.mean(self.aa_norm[i : i + ventana_max]))
        self.mesage.config(text="Procesando audio.........")
        self.mesage.update()
        self.senial = []
        self.maximos = []
        for i in range(
            0, len(self.suavizada) - ventana_max - 1
        ):  # Seccionando en ventanas de 10ms
            self.max_local = (
                np.max(self.suavizada[i : i + ventana_max]) * factor_escalado
            )  # Normalizada
            self.maximos.append(self.max_local)
            self.senial.append(int(self.max_local >= umbral_sonido))
        self.senial = np.array(self.senial)
        self.mesage.config(text="Procesando audio............")
        self.mesage.update()
        self.secun = tk.Frame(self.vent2)
        self.secun.place(x=520, y=150, height=400, width=480)
        self.figure = Figure(figsize=(8.3, 7), dpi=58)
        ax = self.figure.add_subplot(1, 1, 1)
        line = FigureCanvasTkAgg(self.figure, self.secun)
        line.get_tk_widget().place(x=0, y=0)
        ax.clear()
        ax.plot(self.senial), ax.grid(True)
        ax.set_xlabel("$duracion$"), ax.set_ylabel("$sonido$")
        line.draw()
        self.estado = self.senial[0]
        self.muestras = 0
        self.mesage.config(text="Secuencia recuperada....")
        self.mesage.update()
        self.secuencia = ""
        self.texto_final = ""
        for k in range(1, len(self.senial)):
            self.muestras += 1
            if self.senial[k] != self.senial[k - 1]:
                self.tiempo = self.muestras * Ts * 1000  # ms
                self.muestras = 0
                if self.senial[k - 1]:
                    if self.tiempo <= 150:
                        self.secuencia += "."
                    else:
                        self.secuencia += "-"
                else:
                    if (
                        self.tiempo > pausa_letras
                        and self.secuencia != ""
                        and (self.secuencia in letras)
                    ):
                        # print(secuencia)
                        # print(letras[secuencia], end="")
                        self.texto_final += letras[self.secuencia]
                    if self.tiempo > pausa_letras:
                        self.secuencia = ""
                    if self.tiempo > pausa_palabras:
                        # print(" ", end="")
                        self.texto_final += " "
            if k == len(self.senial) - 1:
                self.tiempo = self.muestras * Ts * 1000  # ms
                self.muestras = 0
                if self.senial[k]:
                    if self.tiempo <= 150:
                        self.secuencia += "."
                    else:
                        self.secuencia += "-"
                else:
                    if (
                        self.tiempo > pausa_letras
                        and self.secuencia != ""
                        and (self.secuencia in letras)
                    ):
                        # print(secuencia)
                        self.texto_final += letras[self.secuencia]
                    if self.tiempo > pausa_letras:
                        self.secuencia = ""
                    if self.tiempo > pausa_palabras:
                        self.texto_final += " "
        self.deco.delete(1.0, "end")
        self.deco.insert("insert", self.texto_final)


raiz = tk.Tk()
prin = MenuPrincipal(raiz)
prin.mainloop()

