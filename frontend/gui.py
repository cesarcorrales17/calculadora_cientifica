# frontend/gui.py
"""
Interfaz gráfica profesional para calculadora científica.
Características:
- Diseño moderno estilo calculadora profesional
- Múltiples modos de operación
- Historial avanzado
- Gráficos de funciones
- Tema oscuro/claro
- Configuraciones personalizables
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import tkinter.font as tkFont
from typing import Optional, List, Dict, Any
import json
import os
import threading
import time

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
    import numpy as np
    HAS_MATPLOTLIB = True
except ImportError:
    HAS_MATPLOTLIB = False

from backend.parser import evaluate, CalcError, format_result

class CalculatorTheme:
    """Gestiona los temas de la calculadora."""
    
    DARK_THEME = {
        'bg': '#1a1a1a',
        'fg': '#ffffff',
        'button_bg': '#2d2d2d',
        'button_fg': '#ffffff',
        'button_active': '#404040',
        'accent': '#00a6fb',
        'error': '#ff6b6b',
        'success': '#51cf66',
        'display_bg': '#000000',
        'display_fg': '#00ff00',
        'history_bg': '#262626',
        'history_fg': '#cccccc'
    }
    
    LIGHT_THEME = {
        'bg': '#f0f0f0',
        'fg': '#000000',
        'button_bg': '#ffffff',
        'button_fg': '#000000',
        'button_active': '#e0e0e0',
        'accent': '#0066cc',
        'error': '#dc3545',
        'success': '#28a745',
        'display_bg': '#ffffff',
        'display_fg': '#000000',
        'history_bg': '#f8f9fa',
        'history_fg': '#333333'
    }

class AdvancedCalculator(tk.Tk):
    """Calculadora científica avanzada."""
    
    def __init__(self):
        super().__init__()
        
        # Configuración inicial
        self.title("ProCalc 2025 - Calculadora Científica Avanzada")
        self.geometry("800x900")
        self.minsize(600, 700)
        
        # Variables de estado
        self.current_expression = ""
        self.last_result = "0"
        self.memory_value = 0
        self.history: List[Dict[str, str]] = []
        self.current_mode = "DEG"  # DEG, RAD, GRAD
        self.precision = 12
        self.theme_name = "dark"
        self.theme = CalculatorTheme.DARK_THEME
        
        # Configurar estilo
        self.style = ttk.Style()
        self.configure_style()
        
        # Crear interfaz
        self.create_menu()
        self.create_widgets()
        self.apply_theme()
        self.load_settings()
        
        # Configurar eventos
        self.bind_events()
        
        # Protocolo de cierre
        self.protocol("WM_DELETE_WINDOW", self.on_closing)

    def configure_style(self):
        """Configura el estilo de los widgets."""
        self.style.theme_use('clam')

    def create_menu(self):
        """Crea la barra de menú."""
        menubar = tk.Menu(self)
        self.config(menu=menubar)
        
        # Menú Archivo
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Archivo", menu=file_menu)
        file_menu.add_command(label="Exportar Historial", command=self.export_history)
        file_menu.add_command(label="Importar Historial", command=self.import_history)
        file_menu.add_separator()
        file_menu.add_command(label="Salir", command=self.on_closing)
        
        # Menú Ver
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ver", menu=view_menu)
        view_menu.add_command(label="Tema Oscuro", command=lambda: self.change_theme("dark"))
        view_menu.add_command(label="Tema Claro", command=lambda: self.change_theme("light"))
        view_menu.add_separator()
        view_menu.add_command(label="Mostrar Gráficos", command=self.toggle_graph_panel)
        
        # Menú Herramientas
        tools_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Herramientas", menu=tools_menu)
        
        mode_menu = tk.Menu(tools_menu, tearoff=0)
        tools_menu.add_cascade(label="Modo Angular", menu=mode_menu)
        mode_menu.add_command(label="Grados", command=lambda: self.set_angle_mode("DEG"))
        mode_menu.add_command(label="Radianes", command=lambda: self.set_angle_mode("RAD"))
        mode_menu.add_command(label="Gradianes", command=lambda: self.set_angle_mode("GRAD"))
        
        tools_menu.add_command(label="Configuraciones", command=self.open_settings)
        
        # Menú Ayuda
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Ayuda", menu=help_menu)
        help_menu.add_command(label="Funciones Disponibles", command=self.show_functions_help)
        help_menu.add_command(label="Acerca de", command=self.show_about)

    def create_widgets(self):
        """Crea todos los widgets de la interfaz."""
        # Frame principal
        main_frame = ttk.Frame(self)
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # Crear paneles
        self.create_display_panel(main_frame)
        self.create_mode_panel(main_frame)
        self.create_button_panel(main_frame)
        self.create_history_panel(main_frame)
        
        if HAS_MATPLOTLIB:
            self.create_graph_panel(main_frame)

    def create_display_panel(self, parent):
        """Crea el panel de visualización."""
        display_frame = ttk.LabelFrame(parent, text="Display", padding=10)
        display_frame.pack(fill='x', pady=(0, 10))
        
        # Display principal
        self.display_var = tk.StringVar(value="0")
        self.display = tk.Entry(
            display_frame,
            textvariable=self.display_var,
            font=('Consolas', 24, 'bold'),
            justify='right',
            state='readonly',
            relief='sunken',
            bd=2
        )
        self.display.pack(fill='x', pady=(0, 5))
        
        # Display secundario para expresiones
        self.expression_var = tk.StringVar()
        self.expression_display = tk.Entry(
            display_frame,
            textvariable=self.expression_var,
            font=('Consolas', 12),
            justify='right',
            state='readonly',
            relief='flat'
        )
        self.expression_display.pack(fill='x')

    def create_mode_panel(self, parent):
        """Crea el panel de modo e información."""
        mode_frame = ttk.Frame(parent)
        mode_frame.pack(fill='x', pady=(0, 10))
        
        # Información de estado
        self.status_frame = ttk.Frame(mode_frame)
        self.status_frame.pack(side='left', fill='x', expand=True)
        
        self.mode_label = ttk.Label(self.status_frame, text="DEG", font=('Arial', 10, 'bold'))
        self.mode_label.pack(side='left', padx=(0, 20))
        
        self.memory_label = ttk.Label(self.status_frame, text="M: 0", font=('Arial', 10))
        self.memory_label.pack(side='left', padx=(0, 20))
        
        self.precision_label = ttk.Label(self.status_frame, text=f"Precisión: {self.precision}", font=('Arial', 10))
        self.precision_label.pack(side='left')

    def create_button_panel(self, parent):
        """Crea el panel de botones."""
        button_frame = ttk.LabelFrame(parent, text="Controles", padding=10)
        button_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Definir layout de botones
        self.create_button_layout(button_frame)

    def create_button_layout(self, parent):
        """Crea el layout de botones de la calculadora."""
        # Botones organizados por filas
        button_configs = [
            # Fila 1: Funciones de memoria y control
            [
                ('MC', 'memory', '#ff6b6b'),
                ('MR', 'memory', '#ff6b6b'), 
                ('M+', 'memory', '#ff6b6b'),
                ('M-', 'memory', '#ff6b6b'),
                ('MS', 'memory', '#ff6b6b'),
                ('C', 'clear', '#ff8c42'),
                ('CE', 'clear', '#ff8c42'),
                ('⌫', 'backspace', '#ff8c42')
            ],
            # Fila 2: Funciones matemáticas avanzadas
            [
                ('sin', 'function', '#00a6fb'),
                ('cos', 'function', '#00a6fb'),
                ('tan', 'function', '#00a6fb'),
                ('ln', 'function', '#00a6fb'),
                ('log', 'function', '#00a6fb'),
                ('√', 'function', '#00a6fb'),
                ('x²', 'function', '#00a6fb'),
                ('xʸ', 'operator', '#ffd23f')
            ],
            # Fila 3: Funciones inversas y constantes
            [
                ('asin', 'function', '#00a6fb'),
                ('acos', 'function', '#00a6fb'),
                ('atan', 'function', '#00a6fb'),
                ('eˣ', 'function', '#00a6fb'),
                ('10ˣ', 'function', '#00a6fb'),
                ('π', 'constant', '#51cf66'),
                ('e', 'constant', '#51cf66'),
                ('(', 'bracket', '#ffd23f')
            ],
            # Fila 4: Números y operadores básicos
            [
                ('7', 'number', '#ffffff'),
                ('8', 'number', '#ffffff'),
                ('9', 'number', '#ffffff'),
                ('÷', 'operator', '#ffd23f'),
                ('n!', 'function', '#00a6fb'),
                ('|x|', 'function', '#00a6fb'),
                ('±', 'function', '#00a6fb'),
                (')', 'bracket', '#ffd23f')
            ],
            # Fila 5
            [
                ('4', 'number', '#ffffff'),
                ('5', 'number', '#ffffff'),
                ('6', 'number', '#ffffff'),
                ('×', 'operator', '#ffd23f'),
                ('1/x', 'function', '#00a6fb'),
                ('%', 'operator', '#ffd23f'),
                ('Rand', 'function', '#51cf66'),
                ('ANS', 'special', '#51cf66')
            ],
            # Fila 6
            [
                ('1', 'number', '#ffffff'),
                ('2', 'number', '#ffffff'),
                ('3', 'number', '#ffffff'),
                ('-', 'operator', '#ffd23f'),
                ('x³', 'function', '#00a6fb'),
                ('∛', 'function', '#00a6fb'),
                ('Floor', 'function', '#00a6fb'),
                ('Ceil', 'function', '#00a6fb')
            ],
            # Fila 7
            [
                ('0', 'number', '#ffffff'),
                ('.', 'number', '#ffffff'),
                ('EXP', 'function', '#00a6fb'),
                ('+', 'operator', '#ffd23f'),
                ('sinh', 'function', '#00a6fb'),
                ('cosh', 'function', '#00a6fb'),
                ('tanh', 'function', '#00a6fb'),
                ('=', 'equals', '#28a745')
            ]
        ]
        
        self.buttons = {}
        
        for row_idx, row in enumerate(button_configs):
            row_frame = ttk.Frame(parent)
            row_frame.pack(fill='x', pady=2)
            
            for col_idx, (text, button_type, color) in enumerate(row):
                btn = tk.Button(
                    row_frame,
                    text=text,
                    font=('Arial', 11, 'bold'),
                    width=6,
                    height=2,
                    command=lambda t=text, bt=button_type: self.on_button_click(t, bt),
                    relief='raised',
                    bd=2
                )
                btn.pack(side='left', fill='x', expand=True, padx=1)
                self.buttons[text] = {'widget': btn, 'type': button_type, 'color': color}

    def create_history_panel(self, parent):
        """Crea el panel de historial."""
        history_frame = ttk.LabelFrame(parent, text="Historial", padding=5)
        history_frame.pack(fill='both', expand=True, pady=(0, 10))
        
        # Frame para historial y scrollbar
        hist_container = ttk.Frame(history_frame)
        hist_container.pack(fill='both', expand=True)
        
        # Texto del historial
        self.history_text = tk.Text(
            hist_container,
            height=8,
            font=('Consolas', 10),
            wrap='word',
            state='disabled'
        )
        
        # Scrollbar
        scrollbar = ttk.Scrollbar(hist_container, orient='vertical', command=self.history_text.yview)
        self.history_text.configure(yscrollcommand=scrollbar.set)
        
        self.history_text.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')
        
        # Botones del historial
        hist_buttons = ttk.Frame(history_frame)
        hist_buttons.pack(fill='x', pady=(5, 0))
        
        ttk.Button(hist_buttons, text="Limpiar Historial", command=self.clear_history).pack(side='left', padx=(0, 5))
        ttk.Button(hist_buttons, text="Copiar Último", command=self.copy_last_result).pack(side='left')

    def create_graph_panel(self, parent):
        """Crea el panel de gráficos (si matplotlib está disponible)."""
        if not HAS_MATPLOTLIB:
            return
            
        self.graph_frame = ttk.LabelFrame(parent, text="Graficador de Funciones", padding=5)
        # Inicialmente oculto
        
        # Entrada de función
        input_frame = ttk.Frame(self.graph_frame)
        input_frame.pack(fill='x', pady=(0, 5))
        
        ttk.Label(input_frame, text="f(x) =").pack(side='left')
        self.graph_entry = ttk.Entry(input_frame, font=('Consolas', 12))
        self.graph_entry.pack(side='left', fill='x', expand=True, padx=(5, 0))
        
        ttk.Button(input_frame, text="Graficar", command=self.plot_function).pack(side='right', padx=(5, 0))
        
        # Canvas para el gráfico
        self.fig, self.ax = plt.subplots(figsize=(8, 4))
        self.canvas = FigureCanvasTkAgg(self.fig, self.graph_frame)
        self.canvas.get_tk_widget().pack(fill='both', expand=True)
        
        self.graph_visible = False

    def on_button_click(self, text: str, button_type: str):
        """Maneja los clicks en los botones."""
        try:
            if button_type == 'number':
                self.handle_number_input(text)
            elif button_type == 'operator':
                self.handle_operator_input(text)
            elif button_type == 'function':
                self.handle_function_input(text)
            elif button_type == 'constant':
                self.handle_constant_input(text)
            elif button_type == 'bracket':
                self.handle_bracket_input(text)
            elif button_type == 'equals':
                self.calculate_result()
            elif button_type == 'clear':
                self.handle_clear(text)
            elif button_type == 'backspace':
                self.handle_backspace()
            elif button_type == 'memory':
                self.handle_memory(text)
            elif button_type == 'special':
                self.handle_special(text)
                
        except Exception as e:
            self.show_error(f"Error en botón {text}: {str(e)}")

    def handle_number_input(self, number: str):
        """Maneja entrada de números."""
        if number == '.' and '.' in self.current_expression.split()[-1] if self.current_expression.split() else False:
            return  # Evitar múltiples puntos decimales
            
        self.current_expression += number
        self.update_displays()

    def handle_operator_input(self, operator: str):
        """Maneja entrada de operadores."""
        # Mapear símbolos visuales a símbolos del parser
        operator_map = {
            '×': '*',
            '÷': '/',
            'xʸ': '^'
        }
        
        op = operator_map.get(operator, operator)
        
        # Evitar operadores duplicados
        if self.current_expression and self.current_expression[-1] in '+-*/^%':
            self.current_expression = self.current_expression[:-1]
            
        self.current_expression += op
        self.update_displays()

    def handle_function_input(self, function: str):
        """Maneja entrada de funciones."""
        function_map = {
            '√': 'sqrt(',
            'x²': '^2',
            'x³': '^3',
            'eˣ': 'exp(',
            '10ˣ': 'exp10(',
            'n!': '!',
            '|x|': 'abs(',
            '±': '-',
            '1/x': '1/',
            '∛': 'cbrt(',
            'Floor': 'floor(',
            'Ceil': 'ceil(',
            'Rand': 'random('
        }
        
        func = function_map.get(function, function.lower())
        
        if function in ['x²', 'x³', 'n!']:
            self.current_expression += func
        elif function == '±':
            if self.current_expression:
                self.current_expression = f"-({self.current_expression})"
            else:
                self.current_expression = "-"
        elif function == '1/x':
            if self.current_expression:
                self.current_expression = f"1/({self.current_expression})"
            else:
                self.current_expression = "1/"
        else:
            if not func.endswith('('):
                func += '('
            self.current_expression += func
            
        self.update_displays()

    def handle_constant_input(self, constant: str):
        """Maneja entrada de constantes."""
        self.current_expression += constant.lower()
        self.update_displays()

    def handle_bracket_input(self, bracket: str):
        """Maneja entrada de paréntesis."""
        self.current_expression += bracket
        self.update_displays()

    def handle_clear(self, clear_type: str):
        """Maneja operaciones de limpieza."""
        if clear_type == 'C':
            self.current_expression = ""
            self.display_var.set("0")
        elif clear_type == 'CE':
            self.current_expression = ""
            
        self.update_displays()

    def handle_backspace(self):
        """Maneja retroceso."""
        if self.current_expression:
            self.current_expression = self.current_expression[:-1]
            self.update_displays()

    def handle_memory(self, operation: str):
        """Maneja operaciones de memoria."""
        try:
            if operation == 'MC':
                self.memory_value = 0
            elif operation == 'MR':
                self.current_expression += str(self.memory_value)
            elif operation == 'MS':
                if self.current_expression:
                    result = evaluate(self.current_expression)
                    self.memory_value = float(result) if not isinstance(result, complex) else result
                else:
                    self.memory_value = float(self.display_var.get())
            elif operation == 'M+':
                if self.current_expression:
                    result = evaluate(self.current_expression)
                    self.memory_value += float(result) if not isinstance(result, complex) else result
                else:
                    self.memory_value += float(self.display_var.get())
            elif operation == 'M-':
                if self.current_expression:
                    result = evaluate(self.current_expression)
                    self.memory_value -= float(result) if not isinstance(result, complex) else result
                else:
                    self.memory_value -= float(self.display_var.get())
                    
            self.update_memory_display()
            self.update_displays()
            
        except Exception as e:
            self.show_error(f"Error en memoria: {str(e)}")

    def handle_special(self, special: str):
        """Maneja operaciones especiales."""
        if special == 'ANS':
            self.current_expression += self.last_result
            self.update_displays()

    def calculate_result(self):
        """Calcula y muestra el resultado."""
        if not self.current_expression:
            return
            
        try:
            # Ajustar para modo angular si es necesario
            expression = self.adjust_for_angle_mode(self.current_expression)
            
            result = evaluate(expression)
            formatted_result = format_result(result, self.precision)
            
            # Actualizar displays
            self.display_var.set(formatted_result)
            self.last_result = str(result)
            
            # Agregar al historial
            self.add_to_history(self.current_expression, formatted_result)
            
            # Limpiar expresión actual
            self.current_expression = ""
            self.update_displays()
            
        except CalcError as e:
            self.show_error(str(e))
        except Exception as e:
            self.show_error(f"Error inesperado: {str(e)}")

    def adjust_for_angle_mode(self, expression: str) -> str:
        """Ajusta la expresión según el modo angular."""
        if self.current_mode == "DEG":
            # Convertir funciones trigonométricas a radianes
            expression = expression.replace('sin(', 'sin(pi/180*')
            expression = expression.replace('cos(', 'cos(pi/180*')
            expression = expression.replace('tan(', 'tan(pi/180*')
        elif self.current_mode == "GRAD":
            # Convertir funciones trigonométricas de gradianes a radianes
            expression = expression.replace('sin(', 'sin(pi/200*')
            expression = expression.replace('cos(', 'cos(pi/200*')
            expression = expression.replace('tan(', 'tan(pi/200*')
            
        return expression

    def update_displays(self):
        """Actualiza los displays de la calculadora."""
        if self.current_expression:
            self.expression_var.set(self.current_expression)
            # También mostrar en display principal mientras se escribe
            try:
                temp_result = evaluate(self.adjust_for_angle_mode(self.current_expression))
                self.display_var.set(format_result(temp_result, 6))
            except:
                pass  # Mantener display anterior si hay error temporal
        else:
            self.expression_var.set("")
            if not self.display_var.get() or self.display_var.get() == "":
                self.display_var.set("0")

    def update_memory_display(self):
        """Actualiza el display de memoria."""
        if self.memory_value != 0:
            mem_str = format_result(self.memory_value, 6)
            self.memory_label.config(text=f"M: {mem_str}")
        else:
            self.memory_label.config(text="M: 0")

    def add_to_history(self, expression: str, result: str):
        """Agrega una operación al historial."""
        timestamp = time.strftime("%H:%M:%S")
        entry = {
            'time': timestamp,
            'expression': expression,
            'result': result
        }
        
        self.history.append(entry)
        
        # Mantener solo las últimas 100 operaciones
        if len(self.history) > 100:
            self.history.pop(0)
            
        self.update_history_display()

    def update_history_display(self):
        """Actualiza el display del historial."""
        self.history_text.config(state='normal')
        self.history_text.delete('1.0', 'end')
        
        for entry in self.history[-20:]:  # Mostrar solo las últimas 20
            line = f"[{entry['time']}] {entry['expression']} = {entry['result']}\n"
            self.history_text.insert('end', line)
            
        self.history_text.config(state='disabled')
        self.history_text.see('end')

    def clear_history(self):
        """Limpia el historial."""
        self.history.clear()
        self.update_history_display()

    def copy_last_result(self):
        """Copia el último resultado al clipboard."""
        if self.history:
            result = self.history[-1]['result']
            self.clipboard_clear()
            self.clipboard_append(result)
            self.show_message("Resultado copiado al portapapeles")

    def show_error(self, message: str):
        """Muestra un mensaje de error."""
        self.display_var.set("Error")
        messagebox.showerror("Error", message)

    def show_message(self, message: str):
        """Muestra un mensaje informativo."""
        messagebox.showinfo("Información", message)

    def change_theme(self, theme_name: str):
        """Cambia el tema de la calculadora."""
        self.theme_name = theme_name
        if theme_name == "dark":
            self.theme = CalculatorTheme.DARK_THEME
        else:
            self.theme = CalculatorTheme.LIGHT_THEME
        self.apply_theme()

    def apply_theme(self):
        """Aplica el tema actual a todos los widgets."""
        # Configurar colores principales
        self.configure(bg=self.theme['bg'])
        
        # Display principal
        self.display.configure(
            bg=self.theme['display_bg'],
            fg=self.theme['display_fg'],
            insertbackground=self.theme['display_fg']
        )
        
        # Display de expresión
        self.expression_display.configure(
            bg=self.theme['display_bg'],
            fg=self.theme['display_fg']
        )
        
        # Historial
        self.history_text.configure(
            bg=self.theme['history_bg'],
            fg=self.theme['history_fg'],
            insertbackground=self.theme['history_fg']
        )
        
        # Botones
        for button_info in self.buttons.values():
            widget = button_info['widget']
            widget.configure(
                bg=button_info['color'],
                fg='#000000' if button_info['color'] == '#ffffff' else '#ffffff',
                activebackground=self.theme['button_active']
            )

    def set_angle_mode(self, mode: str):
        """Establece el modo angular."""
        self.current_mode = mode
        self.mode_label.config(text=mode)

    def toggle_graph_panel(self):
        """Muestra/oculta el panel de gráficos."""
        if not HAS_MATPLOTLIB:
            self.show_message("Matplotlib no está instalado. No se pueden mostrar gráficos.")
            return
            
        if self.graph_visible:
            self.graph_frame.pack_forget()
            self.graph_visible = False
        else:
            self.graph_frame.pack(fill='both', expand=True, pady=(0, 10))
            self.graph_visible = True

    def plot_function(self):
        """Grafica una función matemática."""
        if not HAS_MATPLOTLIB:
            return
            
        function_str = self.graph_entry.get().strip()
        if not function_str:
            return
            
        try:
            # Preparar datos
            x = np.linspace(-10, 10, 1000)
            y = []
            
            for x_val in x:
                try:
                    # Reemplazar 'x' con el valor actual
                    expr = function_str.replace('x', str(x_val))
                    result = evaluate(expr)
                    y.append(float(result) if not isinstance(result, complex) else float('nan'))
                except:
                    y.append(float('nan'))
            
            # Limpiar y graficar
            self.ax.clear()
            self.ax.plot(x, y, 'b-', linewidth=2, label=f'f(x) = {function_str}')
            self.ax.grid(True, alpha=0.3)
            self.ax.axhline(y=0, color='k', linewidth=0.5)
            self.ax.axvline(x=0, color='k', linewidth=0.5)
            self.ax.set_xlabel('x')
            self.ax.set_ylabel('f(x)')
            self.ax.set_title(f'Gráfico de f(x) = {function_str}')
            self.ax.legend()
            
            self.canvas.draw()
            
        except Exception as e:
            self.show_error(f"Error al graficar: {str(e)}")

    def open_settings(self):
        """Abre la ventana de configuraciones."""
        settings_window = tk.Toplevel(self)
        settings_window.title("Configuraciones")
        settings_window.geometry("400x300")
        settings_window.transient(self)
        settings_window.grab_set()
        
        # Precisión
        ttk.Label(settings_window, text="Precisión decimal:").pack(pady=10)
        precision_var = tk.IntVar(value=self.precision)
        precision_scale = ttk.Scale(settings_window, from_=6, to=20, variable=precision_var, orient='horizontal')
        precision_scale.pack(fill='x', padx=20)
        
        # Botones
        button_frame = ttk.Frame(settings_window)
        button_frame.pack(side='bottom', fill='x', padx=10, pady=10)
        
        ttk.Button(button_frame, text="Aplicar", 
                  command=lambda: self.apply_settings(precision_var.get(), settings_window)).pack(side='right', padx=(5, 0))
        ttk.Button(button_frame, text="Cancelar", 
                  command=settings_window.destroy).pack(side='right')

    def apply_settings(self, precision: int, window: tk.Toplevel):
        """Aplica las configuraciones."""
        self.precision = precision
        self.precision_label.config(text=f"Precisión: {self.precision}")
        window.destroy()

    def show_functions_help(self):
        """Muestra ayuda sobre las funciones disponibles."""
        help_text = """
