"""
Módulo de Análisis y Evaluación de Expresiones Matemáticas
=========================================================
Este módulo implementa un analizador léxico-sintáctico (parser) para evaluar 
expresiones matemáticas en notación infix (la notación matemática tradicional).

El proceso de evaluación ocurre en tres fases:
1. Análisis léxico: Convierte la cadena de texto en tokens (unidades léxicas)
2. Análisis sintáctico: Organiza los tokens según las reglas gramaticales
3. Evaluación: Calcula el resultado numérico de la expresión

El parser implementa el algoritmo de "Recursive Descent Parsing" con reglas
gramaticales que respetan la precedencia de operadores matemáticos:
- Paréntesis tienen la mayor precedencia
- Luego potencias (^)
- Luego multiplicación y división (* /)
- Finalmente suma y resta (+ -)

Además soporta constantes matemáticas (pi, e) y funciones (sin, cos, log, etc.)
"""

# Importamos el módulo math para acceder a funciones y constantes matemáticas
import math

# ---------- ANÁLISIS LÉXICO (tokenizer) ----------
def tokenize(expr):
    """
    Análisis léxico: Convierte una expresión matemática en cadena de texto
    a una lista de tokens (componentes léxicos).
    
    Un token es una tupla (tipo, valor) donde:
    - tipo: puede ser "NUM" (número), "ID" (identificador) u "OP" (operador)
    - valor: el valor numérico, nombre o símbolo correspondiente
    
    Parámetros:
    - expr (str): La expresión matemática a tokenizar
    
    Retorna:
    - list: Lista de tokens [(tipo, valor), ...]
    
    Ejemplo: 
    "2+sin(3)" -> [("NUM", 2), ("OP","+"), ("ID","sin"), ("OP","("), ("NUM",3), ("OP",")")]
    """
    tokens = []  # Lista para almacenar los tokens resultantes
    i = 0        # Índice para recorrer la cadena de caracteres
    
    # Recorre cada carácter de la expresión
    while i < len(expr):
        ch = expr[i]  # Carácter actual

        # Ignorar espacios en blanco (no afectan a la expresión)
        if ch.isspace():
            i += 1    # Avanza al siguiente carácter
            continue

        # Detección y procesamiento de números (enteros o decimales)
        if ch.isdigit() or (ch == "." and i+1 < len(expr) and expr[i+1].isdigit()):
            num = ""  # Variable para construir el número completo
            # Continúa leyendo dígitos o puntos decimales hasta encontrar otro tipo de carácter
            while i < len(expr) and (expr[i].isdigit() or expr[i] == "."):
                num += expr[i]  # Añade el dígito o punto al número
                i += 1          # Avanza al siguiente carácter
            # Convierte la cadena de dígitos a un valor numérico (float)
            # y agrega el token a la lista de tokens
            tokens.append(("NUM", float(num)))
            continue  # Continúa con el siguiente carácter

        # Detección y procesamiento de identificadores (nombres de funciones o constantes)
        if ch.isalpha():
            ident = ""  # Variable para construir el identificador completo
            # Continúa leyendo letras hasta encontrar otro tipo de carácter
            while i < len(expr) and expr[i].isalpha():
                ident += expr[i]  # Añade la letra al identificador
                i += 1            # Avanza al siguiente carácter
            # Convierte el identificador a minúsculas para evitar sensibilidad a mayúsculas
            # y agrega el token a la lista de tokens
            tokens.append(("ID", ident.lower()))
            continue  # Continúa con el siguiente carácter

        # Detección de operadores matemáticos y paréntesis
        if ch in "+-*/^()":
            # Agrega el operador como token
            tokens.append(("OP", ch))
            i += 1  # Avanza al siguiente carácter
            continue  # Continúa con el siguiente carácter

        # Si se encuentra un carácter que no encaja en ninguna categoría,
        # se considera un error léxico
        raise ValueError(f"Carácter no válido: {ch}")

    # Devuelve la lista completa de tokens
    return tokens


