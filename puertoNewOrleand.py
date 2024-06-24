#Puerto caldera

import tkinter as tk
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import random
import matplotlib.pyplot as plt
import pandas as pd
import json
import os

# Distribuciones de probabilidad para las llegadas de barcazas
llegadas_prob = [(0, 0.13), (1, 0.17), (2, 0.15), (3, 0.25), (4, 0.20), (5, 0.10)]
# Distribuciones de probabilidad para las descargas de barcazas
descargas_prob = [(1, 0.05), (2, 0.15), (3, 0.50), (4, 0.20), (5, 0.10)]

# Variables globales para almacenar los datos de la simulación
llegadas_diarias = []
descargas_diarias = []
retrasos_diarias = []
simulaciones_guardadas = []

modo_manual = False  # Variable global para controlar el modo de entrada de datos
dia_actual = 0  # Variable global para controlar el día actual en el modo manual

def generar_valor(probabilidades):
    """Generar un valor basado en una distribución de probabilidad"""
    rand_val = random.random()
    acumulado = 0
    for valor, prob in probabilidades:
        acumulado += prob
        if rand_val <= acumulado:
            return valor
    return probabilidades[-1][0]

def guardar_simulacion(simulacion):
    """Guardar la simulación en un archivo Excel"""
    filename = "simulaciones.xlsx"
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        df = pd.concat([df, pd.DataFrame([simulacion])], ignore_index=True)
    else:
        df = pd.DataFrame([simulacion])
    df.to_excel(filename, index=False)

def cargar_simulaciones():
    """Cargar las simulaciones guardadas del archivo Excel"""
    global simulaciones_guardadas
    simulaciones_guardadas.clear()
    filename = "simulaciones.xlsx"
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        df["llegadas_diarias"] = df["llegadas_diarias"].apply(json.loads)
        df["descargas_diarias"] = df["descargas_diarias"].apply(json.loads)
        df["retrasos_diarias"] = df["retrasos_diarias"].apply(json.loads)
        simulaciones_guardadas = df.to_dict(orient='records')

def obtener_ultimo_id():
    """Obtener el último ID utilizado para las simulaciones"""
    filename = "simulaciones.xlsx"
    if os.path.exists(filename):
        df = pd.read_excel(filename)
        return df["id"].max()
    return 0

def actualizar_ultimo_id(nuevo_id):
    """Actualizar el último ID utilizado para las simulaciones"""
    # No es necesario para el archivo Excel
    pass

def ejecutar_simulacion_automatica():
    """Iniciar la simulación automática al presionar el botón"""
    try:
        dias_simulacion = int(dias_entry.get())
        calcular_simulacion_automatica(dias_simulacion)
    except ValueError:
        messagebox.showerror("Entrada inválida", "Por favor, ingrese un número válido de días.")

def calcular_simulacion_automatica(dias_simulacion):
    global llegadas_diarias, descargas_diarias, retrasos_diarias, tree, boton_graficar, boton_limpiar

    identificador = obtener_ultimo_id() + 1
    retrasos = 0
    total_llegadas = 0
    total_descargas = 0
    total_retrasos = 0
    ganancia_total = 0
    perdida_total = 0

    llegadas_diarias.clear()
    descargas_diarias.clear()
    retrasos_diarias.clear()

    ganancia_por_descarga = float(ganancia_entry.get())
    perdida_por_retraso = float(perdida_entry.get())

    for dia in range(1, dias_simulacion + 1):
        llegadas = generar_valor(llegadas_prob)
        if llegadas == 0 and retrasos == 0:
            descargas = 0
        else:
            descargas = generar_valor(descargas_prob)

        total_llegadas += llegadas

        # Barcazas a descargar hoy
        a_descargar = min(llegadas + retrasos, descargas)
        total_descargas += a_descargar
        retrasos = max(0, llegadas + retrasos - a_descargar)
        total_retrasos += retrasos

        ganancia_total += a_descargar * ganancia_por_descarga
        perdida_total += retrasos * perdida_por_retraso

        llegadas_diarias.append(llegadas)
        descargas_diarias.append(descargas)
        retrasos_diarias.append(retrasos)

    neto_total = ganancia_total - perdida_total

    # Guardar la simulación
    simulacion = {
        "id": identificador,
        "dias_simulacion": dias_simulacion,
        "llegadas_diarias": json.dumps(llegadas_diarias),
        "descargas_diarias": json.dumps(descargas_diarias),
        "retrasos_diarias": json.dumps(retrasos_diarias),
        "total_llegadas": total_llegadas,
        "total_descargas": total_descargas,
        "total_retrasos": total_retrasos,
        "retrasos_promedio": total_retrasos / dias_simulacion if dias_simulacion > 0 else 0,
        "ganancia_total": ganancia_total,
        "perdida_total": perdida_total,
        "neto_total": neto_total
    }
    guardar_simulacion(simulacion)
    mostrar_resultados(simulacion)

