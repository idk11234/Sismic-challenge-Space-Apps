import tkinter as tk 
import numpy as np
from tkinter import filedialog
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from obspy import read
import pandas as pd
import os 

from obspy.signal.invsim import cosine_taper
from obspy.signal.filter import highpass
from obspy.signal.trigger import classic_sta_lta, plot_trigger, trigger_onset
from scipy import signal
from matplotlib import cm
from obspy.signal.invsim import cosine_taper
from obspy.signal.filter import highpass
from obspy.signal.trigger import classic_sta_lta, plot_trigger, trigger_onset
from scipy.signal import butter,lfilter, freqz


#Creacion de la aplicación 
app = tk.Tk()

app.title("Sismos")

#Figura 1
tiempo = np.linspace(0, 1, 1000)  # Tiempo de 0 a 1 segundo
amplitud = np.sin(2 * np.pi * 50 * tiempo) + np.random.normal(0, 0.5, tiempo.shape)

fig1, ax1 = plt.subplots(figsize=(4, 2))
ax1.plot(tiempo, amplitud)  # Datos de ejemplo
ax1.set_title("Señal de tiempo")
ax1.set_xlabel("Tiempo (s)")
ax1.set_ylabel("Amplitud")

#Figura 2
fig2, ax2 = plt.subplots(figsize=(4, 2))
Pxx, freqs, bins, im = ax2.specgram(amplitud, NFFT=256, Fs=1000, noverlap=128, cmap='viridis')
ax2.set_title("Espectrograma")
ax2.set_xlabel("Tiempo (s)")
ax2.set_ylabel("Frecuencia (Hz)")



#Frame para contener las graficas 
frame_graficas = tk.Frame(app)

canvas2 = FigureCanvasTkAgg(fig2, master=frame_graficas)
canvas1 = FigureCanvasTkAgg(fig1, master=frame_graficas)

#Función para cambiar imagenes 
def btn_luna_function():
    # if seleccion.get() == "Luna":
    #     imagen = Image.open("imagenes\luna.png") #Ruta de la imagen de la Luna
    # else:
    #     imagen = Image.open("imagenes\marte.png")#Ruta de la imagen de  Marte
    imagen = Image.open("imagenes\luna.png") #Ruta de la imagen de la Luna
    imagen = imagen.resize((200,200)) #Redimiensionar la imagen 
    photo = ImageTk.PhotoImage(imagen)

    label_imagen.config(image=photo)
    label_imagen.image = photo

    carpeta_inicial = "space_apps_2024_seismic_detection\space_apps_2024_seismic_detection\data\lunar"  # Cambia a la ruta de tu carpeta específica

    # Abrir la ventana para seleccionar un archivo CSV
    archivo_seleccionado = filedialog.askopenfilename(initialdir=carpeta_inicial, title="Selecciona un archivo CSV",filetypes=[("Archivos CSV", "*.csv"),("Archivos MINISEED","*.mseed")])
    # Si se seleccionó un archivo, mostrar su nombre
    if archivo_seleccionado:
        pipe(leer(archivo_seleccionado),ax1,ax2)
        # canvas2.get_tk_widget().delete("all")     
        # canvas1.get_tk_widget().delete("all")

        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0)
        #Canvas 2

        canvas2.draw()
        canvas2.get_tk_widget().grid(row=0, column=10)
        frame_graficas.pack(pady=20)
        print(seleccion)



def btn_marte_function():
    imagen = Image.open("imagenes\marte.png") #Ruta de la imagen de la Luna
    imagen = imagen.resize((200,200)) #Redimiensionar la imagen 
    photo = ImageTk.PhotoImage(imagen)

    label_imagen.config(image=photo)
    label_imagen.image = photo
    carpeta_inicial = "space_apps_2024_seismic_detection\space_apps_2024_seismic_detection\data\mars"  # Cambia a la ruta de tu carpeta específica

    # Abrir la ventana para seleccionar un archivo CSV
    archivo_seleccionado = filedialog.askopenfilename(initialdir=carpeta_inicial, title="Selecciona un archivo CSV",filetypes=[("Archivos CSV", "*.csv"),("Archivos MINISEED","*.mseed")])
    # Si se seleccionó un archivo, mostrar su nombre
    if archivo_seleccionado:
        nombre_archivo = archivo_seleccionado.split('/')[-1]  # Obtener solo el nombre del archivo
        seleccion=f"Archivo seleccionado: {nombre_archivo}"
        print("hbbkj" + archivo_seleccionado)
        pipe(leer(archivo_seleccionado),ax1,ax2)

        # canvas2.get_tk_widget().delete("all")     
        # canvas1.get_tk_widget().delete("all")

        canvas1.draw()
        canvas1.get_tk_widget().grid(row=0, column=0)
        #Canvas 2

        canvas2.draw()
        canvas2.get_tk_widget().grid(row=0, column=10)
        frame_graficas.pack(pady=20)
        print(seleccion)

