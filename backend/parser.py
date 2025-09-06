# backend/parser.py
"""
Parser y evaluador de expresiones matemáticas avanzado.
Implementa:
 - Tokenizer robusto
 - Shunting-yard con soporte completo de funciones y constantes
 - Evaluador de RPN con números complejos
 - Funciones científicas avanzadas
 - Manejo de errores exhaustivo
"""

from __future__ import annotations
import math
import cmath
import statistics
from dataclasses import dataclass
from typing import List, Union, Callable, Dict, Tuple
from decimal import Decimal, getcontext
import re

# Configurar precisión decimal
getcontext().prec = 50

Number = Union[float, complex, Decimal]

# ------------------------
# Excepciones del módulo
# ------------------------
class CalcError(Exception):
    pass

class TokenizeError(CalcError):
    pass

class ParseError(CalcError):
    pass

class EvalError(CalcError):
    pass

# ------------------------
# Tokens
# ------------------------
@dataclass
class Token:
    type: str
    value: str

# ------------------------
# Operadores y funciones
# ------------------------
OPERATORS: Dict[str, Tuple[int, str]] = {
    '+': (2, 'L'),
    '-': (2, 'L'),
    '*': (3, 'L'),
    '/': (3, 'L'),
    '%': (3, 'L'),  # Módulo
    '^': (4, 'R'),  # Potencia
    '**': (4, 'R'), # Potencia alternativa
}

# Funciones matemáticas avanzadas
def safe_factorial(x):
    if isinstance(x, complex):
        return cmath.gamma(x + 1)
    if x < 0 or x != int(x) or x > 170:
        raise ValueError("Factorial solo para enteros no negativos menores a 171")
    return math.factorial(int(x))

def safe_sqrt(x):
    if isinstance(x, complex) or x < 0:
        return cmath.sqrt(x)
    return math.sqrt(x)

def safe_log(x, base=math.e):
    if isinstance(x, complex) or x <= 0:
        return cmath.log(x) if base == math.e else cmath.log(x) / cmath.log(base)
    return math.log(x) if base == math.e else math.log(x, base)

def safe_pow(base, exp):
    try:
        if isinstance(base, complex) or isinstance(exp, complex):
            return base ** exp
        if base < 0 and not isinstance(exp, int):
            return complex(base) ** exp
        return base ** exp
    except OverflowError:
        return float('inf') if base > 0 else float('-inf')

FUNCTIONS: Dict[str, Callable] = {
    # Trigonométricas
    'sin': lambda x: cmath.sin(x) if isinstance(x, complex) else math.sin(x),
    'cos': lambda x: cmath.cos(x) if isinstance(x, complex) else math.cos(x),
    'tan': lambda x: cmath.tan(x) if isinstance(x, complex) else math.tan(x),
    'asin': lambda x: cmath.asin(x) if isinstance(x, complex) or abs(x) > 1 else math.asin(x),
    'acos': lambda x: cmath.acos(x) if isinstance(x, complex) or abs(x) > 1 else math.acos(x),
    'atan': lambda x: cmath.atan(x) if isinstance(x, complex) else math.atan(x),
    'sinh': lambda x: cmath.sinh(x) if isinstance(x, complex) else math.sinh(x),
    'cosh': lambda x: cmath.cosh(x) if isinstance(x, complex) else math.cosh(x),
    'tanh': lambda x: cmath.tanh(x) if isinstance(x, complex) else math.tanh(x),
    
    # Trigonométricas en grados
    'sind': lambda x: math.sin(math.radians(x)),
    'cosd': lambda x: math.cos(math.radians(x)),
    'tand': lambda x: math.tan(math.radians(x)),
    
    # Logarítmicas y exponenciales
    'sqrt': safe_sqrt,
    'cbrt': lambda x: x ** (1/3) if x >= 0 else -((-x) ** (1/3)),
    'ln': lambda x: safe_log(x),
    'log': lambda x: safe_log(x, 10),
    'log2': lambda x: safe_log(x, 2),
    'exp': lambda x: cmath.exp(x) if isinstance(x, complex) else math.exp(x),
    'exp2': lambda x: 2 ** x,
    'exp10': lambda x: 10 ** x,
    
    # Otras funciones
    'abs': abs,
    'sign': lambda x: 1 if x > 0 else (-1 if x < 0 else 0),
    'floor': math.floor,
    'ceil': math.ceil,
    'round': round,
    'trunc': math.trunc,
    'frac': lambda x: x - math.trunc(x),
    
    # Funciones especiales
    'factorial': safe_factorial,
    'fact': safe_factorial,
    'gamma': lambda x: cmath.gamma(x) if isinstance(x, complex) else math.gamma(x),
    'lgamma': lambda x: cmath.lgamma(x) if isinstance(x, complex) else math.lgamma(x),
    
    # Funciones de números complejos
    'real': lambda x: x.real if isinstance(x, complex) else x,
    'imag': lambda x: x.imag if isinstance(x, complex) else 0,
    'conj': lambda x: x.conjugate() if isinstance(x, complex) else x,
    'phase': lambda x: cmath.phase(x) if isinstance(x, complex) else 0,
    'polar': lambda x: abs(x),
    
    # Funciones estadísticas (para listas futuras)
    'min': min,
    'max': max,
}