FUNCIONES DISPONIBLES:

Trigonométricas:
sin, cos, tan, asin, acos, atan
sinh, cosh, tanh

Logarítmicas:
ln (logaritmo natural), log (base 10), log2 (base 2)
exp (e^x), exp2 (2^x), exp10 (10^x)

Otras funciones:
sqrt (raíz cuadrada), cbrt (raíz cúbica)
abs (valor absoluto), sign (signo)
floor, ceil, round, trunc
factorial, gamma

Constantes:
pi (π), e, tau (2π), phi (razón áurea)
i, j (unidad imaginaria)

Operadores:
+, -, *, /, ^ (potencia), % (módulo)
"""
        
        help_window = tk.Toplevel(self)
        help_window.title("Funciones Disponibles")
        help_window.geometry("500x600")
        
        text_widget = tk.Text(help_window, wrap='word', font=('Consolas', 10))
        scrollbar = ttk.Scrollbar(help_window, orient='vertical', command=text_widget.yview)
        text_widget.configure(yscrollcommand=scrollbar.set)
        
        text_widget.insert('1.0', help_text)
        text_widget.config(state='disabled')
        
        text_widget.pack(side='left', fill='both', expand=True)
        scrollbar.pack(side='right', fill='y')

    def show_about(self):
        """Muestra información sobre la aplicación."""
        about_text = """