def calcular_simulacion_manual():
    """Calcular la simulación manual con los datos ingresados"""
    global modo_manual
    modo_manual = True
    ventana_manual.destroy()

    identificador = obtener_ultimo_id() + 1
    total_llegadas = sum(llegadas_diarias)
    total_descargas = sum(descargas_diarias)
    total_retrasos = sum(retrasos_diarias)
    retrasos_promedio = total_retrasos / len(retrasos_diarias) if len(retrasos_diarias) > 0 else 0

    ganancia_por_descarga = float(ganancia_entry.get())
    perdida_por_retraso = float(perdida_entry.get())
    ganancia_total = total_descargas * ganancia_por_descarga
    perdida_total = total_retrasos * perdida_por_retraso
    neto_total = ganancia_total - perdida_total

    # Guardar la simulación
    simulacion = {
        "id": identificador,
        "dias_simulacion": len(llegadas_diarias),
        "llegadas_diarias": json.dumps(llegadas_diarias),
        "descargas_diarias": json.dumps(descargas_diarias),
        "retrasos_diarias": json.dumps(retrasos_diarias),
        "total_llegadas": total_llegadas,
        "total_descargas": total_descargas,
        "total_retrasos": total_retrasos,
        "retrasos_promedio": retrasos_promedio,
        "ganancia_total": ganancia_total,
        "perdida_total": perdida_total,
        "neto_total": neto_total
    }
    guardar_simulacion(simulacion)
    mostrar_resultados(simulacion)

def mostrar_resultados(simulacion):
    """Mostrar los resultados en la interfaz gráfica"""
    global tree, boton_graficar, boton_limpiar

    columns = ("Día", "Llegadas", "Descargas", "Retrasos")
    tree = ttk.Treeview(canvas, columns=columns, show='headings', height=10)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100, anchor="center")

    # Limpiar la tabla antes de insertar nuevos datos
    for row in tree.get_children():
        tree.delete(row)

    # Insertar datos en la tabla
    llegadas_diarias = json.loads(simulacion["llegadas_diarias"])
    descargas_diarias = json.loads(simulacion["descargas_diarias"])
    retrasos_diarias = json.loads(simulacion["retrasos_diarias"])

    for dia in range(simulacion["dias_simulacion"]):
        tree.insert("", "end", values=(dia + 1, llegadas_diarias[dia], descargas_diarias[dia], retrasos_diarias[dia]))

    tree_id = canvas.create_window(400, 380, window=tree)

    # Mostrar resultados directamente en la interfaz
    resultados = (f"Total de llegadas en {simulacion['dias_simulacion']} días: {simulacion['total_llegadas']}\n"
                  f"Total de descargas en {simulacion['dias_simulacion']} días: {simulacion['total_descargas']}\n"
                  f"Retrasos promedio por día: {simulacion['retrasos_promedio']:.2f}\n"
                  f"Total de retrasos: {simulacion['total_retrasos']}\n"
                  f"Ganancia total: {simulacion['ganancia_total']:.2f}\n"
                  f"Pérdida total: {simulacion['perdida_total']:.2f}\n"
                  f"Neto total: {simulacion['neto_total']:.2f}")
    resultado_label.config(text=resultados)

    # Crear el botón para generar gráficos
    boton_graficar = ttk.Button(canvas, text="Generar Gráfica", command=generar_graficos)
    boton_graficar_id = canvas.create_window(400, 550, window=boton_graficar)

    # Crear el botón para limpiar la tabla y ocultar botones
    boton_limpiar = ttk.Button(canvas, text="Limpiar", command=lambda: limpiar_tabla(tree_id, boton_graficar_id, boton_limpiar_id))
    boton_limpiar_id = canvas.create_window(400, 600, window=boton_limpiar)