CONSTANTS: Dict[str, Number] = {
    'pi': math.pi,
    'π': math.pi,
    'e': math.e,
    'tau': 2 * math.pi,
    'phi': (1 + math.sqrt(5)) / 2,  # Golden ratio
    'inf': float('inf'),
    'nan': float('nan'),
    'i': 1j,
    'j': 1j,
}

# ------------------------
# Tokenizer mejorado
# ------------------------
def tokenize(expr: str) -> List[Token]:
    """Convierte la expresión en una lista de tokens."""
    if not expr.strip():
        raise TokenizeError("Expresión vacía")
    
    tokens: List[Token] = []
    i = 0
    n = len(expr)
    
    while i < n:
        ch = expr[i]
        
        if ch.isspace():
            i += 1
            continue
            
        # Números (incluyendo notación científica)
        if ch.isdigit() or (ch == '.' and i+1 < n and expr[i+1].isdigit()):
            j = i
            has_dot = False
            has_e = False
            
            while j < n:
                if expr[j].isdigit():
                    j += 1
                elif expr[j] == '.' and not has_dot and not has_e:
                    has_dot = True
                    j += 1
                elif expr[j].lower() == 'e' and not has_e and j > i:
                    has_e = True
                    j += 1
                    if j < n and expr[j] in '+-':
                        j += 1
                else:
                    break
            
            number_str = expr[i:j]
            try:
                # Validar que es un número válido
                float(number_str)
                tokens.append(Token('NUMBER', number_str))
            except ValueError:
                raise TokenizeError(f"Número mal formado: {number_str}")
            i = j
            continue
            
        # Identificadores (funciones y constantes)
        if ch.isalpha() or ch in 'πφτ':
            j = i
            while j < n and (expr[j].isalnum() or expr[j] in '_πφτ'):
                j += 1
            name = expr[i:j].lower()
            tokens.append(Token('IDENT', name))
            i = j
            continue
            
        # Operadores de dos caracteres
        if i + 1 < n:
            two_char = expr[i:i+2]
            if two_char in ['**', '==', '!=', '<=', '>=']:
                tokens.append(Token('OP', two_char))
                i += 2
                continue
                
        # Operadores de un caracter
        if ch in '+-*/%^()!,':
            if ch == '!':
                tokens.append(Token('OP', 'factorial'))
            elif ch in '+-*/%^':
                tokens.append(Token('OP', ch))
            elif ch == '(':
                tokens.append(Token('LP', ch))
            elif ch == ')':
                tokens.append(Token('RP', ch))
            elif ch == ',':
                tokens.append(Token('COMMA', ch))
            i += 1
            continue
            
        raise TokenizeError(f"Carácter no soportado: '{ch}' en posición {i}")
    
    return tokens

# ------------------------
# Shunting-yard mejorado
# ------------------------
def shunting_yard(tokens: List[Token]) -> List[Token]:
    """Convierte tokens infix a RPN usando shunting-yard."""
    output: List[Token] = []
    stack: List[Token] = []
    
    for i, tok in enumerate(tokens):
        if tok.type == 'NUMBER':
            output.append(tok)
            
        elif tok.type == 'IDENT':
            if tok.value in CONSTANTS:
                output.append(tok)
            else:
                stack.append(tok)  # Función
                
        elif tok.type == 'COMMA':
            while stack and stack[-1].type != 'LP':
                output.append(stack.pop())
            if not stack:
                raise ParseError("Coma fuera de contexto de función")
                
        elif tok.type == 'OP':
            op = tok.value
            
            # Manejar menos unario
            if op == '-' and (i == 0 or tokens[i-1].type in ['OP', 'LP', 'COMMA']):
                op = 'unary_minus'
                tok = Token('OP', op)
                prec = (5, 'R')  # Alta precedencia
            elif op == 'factorial':
                prec = (6, 'L')  # Muy alta precedencia
            else:
                prec = OPERATORS.get(op)
                if not prec:
                    raise ParseError(f"Operador desconocido: {op}")
            
            while (stack and stack[-1].type == 'OP' and 
                   stack[-1].value in OPERATORS or stack[-1].value in ['unary_minus', 'factorial']):
                top_op = stack[-1].value
                if top_op == 'unary_minus':
                    top_prec = (5, 'R')
                elif top_op == 'factorial':
                    top_prec = (6, 'L')
                else:
                    top_prec = OPERATORS[top_op]
                
                if (top_prec[0] > prec[0] or 
                    (top_prec[0] == prec[0] and prec[1] == 'L')):
                    output.append(stack.pop())
                else:
                    break
            
            stack.append(tok)
            
        elif tok.type == 'LP':
            stack.append(tok)
            
        elif tok.type == 'RP':
            while stack and stack[-1].type != 'LP':
                output.append(stack.pop())
            if not stack:
                raise ParseError("Paréntesis no balanceados")
            stack.pop()  # Quitar '('
            
            # Si hay una función en la cima, moverla a output
            if stack and stack[-1].type == 'IDENT':
                output.append(stack.pop())
    
    while stack:
        if stack[-1].type in ['LP', 'RP']:
            raise ParseError("Paréntesis no balanceados")
        output.append(stack.pop())
    
    return output

