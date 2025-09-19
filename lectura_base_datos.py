import pandas as pd
#from rgbmatrix import RGBMatrix, RGBMatrixOptions
import time
import sys
#from PIL import Image, ImageDraw, ImageFont

nombre_archivo = 'prueba_excel.xlsx'
nombre_columna_a_leer = 'hola' 

# ---- 1. Función para leer frases del archivo de Excel ----
def leer_frases_excel(nombre_archivo, nombre_columna_a_leer):
    """Lee frases de una columna específica en un archivo de Excel."""
    try:
        df = pd.read_excel(nombre_archivo, sheet_name=0)
        frases = df[nombre_columna_a_leer].tolist()
        return frases
    except FileNotFoundError:
        print(f"Error: El archivo '{nombre_archivo}' no fue encontrado.")
        sys.exit(1)
    except KeyError:
        print(f"Error: La columna '{nombre_columna_a_leer}' no existe en el archivo.")
        sys.exit(1)
    except Exception as e:
        print(f"Ocurrió un error al leer el archivo: {e}")
        sys.exit(1)
   
datos_leidos = leer_frases_excel(nombre_archivo, nombre_columna_a_leer)

# Muestra los datos leídos
if datos_leidos:
    print(f"Datos de la columna '{nombre_columna_a_leer}':")
    for frase in datos_leidos:
        print(frase)
"""
# ---- 2. Configuración y visualización en el panel LED ----
def mostrar_frases_en_led_panel(frases):
    if not frases:
        print("No hay frases para mostrar. Saliendo del programa.")
        return

    # Configuración del panel LED
    options = RGBMatrixOptions()
    options.rows = 64
    options.cols = 128
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = "adafruit-hat-pwm"
    options.gpio_slowdown = 4
    
    # Crear el objeto de la matriz
    try:
        matrix = RGBMatrix(options=options)
    except Exception as e:
        print(f"Error al inicializar la matriz: {e}")
        return

    try:
        font = matrix.LoadFont("fonts/7x13.bdf")
    except Exception as e:
        print(f"Error al cargar la fuente: {e}")
        return

    print("Empezando a mostrar frases. Presiona CTRL+C para detener.")
    
    # Bucle infinito para recorrer las frases
    while True:
        for frase in frases:
            canvas = matrix.CreateFrameCanvas()
            
            # Limpia el canvas
            canvas.Clear()

            text_width = font.text_width(frase)
            x_pos = (canvas.width - text_width) // 2
            y_pos = (canvas.height - font.height) // 2 + font.height

            # Dibuja el texto en el canvas. 
            canvas.DrawText(font, x_pos, y_pos, frase.encode('utf-8'))
            
            # Muestra el canvas en la pantalla y espera 5 segundos
            matrix.SwapOnVSync(canvas)
            time.sleep(5)
            
# ---- 3. Lógica principal del programa ----
if __name__ == "__main__":
    # Configuración del archivo y la columna
    archivo_excel = 'frases.xlsx'
    columna_frases = 'Frase'

    # Lee las frases desde el archivo
    lista_de_frases = leer_frases_excel(archivo_excel, columna_frases)

    # Muestra las frases en el panel LED
    mostrar_frases_en_led_panel(lista_de_frases)
"""
