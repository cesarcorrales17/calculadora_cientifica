"""
Módulo GUI de la Calculadora Científica
=======================================
Este módulo implementa la interfaz gráfica de usuario para la calculadora científica
utilizando la biblioteca customtkinter (versión mejorada de tkinter) para crear
una interfaz moderna con tema oscuro.

La GUI incluye botones para números, operadores matemáticos básicos, funciones trigonométricas,
logaritmos y constantes matemáticas.
"""

# Importación de bibliotecas necesarias
import customtkinter as ctk        # Biblioteca para crear interfaces gráficas modernas
from backend.parser import evaluar_expresion  # Importamos el analizador de expresiones matemáticas

def click(b, entry):
    """
    Función que maneja la lógica de los clics en los botones de la calculadora.
    
    Parámetros:
    - b (str): El texto/valor del botón presionado
    - entry (CTkEntry): El campo de entrada donde se muestra la expresión y resultados
    
    Comportamiento:
    - Si se presiona "=": Evalúa la expresión matemática actual y muestra el resultado
    - Si se presiona "C": Borra todo el contenido del campo de entrada
    - Para cualquier otro botón: Añade su valor al campo de entrada
    """
    if b == "=":
        try:
            # Obtiene la expresión del campo de entrada
            expresion = entry.get()
            # Evalúa la expresión usando el analizador matemático del backend
            result = evaluar_expresion(expresion)
            # Borra el contenido actual y muestra el resultado
            entry.delete(0, "end")
            entry.insert("end", str(result))
        except Exception:
            # En caso de error en la expresión, muestra "Error"
            entry.delete(0, "end")
            entry.insert("end", "Error")
    elif b == "C":
        # Botón de borrar: limpia el campo de entrada
        entry.delete(0, "end")
    else:
        # Para cualquier otro botón, añade su valor al campo
        entry.insert("end", b)

def lanzar_calculadora():
    """
    Función principal que crea y configura la ventana de la calculadora.
    Esta función debe ser llamada para iniciar la aplicación.
    """
    # ----- Configuración inicial de la ventana -----
    ctk.set_appearance_mode("dark")  # Configura el tema oscuro para toda la aplicación
    root = ctk.CTk()                 # Crea la ventana principal
    root.title("Calculadora Científica")  # Establece el título de la ventana
    root.geometry("420x600")              # Dimensiones de la ventana (ancho x alto)
    root.resizable(False, False)          # Impide que el usuario redimensione la ventana

    # ---------- Pantalla de visualización ----------
    # Creación del campo de entrada/visualización donde se muestran las expresiones y resultados
    entry = ctk.CTkEntry(
        root,                         # Ventana padre donde se coloca este elemento
        width=380,                    # Ancho del campo en píxeles
        height=60,                    # Alto del campo en píxeles
        font=("Consolas", 22, "bold"),# Fuente de tipo monoespaciada (todas las letras ocupan el mismo espacio)
        justify="right",              # Alinea el texto a la derecha (como las calculadoras reales)
        fg_color="#000000",           # Color de fondo negro para la pantalla
        text_color="#00ff99"          # Color de texto verde brillante (simula el display LCD de calculadoras)
    )
    # Posicionamiento del campo en la ventana usando coordenadas absolutas
    entry.place(x=20, y=20)           # Coordenadas (x, y) desde la esquina superior izquierda

    # ---------- Definición de botones: matriz de disposición ----------
    # Matriz que define la disposición de los botones en filas y columnas
    # Cada sublista representa una fila de botones en la calculadora
    botones = [
        # Primera fila: funciones matemáticas
        ["sin","cos","tan","log","ln","sqrt"],
        # Segunda fila: números y operaciones
        ["7","8","9","/","(",")"],
        # Tercera fila: números, multiplicación y constantes
        ["4","5","6","*","pi","e"],
        # Cuarta fila: números, resta, potencia y borrar
        ["1","2","3","-","^","C"],
        # Quinta fila: cero, punto decimal, suma e igual
        ["0",".","+","="]
    ]

    # ---------- Esquema de colores: diccionario de estilos visuales ----------
    # Define colores personalizados para cada categoría de botones
    # Cada categoría tiene un color de fondo (fg_color) y un color cuando el ratón pasa por encima (hover_color)
    colores = {
        "numeros": {"fg_color": "#2c3e50", "hover_color": "#34495e"},   # Gris oscuro para números
        "operadores": {"fg_color": "#0a3d62", "hover_color": "#1e5f9c"},# Azul para operadores matemáticos
        "funciones": {"fg_color": "#145a32", "hover_color": "#1e8449"}, # Verde para funciones matemáticas
        "igual": {"fg_color": "#e67e22", "hover_color": "#d35400"},     # Naranja para el botón de igual
        "clear": {"fg_color": "#922b21", "hover_color": "#c0392b"}      # Rojo para el botón de borrar
    }

    # ---------- Creación dinámica de botones ----------
    # Posición vertical inicial para la primera fila de botones
    y = 100
    
    # Iteramos por cada fila de botones en la matriz definida anteriormente
    for fila in botones:
        # Posición horizontal inicial para cada fila
        x = 20
        
        # Iteramos por cada botón en la fila actual
        for b in fila:
            # ---------- Determinar estilo según el tipo de botón ----------
            # Asigna el estilo visual correspondiente a cada tipo de botón
            if b.isdigit() or b == ".":
                # Números y punto decimal
                estilo = colores["numeros"]
            elif b in ["+","-","*","/","^","(",")","pi","e"]:
                # Operadores aritméticos, paréntesis y constantes
                estilo = colores["operadores"]
            elif b in ["sin","cos","tan","log","ln","sqrt"]:
                # Funciones matemáticas
                estilo = colores["funciones"]
            elif b == "=":
                # Botón de igual (resultado)
                estilo = colores["igual"]
            elif b == "C":
                # Botón de borrar
                estilo = colores["clear"]
            else:
                # Estilo por defecto (por si acaso)
                estilo = colores["operadores"]

            # ---------- Creación del botón actual ----------
            btn = ctk.CTkButton(
                root,                        # Ventana padre
                text=b,                      # Texto que muestra el botón
                width=60 if b != "=" else 130, # Ancho: botón normal o más ancho para "="
                height=60,                   # Alto del botón
                font=("Consolas", 16, "bold"),# Fuente del texto
                corner_radius=8,             # Radio de las esquinas redondeadas
                fg_color=estilo["fg_color"], # Color de fondo según la categoría
                hover_color=estilo["hover_color"], # Color al pasar el ratón
                command=lambda b=b: click(b, entry) # Función que se ejecuta al hacer clic
                                          # Usamos lambda para "congelar" el valor actual de b
            )
            # Posicionamiento del botón en la ventana
            btn.place(x=x, y=y)

            # Avanzar posición horizontal para el siguiente botón
            # El botón "=" es más ancho, por lo que avanza más
            x += 65 if b != "=" else 135
            
        # Avanzar a la siguiente fila (incrementar posición vertical)
        y += 70

    # Inicia el bucle principal de la aplicación
    # Este método bloquea la ejecución hasta que se cierre la ventana
    root.mainloop()