# ------------------------
# Evaluador RPN mejorado
# ------------------------
def eval_rpn(rpn: List[Token]) -> Number:
    """Evalúa una expresión en notación polaca reversa."""
    stack: List[Number] = []
    
    for tok in rpn:
        if tok.type == 'NUMBER':
            try:
                val = float(tok.value)
                stack.append(val)
            except ValueError:
                raise EvalError(f"Número inválido: {tok.value}")
                
        elif tok.type == 'IDENT':
            if tok.value in CONSTANTS:
                stack.append(CONSTANTS[tok.value])
            elif tok.value in FUNCTIONS:
                if not stack:
                    raise EvalError(f"Falta argumento para función {tok.value}")
                arg = stack.pop()
                try:
                    result = FUNCTIONS[tok.value](arg)
                    stack.append(result)
                except Exception as e:
                    raise EvalError(f"Error en función {tok.value}: {str(e)}")
            else:
                raise EvalError(f"Función/constante desconocida: {tok.value}")
                
        elif tok.type == 'OP':
            op = tok.value
            
            if op == 'unary_minus':
                if not stack:
                    raise EvalError("Falta operando para menos unario")
                stack.append(-stack.pop())
                
            elif op == 'factorial':
                if not stack:
                    raise EvalError("Falta operando para factorial")
                try:
                    result = safe_factorial(stack.pop())
                    stack.append(result)
                except Exception as e:
                    raise EvalError(f"Error en factorial: {str(e)}")
                    
            else:
                if len(stack) < 2:
                    raise EvalError(f"Operador {op} requiere dos operandos")
                    
                b = stack.pop()
                a = stack.pop()
                
                try:
                    if op == '+':
                        result = a + b
                    elif op == '-':
                        result = a - b
                    elif op == '*':
                        result = a * b
                    elif op == '/':
                        if b == 0:
                            raise EvalError("División por cero")
                        result = a / b
                    elif op == '%':
                        if b == 0:
                            raise EvalError("Módulo por cero")
                        result = a % b
                    elif op in ['^', '**']:
                        result = safe_pow(a, b)
                    else:
                        raise EvalError(f"Operador no implementado: {op}")
                        
                    stack.append(result)
                except Exception as e:
                    raise EvalError(f"Error en operación {op}: {str(e)}")
    
    if len(stack) != 1:
        raise EvalError("Expresión malformada")
    
    result = stack[0]
    
    # Limpiar resultados muy pequeños (errores de punto flotante)
    if isinstance(result, complex):
        real_part = result.real if abs(result.real) > 1e-14 else 0
        imag_part = result.imag if abs(result.imag) > 1e-14 else 0
        if imag_part == 0:
            result = real_part
        else:
            result = complex(real_part, imag_part)
    elif isinstance(result, float) and abs(result) < 1e-14:
        result = 0.0
        
    return result

# ------------------------
# Función pública principal
# ------------------------
def evaluate(expression: str) -> Number:
    """Evalúa una expresión matemática y devuelve el resultado."""
    try:
        if not expression or not expression.strip():
            raise CalcError("Expresión vacía")
            
        # Preprocesar la expresión
        expr = expression.strip()
        expr = re.sub(r'\s+', '', expr)  # Quitar espacios
        expr = expr.replace('×', '*').replace('÷', '/')  # Símbolos alternativos
        
        tokens = tokenize(expr)
        if not tokens:
            raise CalcError("No se encontraron tokens válidos")
            
        rpn = shunting_yard(tokens)
        result = eval_rpn(rpn)
        
        return result
        
    except (TokenizeError, ParseError, EvalError) as e:
        raise e
    except Exception as e:
        raise CalcError(f"Error inesperado: {str(e)}")

# ------------------------
# Funciones de utilidad
# ------------------------
def format_result(result: Number, precision: int = 12) -> str:
    """Formatea el resultado para mostrar."""
    if isinstance(result, complex):
        if result.imag == 0:
            return format_result(result.real, precision)
        real_str = f"{result.real:.{precision}g}".rstrip('0').rstrip('.')
        imag_str = f"{abs(result.imag):.{precision}g}".rstrip('0').rstrip('.')
        sign = '+' if result.imag >= 0 else '-'
        return f"{real_str}{sign}{imag_str}i"
    else:
        formatted = f"{result:.{precision}g}"
        return formatted.rstrip('0').rstrip('.')

# Prueba rápida
if __name__ == "__main__":
    test_expressions = [
        "2+2",
        "sin(pi/2)",
        "sqrt(-1)",
        "2^3^2",
        "factorial(5)",
        "ln(e^2)",
        "-(-3)",
        "1/0"
    ]
    
    for expr in test_expressions:
        try:
            result = evaluate(expr)
            print(f"{expr} = {format_result(result)}")
        except CalcError as e:
            print(f"{expr} = Error: {e}")