def abrir_ventana_manual(dias_simulacion):
    """Abrir ventana para entrada manual de datos"""
    global ventana_manual, entry_llegadas, entry_descargas, dia_actual, retrasos_anterior
    dia_actual = 0
    retrasos_anterior = 0
    llegadas_diarias.clear()
    descargas_diarias.clear()
    retrasos_diarias.clear()
    ventana_manual = tk.Toplevel()
    ventana_manual.title("Entrada Manual de Datos")
    ventana_manual.geometry("400x300")
    
    ttk.Label(ventana_manual, text="Día 1", font=("Helvetica", 14)).pack(pady=10)
    
    frame_llegadas = ttk.Frame(ventana_manual)
    frame_llegadas.pack(pady=5)
    ttk.Label(frame_llegadas, text="Llegadas:").pack(side="left")
    entry_llegadas = ttk.Entry(frame_llegadas, width=5)
    entry_llegadas.pack(side="left")
    
    frame_descargas = ttk.Frame(ventana_manual)
    frame_descargas.pack(pady=5)
    ttk.Label(frame_descargas, text="Descargas:").pack(side="left")
    entry_descargas = ttk.Entry(frame_descargas, width=5)
    entry_descargas.pack(side="left")
    
    frame_botones = ttk.Frame(ventana_manual)
    frame_botones.pack(pady=20)
    
    ttk.Button(frame_botones, text="Siguiente Día", command=lambda: siguiente_dia(dias_simulacion)).pack(side="left", padx=10)
    ttk.Button(frame_botones, text="Ejecutar Reporte", command=calcular_simulacion_manual).pack(side="left", padx=10)

def siguiente_dia(dias_simulacion):
    """Guardar los datos del día actual y pasar al siguiente día"""
    global dia_actual, entry_llegadas, entry_descargas, retrasos_anterior
    try:
        llegadas = int(entry_llegadas.get())
        descargas = int(entry_descargas.get())
        if dia_actual < dias_simulacion:
            llegadas_diarias.append(llegadas)
            descargas_diarias.append(descargas)
            
            # Calcular retrasos
            a_descargar = min(llegadas + retrasos_anterior, descargas)
            retrasos_anterior = max(0, llegadas + retrasos_anterior - a_descargar)
            retrasos_diarias.append(retrasos_anterior)
            
            dia_actual += 1
            if dia_actual < dias_simulacion:
                for widget in ventana_manual.winfo_children():
                    widget.destroy()
                ttk.Label(ventana_manual, text=f"Día {dia_actual + 1}", font=("Helvetica", 14)).pack(pady=10)
                
                frame_llegadas = ttk.Frame(ventana_manual)
                frame_llegadas.pack(pady=5)
                ttk.Label(frame_llegadas, text="Llegadas:").pack(side="left")
                entry_llegadas = ttk.Entry(frame_llegadas, width=5)
                entry_llegadas.pack(side="left")
                
                frame_descargas = ttk.Frame(ventana_manual)
                frame_descargas.pack(pady=5)
                ttk.Label(frame_descargas, text="Descargas:").pack(side="left")
                entry_descargas = ttk.Entry(frame_descargas, width=5)
                entry_descargas.pack(side="left")
                
                frame_botones = ttk.Frame(ventana_manual)
                frame_botones.pack(pady=20)
                
                ttk.Button(frame_botones, text="Siguiente Día", command=lambda: siguiente_dia(dias_simulacion)).pack(side="left", padx=10)
                ttk.Button(frame_botones, text="Ejecutar Reporte", command=calcular_simulacion_manual).pack(side="left", padx=10)
    except ValueError:
        messagebox.showerror("Entrada inválida", "Por favor, ingrese valores numéricos válidos.")