# ---------- ANÁLISIS SINTÁCTICO (parser) ----------
class Parser:
    """
    Analizador sintáctico que implementa un parser descendente recursivo.
    
    Esta clase implementa una gramática matemática que respeta las reglas
    de precedencia de operadores matemáticos, utilizando el patrón de diseño
    "Recursive Descent Parsing".
    
    La gramática implementada es:
    expr    → term ((+|-) term)*
    term    → power ((*|/) power)*
    power   → unary (^ unary)*
    unary   → (+|-) unary | primary
    primary → NUM | ID | ( expr )
    
    Donde cada método de la clase implementa una regla gramatical.
    """
    
    def __init__(self, tokens):
        """
        Inicializa el parser con una lista de tokens.
        
        Parámetros:
        - tokens (list): Lista de tokens generada por la función tokenize()
        """
        self.tokens = tokens  # Lista de tokens a procesar
        self.pos = 0          # Posición actual en la lista de tokens

    def peek(self):
        """
        Devuelve el token actual sin consumirlo (sin avanzar el puntero).
        
        Retorna:
        - tuple or None: El token actual (tipo, valor) o None si ya no hay tokens
        """
        # Si el puntero está dentro de los límites, devuelve el token actual
        # De lo contrario, devuelve None (fin de la expresión)
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def eat(self, expected=None):
        """
        Consume el token actual y avanza al siguiente.
        
        Este método es crucial para el proceso de parsing ya que:
        1. Verifica que el token actual sea el esperado (validación sintáctica)
        2. Avanza el puntero al siguiente token (progresión del parsing)
        
        Parámetros:
        - expected: Si se proporciona, verifica que el valor del token coincida
                   con este parámetro (validación sintáctica)
        
        Retorna:
        - tuple: El token consumido
        
        Lanza:
        - ValueError: Si no hay más tokens o si el token no coincide con el esperado
        """
        # Obtiene el token actual
        tok = self.peek()
        
        # Verifica si hay un token disponible
        if not tok:
            raise ValueError("Expresión incompleta")
            
        # Si se especificó un valor esperado, verifica que coincida con el valor del token
        if expected and tok[1] != expected:
            raise ValueError(f"Se esperaba {expected}, se encontró {tok}")
            
        # Avanza al siguiente token
        self.pos += 1
        
        # Devuelve el token consumido
        return tok

    def parse(self):
        """
        Punto de inicio del análisis sintáctico: evalúa la expresión completa.
        
        Este método inicia el proceso de análisis descendente recursivo,
        comenzando por la regla de mayor nivel (expr).
        
        Retorna:
        - float: El valor numérico resultante de evaluar la expresión
        
        Lanza:
        - ValueError: Si hay tokens no utilizados (síntomas extra)
        """
        # Inicia el análisis con la regla de mayor nivel (expr)
        value = self.expr()
        
        # Verifica que se hayan consumido todos los tokens
        # Si quedan tokens sin usar, hay un error sintáctico
        if self.peek():
            raise ValueError("Símbolos extra en la expresión")
            
        # Devuelve el valor resultante de la evaluación
        return value

    # Implementación de la regla gramatical: expr → term ((+|-) term)*
    def expr(self):
        """
        Analiza y evalúa términos conectados por operadores de suma (+) o resta (-).
        
        Esta regla maneja los operadores de menor precedencia (+ y -).
        
        Gramática: expr → term ((+|-) term)*
        
        Retorna:
        - float: El valor resultante de la evaluación
        """
        # Primero evaluamos el término izquierdo
        value = self.term()
        
        # Mientras haya más tokens y sean operadores de suma o resta
        while self.peek() and self.peek()[1] in ("+", "-"):
            # Consumimos el operador
            op = self.eat()[1]
            
            # Evaluamos el término derecho
            rhs = self.term()  # rhs = right-hand side (lado derecho)
            
            # Aplicamos la operación correspondiente
            value = value + rhs if op == "+" else value - rhs
            
        # Devolvemos el resultado acumulado
        return value

    # Implementación de la regla gramatical: term → power ((*|/) power)*
    def term(self):
        """
        Analiza y evalúa factores conectados por operadores de multiplicación (*) o división (/).
        
        Esta regla maneja los operadores de precedencia media (* y /).
        
        Gramática: term → power ((*|/) power)*
        
        Retorna:
        - float: El valor resultante de la evaluación
        """
        # Primero evaluamos el factor izquierdo
        value = self.power()
        
        # Mientras haya más tokens y sean operadores de multiplicación o división
        while self.peek() and self.peek()[1] in ("*", "/"):
            # Consumimos el operador
            op = self.eat()[1]
            
            # Evaluamos el factor derecho
            rhs = self.power()  # rhs = right-hand side (lado derecho)
            
            # Aplicamos la operación correspondiente
            if op == "*":
                value *= rhs  # Multiplicación
            else:
                # Verificamos división por cero
                if rhs == 0:
                    raise ZeroDivisionError("División por cero")
                value /= rhs  # División
                
        # Devolvemos el resultado acumulado
        return value

    # Implementación de la regla gramatical: power → unary (^ unary)*
    def power(self):
        """
        Analiza y evalúa expresiones de potenciación.
        
        Esta regla maneja el operador de potencia (^) que tiene mayor precedencia
        que la multiplicación/división pero menor que los paréntesis.
        
        Gramática: power → unary (^ unary)*
        
        Retorna:
        - float: El valor resultante de la evaluación
        """
        # Primero evaluamos la base (unary)
        value = self.unary()
        
        # Mientras haya más tokens y sean operadores de potencia
        while self.peek() and self.peek()[1] == "^":
            # Consumimos el operador de potencia
            self.eat("^")
            
            # Evaluamos el exponente (unary)
            rhs = self.unary()  # rhs = right-hand side (exponente)
            
            # Aplicamos la operación de potenciación
            value = value ** rhs
            
        # Devolvemos el resultado
        return value

    # Implementación de la regla gramatical: unary → (+|-) unary | primary
    def unary(self):
        """
        Analiza y evalúa operadores unarios (+/-) o una expresión primaria.
        
        Esta regla maneja operadores unarios como +x o -x.
        
        Gramática: unary → (+|-) unary | primary
        
        Retorna:
        - float: El valor resultante de la evaluación
        """
        # Verificamos si hay un operador unario (+ o -)
        if self.peek() and self.peek()[1] in ("+", "-"):
            # Consumimos el operador
            op = self.eat()[1]
            
            # Evaluamos la expresión a la que se aplica el operador
            val = self.unary()
            
            # Aplicamos el operador unario
            # (+ no afecta el valor, - lo niega)
            return val if op == "+" else -val
            
        # Si no hay operador unario, procesamos una expresión primaria
        return self.primary()

    # Implementación de la regla gramatical: primary → NUM | ID | ( expr )
    def primary(self):
        """
        Analiza y evalúa expresiones primarias: números, identificadores o expresiones entre paréntesis.
        
        Las expresiones primarias son las unidades básicas de una expresión matemática:
        - Números literales
        - Constantes matemáticas (pi, e)
        - Funciones matemáticas (sin, cos, etc.)
        - Expresiones entre paréntesis
        
        Gramática: primary → NUM | ID | ( expr )
        
        Retorna:
        - float: El valor resultante de la evaluación
        
        Lanza:
        - ValueError: Si un identificador no es reconocido o si hay un error sintáctico
        """
        # Obtenemos el token actual sin consumirlo
        tok = self.peek()
        
        # Si es un número literal, lo consumimos y devolvemos su valor
        if tok[0] == "NUM":
            self.eat()  # Consumimos el token
            return tok[1]  # Devolvemos el valor numérico

        # Si es un identificador (constante o función)
        if tok[0] == "ID":
            # Consumimos el identificador
            name = self.eat()[1]
            
            # Verificamos si es una constante matemática
            if name == "pi": return math.pi  # Constante π
            if name == "e": return math.e    # Constante e (base del logaritmo natural)
            
            # Verificamos si es una función matemática (debe tener paréntesis y argumento)
            if self.peek() and self.peek()[1] == "(":
                # Consumimos el paréntesis izquierdo
                self.eat("(")
                
                # Evaluamos la expresión dentro del paréntesis (argumento de la función)
                arg = self.expr()
                
                # Consumimos el paréntesis derecho
                self.eat(")")
                
                # Aplicamos la función matemática correspondiente
                if name == "sin": return math.sin(arg)   # Seno
                if name == "cos": return math.cos(arg)   # Coseno
                if name == "tan": return math.tan(arg)   # Tangente
                if name == "sqrt": return math.sqrt(arg) # Raíz cuadrada
                if name == "log": return math.log10(arg) # Logaritmo base 10
                if name == "ln": return math.log(arg)    # Logaritmo natural (base e)
                
                # Si el nombre no corresponde a ninguna función reconocida
                raise ValueError(f"Función no reconocida: {name}")
            
            # Si el identificador no es una constante ni una función con argumento
            raise ValueError(f"Identificador desconocido: {name}")

        # Si es un paréntesis izquierdo, evaluamos la expresión entre paréntesis
        if tok[1] == "(":
            # Consumimos el paréntesis izquierdo
            self.eat("(")
            
            # Evaluamos la expresión dentro del paréntesis
            val = self.expr()
            
            # Consumimos el paréntesis derecho
            self.eat(")")
            
            # Devolvemos el valor de la expresión
            return val

        # Si el token no encaja en ninguna de las categorías anteriores, hay un error sintáctico
        raise ValueError(f"Token inesperado: {tok}")


