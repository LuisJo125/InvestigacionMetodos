import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk  # Necesitas instalar Pillow (pip install pillow)
import random
import matplotlib.pyplot as plt

# Distribuciones de probabilidad para las llegadas de barcazas
llegadas_prob = [(0, 0.13), (1, 0.17), (2, 0.15), (3, 0.25), (4, 0.20), (5, 0.10)]
# Distribuciones de probabilidad para las descargas de barcazas
descargas_prob = [(1, 0.05), (2, 0.15), (3, 0.50), (4, 0.20), (5, 0.10)]

# Variables globales para almacenar los datos de la simulación
llegadas_diarias = []
descargas_diarias = []
retrasos_diarias = []

def generar_valor(probabilidades):
    """Generar un valor basado en una distribución de probabilidad"""
    rand_val = random.random()
    acumulado = 0
    for valor, prob in probabilidades:
        acumulado += prob
        if rand_val <= acumulado:
            return valor
    return probabilidades[-1][0]

def ejecutar_simulacion(dias_simulacion):
    global llegadas_diarias, descargas_diarias, retrasos_diarias, tree, boton_graficar, boton_limpiar
    retrasos = 0
    total_llegadas = 0
    total_descargas = 0

    llegadas_diarias = []
    descargas_diarias = []
    retrasos_diarias = []

    for dia in range(1, dias_simulacion + 1):
        llegadas = generar_valor(llegadas_prob)
        descargas = generar_valor(descargas_prob)
        total_llegadas += llegadas
        
        # Barcazas a descargar hoy
        a_descargar = min(llegadas + retrasos, descargas)
        total_descargas += a_descargar
        retrasos = max(0, llegadas + retrasos - a_descargar)

        llegadas_diarias.append(llegadas)
        descargas_diarias.append(descargas)
        retrasos_diarias.append(retrasos)
    
    # Crear la tabla para mostrar los resultados
    columns = ("Día", "Llegadas", "Descargas", "Retrasos")
    tree = ttk.Treeview(canvas, columns=columns, show='headings', height=10)
    tree.heading("Día", text="Día")
    tree.heading("Llegadas", text="Llegadas")
    tree.heading("Descargas", text="Descargas")
    tree.heading("Retrasos", text="Retrasos")

    for col in columns:
        tree.column(col, width=100, anchor="center")

    # Limpiar la tabla antes de insertar nuevos datos
    for row in tree.get_children():
        tree.delete(row)

    # Insertar datos en la tabla
    for dia in range(dias_simulacion):
        tree.insert("", "end", values=(dia + 1, llegadas_diarias[dia], descargas_diarias[dia], retrasos_diarias[dia]))

    tree_id = canvas.create_window(400, 380, window=tree)

    # Mostrar resultados directamente en la interfaz
    resultados = f"Total de llegadas en {dias_simulacion} días: {total_llegadas}\nTotal de descargas en {dias_simulacion} días: {total_descargas}\nRetrasos promedio por día: {retrasos / dias_simulacion:.2f}"
    resultado_label.config(text=resultados)

    # Crear el botón para generar gráficos
    boton_graficar = ttk.Button(canvas, text="Generar Gráfica", command=generar_graficos)
    boton_graficar_id = canvas.create_window(400, 550, window=boton_graficar)

    # Crear el botón para limpiar la tabla y ocultar botones
    boton_limpiar = ttk.Button(canvas, text="Limpiar", command=lambda: limpiar_tabla(tree_id, boton_graficar_id, boton_limpiar_id))
    boton_limpiar_id = canvas.create_window(400, 600, window=boton_limpiar)

def generar_graficos():
    plt.figure(figsize=(10, 6))

    plt.subplot(2, 1, 1)
    plt.plot(range(1, len(llegadas_diarias) + 1), llegadas_diarias, label='Llegadas Diarias', marker='o')
    plt.plot(range(1, len(llegadas_diarias) + 1), descargas_diarias, label='Descargas Diarias', marker='x')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title('Llegadas y Descargas Diarias')
    plt.legend()
    plt.grid(True)

    plt.subplot(2, 1, 2)
    plt.plot(range(1, len(llegadas_diarias) + 1), retrasos_diarias, label='Retrasos Acumulados', marker='s', color='red')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title('Retrasos Acumulados')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def limpiar_tabla(tree_id, boton_graficar_id, boton_limpiar_id):
    # Limpiar la tabla y ocultar los botones de gráfica y limpiar
    canvas.delete(tree_id)
    canvas.delete(boton_graficar_id)
    canvas.delete(boton_limpiar_id)
    resultado_label.config(text="")

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Simulación de Colas - Puerto de Nueva Orleans")
ventana.geometry("800x700")
ventana.resizable(False, False)

# Cargar la imagen de fondo
try:
    imagen_fondo = Image.open("fondo.jpg")  # Asegúrate de tener esta imagen en el mismo directorio
    imagen_fondo = imagen_fondo.resize((800, 700))
    imagen_fondo = ImageTk.PhotoImage(imagen_fondo)
except Exception as e:
    messagebox.showerror("Error al cargar la imagen", f"No se pudo cargar la imagen de fondo: {e}")
    ventana.destroy()
    exit()

# Crear un canvas para la imagen de fondo
canvas = tk.Canvas(ventana, width=800, height=700)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=imagen_fondo, anchor="nw")

# Crear los widgets en el canvas
titulo = ttk.Label(canvas, text="Simulación de Colas en el Puerto de Nueva Orleans", font=("Helvetica", 16))
canvas.create_window(400, 50, window=titulo)

dias_label = ttk.Label(canvas, text="Número de días de simulación:", font=("Helvetica", 12))
canvas.create_window(400, 100, window=dias_label)

dias_entry = ttk.Entry(canvas, width=5)
canvas.create_window(400, 130, window=dias_entry)
dias_entry.insert(0, "15")

def boton_simulacion():
    try:
        dias_simulacion = int(dias_entry.get())
        ejecutar_simulacion(dias_simulacion)
    except ValueError:
        messagebox.showerror("Entrada inválida", "Por favor, ingrese un número válido de días.")

boton_simular = ttk.Button(canvas, text="Ejecutar Simulación", command=boton_simulacion)
canvas.create_window(400, 180, window=boton_simular)

# Etiqueta para mostrar resultados
resultado_label = ttk.Label(canvas, text="", font=("Helvetica", 12))
canvas.create_window(400, 220, window=resultado_label)

ventana.mainloop()