def generar_graficos():
    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(range(1, len(llegadas_diarias) + 1), llegadas_diarias, label='Llegadas Diarias', marker='o')
    plt.plot(range(1, len(descargas_diarias) + 1), descargas_diarias, label='Descargas Diarias', marker='x')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title('Llegadas y Descargas Diarias')
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(range(1, len(llegadas_diarias) + 1), retrasos_diarias, label='Retrasos Acumulados', marker='s', color='red')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title('Retrasos Acumulados')
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 3)
    ganancia_diaria = [descargas_diarias[i] * float(ganancia_entry.get()) for i in range(len(descargas_diarias))]
    perdida_diaria = [retrasos_diarias[i] * float(perdida_entry.get()) for i in range(len(retrasos_diarias))]
    neto_diario = [ganancia_diaria[i] - perdida_diaria[i] for i in range(len(ganancia_diaria))]
    plt.plot(range(1, len(ganancia_diaria) + 1), ganancia_diaria, label='Ganancia Diaria', marker='o', color='green')
    plt.plot(range(1, len(perdida_diaria) + 1), perdida_diaria, label='Pérdida Diaria', marker='x', color='red')
    plt.plot(range(1, len(neto_diario) + 1), neto_diario, label='Neto Diario', marker='s', color='blue')
    plt.xlabel('Día')
    plt.ylabel('Valor')
    plt.title('Ganancia, Pérdida y Neto Diario')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def generar_graficos_individuales(llegadas_diarias, descargas_diarias, retrasos_diarias, id_simulacion):
    """Generar gráficos para una simulación individual"""
    plt.figure(figsize=(10, 6))

    plt.subplot(3, 1, 1)
    plt.plot(range(1, len(llegadas_diarias) + 1), llegadas_diarias, label='Llegadas Diarias', marker='o')
    plt.plot(range(1, len(descargas_diarias) + 1), descargas_diarias, label='Descargas Diarias', marker='x')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title(f'Reporte {id_simulacion} - Llegadas y Descargas Diarias')
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 2)
    plt.plot(range(1, len(retrasos_diarias) + 1), retrasos_diarias, label='Retrasos Acumulados', marker='s', color='red')
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title(f'Reporte {id_simulacion} - Retrasos Acumulados')
    plt.legend()
    plt.grid(True)

    plt.subplot(3, 1, 3)
    ganancia_diaria = [descargas_diarias[i] * float(ganancia_entry.get()) for i in range(len(descargas_diarias))]
    perdida_diaria = [retrasos_diarias[i] * float(perdida_entry.get()) for i in range(len(retrasos_diarias))]
    neto_diario = [ganancia_diaria[i] - perdida_diaria[i] for i in range(len(ganancia_diaria))]
    plt.plot(range(1, len(ganancia_diaria) + 1), ganancia_diaria, label='Ganancia Diaria', marker='o', color='green')
    plt.plot(range(1, len(perdida_diaria) + 1), perdida_diaria, label='Pérdida Diaria', marker='x', color='red')
    plt.plot(range(1, len(neto_diario) + 1), neto_diario, label='Neto Diario', marker='s', color='blue')
    plt.xlabel('Día')
    plt.ylabel('Valor')
    plt.title(f'Reporte {id_simulacion} - Ganancia, Pérdida y Neto Diario')
    plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