# ---------- API PÚBLICA DEL MÓDULO ----------
def evaluar_expresion(expr: str) -> float:
    """
    API pública del analizador matemático.
    
    Esta función es el punto de entrada principal para evaluar expresiones matemáticas
    desde otros módulos. Encapsula todo el proceso de análisis léxico, sintáctico y 
    evaluación en una única llamada de función.
    
    Parámetros:
    - expr (str): Cadena de texto con la expresión matemática a evaluar
                 Por ejemplo: "2+sin(pi/2)", "3*4^2", "log(100)+sqrt(16)"
    
    Retorna:
    - float: El valor numérico resultante de evaluar la expresión
    
    Lanza:
    - ValueError: Si hay errores léxicos o sintácticos en la expresión
    - ZeroDivisionError: Si hay una división por cero
    - Exception: Cualquier otro error durante la evaluación
    
    Ejemplo de uso:
    >>> evaluar_expresion("2+3*4")
    14.0
    >>> evaluar_expresion("sin(pi/2)")
    1.0
    """
    # Fase 1: Análisis léxico - Convierte la cadena en tokens
    tokens = tokenize(expr)
    
    # Fase 2: Análisis sintáctico - Crea un parser con los tokens
    parser = Parser(tokens)
    
    # Fase 3: Evaluación - Ejecuta el análisis y devuelve el resultado
    return parser.parse()
