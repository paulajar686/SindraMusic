import customtkinter as ctk
from tkinter import filedialog
from CTkListbox import CTkListbox
import vlc
import os
import json
from mutagen import File
from PIL import Image, ImageTk
import io

# ------- CONFIGURACIÓN ------- #
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

instance = vlc.Instance()
player = instance.media_player_new()

playlist = []
favoritos = []
indice_actual = 0

ARCHIVO_PLAYLIST = "playlist_guardada.json"
label_mini = None

# -------- FUNCIONES -------- #

def guardar_playlist_auto():
    with open(ARCHIVO_PLAYLIST, "w") as f:
        json.dump(playlist, f)

def cargar_playlist_auto():
    global playlist
    if os.path.exists(ARCHIVO_PLAYLIST):
        with open(ARCHIVO_PLAYLIST, "r") as f:
            playlist = json.load(f)

        lista.delete("all")
        for c in playlist:
            lista.insert("end", os.path.basename(c))

def cargar_canciones():
    archivos = filedialog.askopenfilenames(
        filetypes=[("Audio", "*.mp3 *.wav *.m4a")]
    )
    for archivo in archivos:
        if archivo not in playlist:
            playlist.append(archivo)
            lista.insert("end", os.path.basename(archivo))

def reproducir():
    global indice_actual
    if not playlist:
        return

    seleccion = lista.curselection()
    if seleccion:
        indice_actual = seleccion

    archivo = playlist[indice_actual]

    media = instance.media_new(archivo)
    player.set_media(media)
    player.play()

    animar_titulo(os.path.basename(archivo))
    mostrar_caratula(archivo)

def pausar():
    player.pause()

def detener():
    player.stop()

def siguiente():
    global indice_actual
    if playlist:
        indice_actual = (indice_actual + 1) % len(playlist)
        reproducir_auto()

def anterior():
    global indice_actual
    if playlist:
        indice_actual = (indice_actual - 1) % len(playlist)
        reproducir_auto()

def reproducir_auto():
    lista.select(indice_actual)
    reproducir()

def cambiar_volumen(valor):
    player.audio_set_volume(int(float(valor) * 100))

def actualizar_barra():
    if player.is_playing():
        duracion = player.get_length() // 1000
        tiempo = player.get_time() // 1000

        if duracion > 0:
            barra_progreso.configure(to=duracion)
            barra_progreso.set(tiempo)

        if tiempo >= duracion - 1 and duracion > 0:
            siguiente()

    app.after(1000, actualizar_barra)

def mostrar_caratula(archivo):
    try:
        audio = File(archivo)
        if hasattr(audio, "tags"):
            for tag in audio.tags.values():
                if hasattr(tag, "data"):
                    imagen = Image.open(io.BytesIO(tag.data))
                    imagen = imagen.resize((200, 200))
                    img = ImageTk.PhotoImage(imagen)
                    label_img.configure(image=img, text="")
                    label_img.image = img
                    return
    except:
        pass

    label_img.configure(image=None, text="Sin carátula")

def guardar_playlist():
    ruta = filedialog.asksaveasfilename(defaultextension=".json")
    if ruta:
        with open(ruta, "w") as f:
            json.dump(playlist, f)

def cargar_playlist():
    global playlist
    ruta = filedialog.askopenfilename(filetypes=[("JSON", "*.json")])
    if ruta:
        with open(ruta, "r") as f:
            playlist = json.load(f)

        lista.delete("all")
        for c in playlist:
            lista.insert("end", os.path.basename(c))

# -------- BUSCADOR -------- #

def buscar_cancion(texto):
    lista.delete("all")
    for c in playlist:
        if texto.lower() in os.path.basename(c).lower():
            lista.insert("end", os.path.basename(c))

# -------- FAVORITOS -------- #

def agregar_favorito():
    seleccion = lista.curselection()
    if seleccion:
        cancion = playlist[seleccion]
        if cancion not in favoritos:
            favoritos.append(cancion)

# -------- MINI PLAYER -------- #

def actualizar_mini():
    if label_mini:
        if playlist:
            nombre = os.path.basename(playlist[indice_actual])
            label_mini.configure(text=f"Reproduciendo: {nombre}")
        else:
            label_mini.configure(text="Reproduciendo: Nada")

    app.after(1000, actualizar_mini)