def leer(file):
        filename = os.fsdecode(file)
        if filename.endswith(".mseed"): 

            mseed = read(filename)

            dict = {
                "sample_rate": mseed[0].stats.sampling_rate,
                "time": mseed.traces[0].copy().times(),
                "data": mseed.traces[0].copy().data
            }

            print(dict["sample_rate"])

            return dict

        if filename.endswith(".csv"): 

            csv = pd.read_csv(filename)

            time = csv.iloc[:,1].to_numpy()
            total_time = time[-1]


            dict = {
                "sample_rate": (len(time))/total_time,
                "time": time,
                "data": csv.iloc[:,2].to_numpy()
            }

            

            return dict
        

def butter_lowpass(data, cutoff, fs, order=5):
  nyq=0.5*fs #Frecuencia de Nyquist
  normal_cutoff = cutoff/nyq #Frecuencia normalizada 
  b,a = butter(order, normal_cutoff, btype='low', analog=False)
  y=lfilter(b,a,data)
  return y

def pipe(data,ax,ax2):
    minfreq = 0.5
    maxfreq = 1.0
    sta_len = 120
    lta_len = 600
    thr_on = 4
    thr_off = 1.5
    
    ret = []
    for mseed in data:

        df = data["sample_rate"]

        tr_times = data["time"]
        tr_data =  data["data"]

        print(tr_data)

        f, t, sxx = signal.spectrogram(tr_data, df)

        tr_data = butter_lowpass(tr_data, 0.6, df)
        
        cft = classic_sta_lta(tr_data, int(sta_len * df), int(lta_len * df))

        on_off = np.array(trigger_onset(cft, thr_on, thr_off))
    
        # Plot the time series and spectrogram
        ax.clear()
        ax2.clear()
# Plot trace
        ax.plot(tr_times,tr_data)

# Mark detection
        for i in np.arange(0,len(on_off)):
            triggers = on_off[i]
            ax.axvline(x = tr_times[triggers[0]], color='red', label='Trig. On')
# Make the plot pretty
        ax.set_xlim([min(tr_times),max(tr_times)])
        ax.set_ylabel('Velocity (m/s)')
        ax.set_xlabel('Time (s)')

        vals = ax2.pcolormesh(t, f, sxx, cmap=cm.jet)
        print(min(tr_times))
        print(max(tr_times))
        ax2.set_xlim([min(tr_times),max(tr_times)])
        ax2.set_xlabel(f'Time (Day Hour:Minute)', fontweight='bold')
        ax2.set_ylabel('Frequency (Hz)', fontweight='bold')
        #ax2.axvline(x=arrival, c='red')
        #cbar = fig1.colorbar(vals, orientation='horizontal')
        #cbar.set_label('Power ((m/s)^2/sqrt(Hz))', fontweight='bold')



#Configuración de la ventana 
screen_width =  app.winfo_screenwidth()
screen_height = app.winfo_screenheight()
app.geometry(f"{screen_width}x{screen_height}")
app.iconbitmap("imagenes\logo.ico")
#app.configure(bg="purple3")

#Variable de selección
seleccion = tk.StringVar(value="")

#Label principal 
label_titulo = tk.Label(app,text="Sistema de detección de sismos", font=("consolas", 24, "bold"), fg="purple3")
label_titulo.pack()
#Frame de selección
frame_selection = tk.Frame(app)

btn_luna=tk.Button(frame_selection, text="Luna",bg="purple4",activebackground="MediumPurple",activeforeground="snow",width=20,height=1, relief='flat',cursor='hand2',font=("verdana", 12), fg="snow",command=btn_luna_function)
btn_luna.pack(pady=20)

btn_marte=tk.Button(frame_selection, text="Marte",bg="purple4",activebackground="MediumPurple",activeforeground="snow",width=20,height=1,relief='flat', cursor='hand2',font=("verdana", 12), fg="snow",command=btn_marte_function)
btn_marte.pack(pady=20)

imagen_logo = Image.open("imagenes\logo2.jpeg")
imagen_logo = imagen_logo.resize((200,70))
photo_logo = ImageTk.PhotoImage(imagen_logo)
label_logo = tk.Label(app, image=photo_logo)
label_logo.pack()
""" radio_luna = tk.Radiobutton(frame_selection, text="Luna",variable=seleccion, value="Luna", command=actualizar_imagen)
radio_luna.grid(row=0, column=0)

radio_marte = tk.Radiobutton(frame_selection, text="Marte", variable=seleccion, value="Marte", command=actualizar_imagen)
radio_marte.grid(row=1, column=0) """
frame_selection.pack(pady=20)

#Imagen por defecto
imagen_ini = Image.open("imagenes\luna.png")
imagen_ini = imagen_ini.resize((200,200))
photo_ini = ImageTk.PhotoImage(imagen_ini)
label_imagen = tk.Label(app, image=photo_ini)
label_imagen.pack()

#frame_graficas.configure(bg="black")
#Canvas 1
canvas1.draw()
canvas1.get_tk_widget().grid(row=0, column=0)
#Canvas 2
canvas2.draw()
canvas2.get_tk_widget().grid(row=0, column=10)
frame_graficas.pack(pady=20)

app.mainloop()