ProCalc 2025 - Calculadora Científica Avanzada

Versión: 2.0.0
Desarrollado por: César David Corrales Díaz

Características:
• Parser matemático avanzado
• Soporte para números complejos
• Funciones científicas completas
• Graficador de funciones
• Múltiples temas visuales
• Historial de operaciones
• Sistema de memoria
• Modos angulares (DEG/RAD/GRAD)

© 2025 - Licencia MIT
"""
        messagebox.showinfo("Acerca de ProCalc 2025", about_text)

    def export_history(self):
        """Exporta el historial a un archivo."""
        if not self.history:
            self.show_message("No hay historial para exportar")
            return
            
        filename = filedialog.asksaveasfilename(
            defaultextension=".json",
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'w', encoding='utf-8') as f:
                    json.dump(self.history, f, indent=2, ensure_ascii=False)
                self.show_message("Historial exportado exitosamente")
            except Exception as e:
                self.show_error(f"Error al exportar: {str(e)}")

    def import_history(self):
        """Importa historial desde un archivo."""
        filename = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        
        if filename:
            try:
                with open(filename, 'r', encoding='utf-8') as f:
                    imported_history = json.load(f)
                
                self.history.extend(imported_history)
                self.update_history_display()
                self.show_message("Historial importado exitosamente")
            except Exception as e:
                self.show_error(f"Error al importar: {str(e)}")

    def load_settings(self):
        """Carga configuraciones guardadas."""
        try:
            if os.path.exists('calc_settings.json'):
                with open('calc_settings.json', 'r') as f:
                    settings = json.load(f)
                    
                self.precision = settings.get('precision', 12)
                self.theme_name = settings.get('theme', 'dark')
                self.current_mode = settings.get('angle_mode', 'DEG')
                
                self.change_theme(self.theme_name)
                self.set_angle_mode(self.current_mode)
                self.precision_label.config(text=f"Precisión: {self.precision}")
        except:
            pass  # Usar configuración por defecto si hay error

    def save_settings(self):
        """Guarda las configuraciones actuales."""
        settings = {
            'precision': self.precision,
            'theme': self.theme_name,
            'angle_mode': self.current_mode
        }
        
        try:
            with open('calc_settings.json', 'w') as f:
                json.dump(settings, f, indent=2)
        except:
            pass  # Ignorar errores al guardar

    def bind_events(self):
        """Configura los eventos del teclado."""
        self.bind('<Return>', lambda e: self.calculate_result())
        self.bind('<KP_Enter>', lambda e: self.calculate_result())
        self.bind('<BackSpace>', lambda e: self.handle_backspace())
        self.bind('<Escape>', lambda e: self.handle_clear('C'))
        
        # Números y operadores del teclado
        for i in range(10):
            self.bind(str(i), lambda e, n=str(i): self.handle_number_input(n))
            
        self.bind('+', lambda e: self.handle_operator_input('+'))
        self.bind('-', lambda e: self.handle_operator_input('-'))
        self.bind('*', lambda e: self.handle_operator_input('*'))
        self.bind('/', lambda e: self.handle_operator_input('/'))
        self.bind('^', lambda e: self.handle_operator_input('^'))
        self.bind('.', lambda e: self.handle_number_input('.'))
        self.bind('(', lambda e: self.handle_bracket_input('('))
        self.bind(')', lambda e: self.handle_bracket_input(')'))

    def on_closing(self):
        """Maneja el cierre de la aplicación."""
        self.save_settings()
        self.destroy()

# Función para lanzar la calculadora
def lanzar_calculadora():
    """Lanza la aplicación de la calculadora."""
    try:
        app = AdvancedCalculator()
        app.mainloop()
    except Exception as e:
        print(f"Error al iniciar la calculadora: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    lanzar_calculadora()