def limpiar_tabla(tree_id, boton_graficar_id, boton_limpiar_id):
    """Limpiar la tabla y ocultar los botones de gráfica y limpiar"""
    global llegadas_diarias, descargas_diarias, retrasos_diarias
    canvas.delete(tree_id)
    canvas.delete(boton_graficar_id)
    canvas.delete(boton_limpiar_id)
    resultado_label.config(text="")
    llegadas_diarias.clear()
    descargas_diarias.clear()
    retrasos_diarias.clear()

def cargar_imagen_fondo():
    """Cargar y mostrar la imagen de fondo"""
    try:
        imagen_fondo = Image.open("fondo.jpg")  # Asegúrate de tener esta imagen en el mismo directorio
        imagen_fondo = imagen_fondo.resize((800, 700))
        return ImageTk.PhotoImage(imagen_fondo)
    except Exception as e:
        messagebox.showerror("Error al cargar la imagen", f"No se pudo cargar la imagen de fondo: {e}")
        ventana.destroy()
        exit()

def limpiar_simulaciones_guardadas():
    """Limpiar el archivo de simulaciones guardadas"""
    if os.path.exists("simulaciones.xlsx"):
        os.remove("simulaciones.xlsx")
        messagebox.showinfo("Simulaciones", "Todas las simulaciones guardadas han sido eliminadas.")
    else:
        messagebox.showinfo("Simulaciones", "No hay simulaciones guardadas para eliminar.")

def ver_simulaciones_guardadas():
    """Mostrar todas las simulaciones guardadas en una nueva ventana"""
    cargar_simulaciones()
    top = tk.Toplevel()
    top.title("Reportes Guardados")
    top.geometry("1100x500")
    top.resizable(False, False)

    columns = ("ID", "Días", "Total Llegadas", "Total Descargas", "Retraso Promedio", "Total Retrasos", "GananciaT otal", "Pérdida Total", "Total", "Acciones")
    tree = ttk.Treeview(top, columns=columns, show='headings', height=20)
    for col in columns:
        tree.heading(col, text=col)
        tree.column(col, width=100 if col != "Acciones" else 150, anchor="center")

    def generar_graficos_desde_fila(event):
        item = tree.focus()
        values = tree.item(item, "values")
        if values:
            id_simulacion = int(values[0])
            simulacion = next((s for s in simulaciones_guardadas if s["id"] == id_simulacion), None)
            if simulacion:
                generar_graficos_individuales(
                    simulacion["llegadas_diarias"], 
                    simulacion["descargas_diarias"], 
                    simulacion["retrasos_diarias"], 
                    simulacion["id"]
                )

    for simulacion in simulaciones_guardadas:
        tree.insert("", "end", values=(
            simulacion["id"],
            simulacion["dias_simulacion"],
            simulacion["total_llegadas"],
            simulacion["total_descargas"],
            simulacion["retrasos_promedio"],
            simulacion["total_retrasos"],
            simulacion["ganancia_total"],
            simulacion["perdida_total"],
            simulacion["neto_total"],
            "Generar Gráfica"
        ))

    tree.pack(fill="both", expand=True)
    tree.bind('<ButtonRelease-1>', generar_graficos_desde_fila)

    #boton_graficar_comparativo = ttk.Button(top, text="Generar Gráfica Comparativa", command=generar_graficos_comparativos)
    #boton_graficar_comparativo.pack(pady=10)