def mini_reproductor():
    global label_mini

    mini = ctk.CTkToplevel(app)
    mini.geometry("300x120")
    mini.title("Mini Player")
    mini.attributes("-topmost", True)

    label_mini = ctk.CTkLabel(mini, text="Reproduciendo: Nada")
    label_mini.pack(pady=5)

    actualizar_mini()

    ctk.CTkButton(mini, text="▶️", command=reproducir).pack(side="left", padx=10, pady=10)
    ctk.CTkButton(mini, text="⏸️", command=pausar).pack(side="left", padx=10)
    ctk.CTkButton(mini, text="⏭️", command=siguiente).pack(side="left", padx=10)

# -------- ANIMACIÓN -------- #

def animar_titulo(texto):
    titulo.configure(text="")
    app.after(100, lambda: titulo.configure(text=texto))

# -------- CIERRE -------- #

def al_cerrar():
    guardar_playlist_auto()
    app.destroy()

# -------- UI -------- #

app = ctk.CTk()
app.geometry("900x600")
app.title("🎧 Sindra Music")

app.protocol("WM_DELETE_WINDOW", al_cerrar)

# SIDEBAR
sidebar = ctk.CTkFrame(app, width=220)
sidebar.pack(side="left", fill="y", padx=10, pady=10)

ctk.CTkLabel(sidebar, text="🎧 Mi Música", font=("Arial", 18, "bold")).pack(pady=20)

ctk.CTkButton(sidebar, text="➕ Cargar canciones", command=cargar_canciones)\
    .pack(pady=10, padx=15, fill="x")

ctk.CTkButton(sidebar, text="💾 Guardar playlist", command=guardar_playlist)\
    .pack(pady=10, padx=15, fill="x")

ctk.CTkButton(sidebar, text="📂 Cargar playlist", command=cargar_playlist)\
    .pack(pady=10, padx=15, fill="x")

ctk.CTkButton(sidebar, text="🎧 Mini Player", command=mini_reproductor)\
    .pack(pady=20, padx=15, fill="x")

# MAIN
main = ctk.CTkFrame(app)
main.pack(side="left", fill="both", expand=True)

titulo = ctk.CTkLabel(main, text="Selecciona una canción", font=("Arial", 20))
titulo.pack(pady=10)

label_img = ctk.CTkLabel(main, text="Sin carátula")
label_img.pack(pady=10)

# BUSCADOR
buscador = ctk.CTkEntry(main, placeholder_text="🔍 Buscar canción...")
buscador.pack(pady=10)
buscador.bind("<KeyRelease>", lambda e: buscar_cancion(buscador.get()))

# LISTA
lista = CTkListbox(main, width=500, height=200)
lista.pack(pady=10)

# CONTROLES
controles = ctk.CTkFrame(main)
controles.pack(pady=10)

ctk.CTkButton(controles, text="⏮️", width=50, command=anterior).grid(row=0, column=0, padx=10)
ctk.CTkButton(controles, text="▶️", width=50, command=reproducir).grid(row=0, column=1, padx=10)
ctk.CTkButton(controles, text="⏸️", width=50, command=pausar).grid(row=0, column=2, padx=10)
ctk.CTkButton(controles, text="⏹️", width=50, command=detener).grid(row=0, column=3, padx=10)
ctk.CTkButton(controles, text="⏭️", width=50, command=siguiente).grid(row=0, column=4, padx=10)
ctk.CTkButton(controles, text="❤️", width=50, command=agregar_favorito).grid(row=0, column=5, padx=10)

# PROGRESO
barra_progreso = ctk.CTkSlider(main, from_=0, to=100)
barra_progreso.pack(fill="x", padx=20, pady=10)

# VOLUMEN
ctk.CTkLabel(main, text="Volumen").pack()
slider_vol = ctk.CTkSlider(main, from_=0, to=1, command=cambiar_volumen)
slider_vol.set(0.5)
slider_vol.pack(pady=5)

# INICIO
cargar_playlist_auto()
actualizar_barra()

app.mainloop()