def generar_graficos_comparativos():
    """Generar gráficos comparativos de todas las simulaciones guardadas"""
    cargar_simulaciones()
    if not simulaciones_guardadas:
        messagebox.showinfo("No hay reportes", "No hay reportes guardadas para mostrar.")
        return

    plt.figure(figsize=(10, 6))
    
    for simulacion in simulaciones_guardadas:
        plt.plot(range(1, simulacion["dias_simulacion"] + 1), simulacion["llegadas_diarias"], label=f'Simulación {simulacion["id"]} - Llegadas')
        plt.plot(range(1, simulacion["dias_simulacion"] + 1), simulacion["descargas_diarias"], label=f'Simulación {simulacion["id"]} - Descargas')
    
    plt.xlabel('Día')
    plt.ylabel('Cantidad')
    plt.title('Comparación de Llegadas y Descargas Diarias')
    #plt.legend()
    plt.grid(True)

    plt.tight_layout()
    plt.show()

# Crear la ventana principal
ventana = tk.Tk()
ventana.title("Gestion de Colas - Puerto Caldera")
ventana.geometry("800x700")
ventana.resizable(False, False)

# Cargar la imagen de fondo
imagen_fondo = cargar_imagen_fondo()

# Crear un canvas para la imagen de fondo
canvas = tk.Canvas(ventana, width=800, height=700)
canvas.pack(fill="both", expand=True)
canvas.create_image(0, 0, image=imagen_fondo, anchor="nw")
# Crear los widgets en el canvas
titulo = ttk.Label(canvas, text="Gestion de Colas de Puerto Caldera", font=("Helvetica", 16))
canvas.create_window(400, 50, window=titulo)

dias_label = ttk.Label(canvas, text="Número de días de Reporte:", font=("Helvetica", 12))
canvas.create_window(400, 100, window=dias_label)

dias_entry = ttk.Entry(canvas, width=5)
canvas.create_window(400, 130, window=dias_entry)
dias_entry.insert(0, "7")

ganancia_label = ttk.Label(canvas, text="Ganancia por descarga:", font=("Helvetica", 12))
canvas.create_window(400, 160, window=ganancia_label)

ganancia_entry = ttk.Entry(canvas, width=5)
canvas.create_window(500, 160, window=ganancia_entry)
ganancia_entry.insert(0, "1000")

perdida_label = ttk.Label(canvas, text="Pérdida por retraso:", font=("Helvetica", 12))
canvas.create_window(400, 190, window=perdida_label)

perdida_entry = ttk.Entry(canvas, width=5)
canvas.create_window(500, 190, window=perdida_entry)
perdida_entry.insert(0, "500")

# Crear un frame para los botones
botones_frame = ttk.Frame(canvas)
canvas.create_window(400, 220, window=botones_frame)

# Botón para abrir la ventana de entrada manual
boton_manual = ttk.Button(botones_frame, text="Entrada Manual de Datos", command=lambda: abrir_ventana_manual(int(dias_entry.get())))
boton_manual.pack(side="left", padx=10, pady=10)

# Botón para ejecutar la simulación automática
boton_simular = ttk.Button(botones_frame, text="Ejecutar reporte Automático", command=ejecutar_simulacion_automatica)
boton_simular.pack(side="left", padx=10, pady=10)

# Crear un frame para otros botones
otros_botones_frame = ttk.Frame(canvas)
canvas.create_window(400, 280, window=otros_botones_frame)

# Botón para ver simulaciones guardadas
boton_ver_simulaciones = ttk.Button(otros_botones_frame, text="Ver Reportes Guardados", command=ver_simulaciones_guardadas)
boton_ver_simulaciones.pack(side="left", padx=10, pady=10)

# Botón para limpiar el archivo de simulaciones guardadas
boton_limpiar_simulaciones = ttk.Button(otros_botones_frame, text="Limpiar Reportes Guardados", command=limpiar_simulaciones_guardadas)
boton_limpiar_simulaciones.pack(side="left", padx=10, pady=10)

# Etiqueta para mostrar resultados
resultado_label = ttk.Label(canvas, text="", font=("Helvetica", 12))
canvas.create_window(400, 340, window=resultado_label)

ventana.mainloop()
