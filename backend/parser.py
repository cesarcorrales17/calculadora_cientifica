# backend/parser.py
"""
Parser y evaluador de expresiones matemáticas.
Implementa:
 - Tokenizer
 - Shunting-yard (con soporte de funciones y constantes)
 - Evaluador de RPN (soporta funciones, constantes, números complejos)
 - Buen manejo de errores con excepciones específicas.
"""

from __future__ import annotations
import math
import cmath
from dataclasses import dataclass
from typing import List, Union, Callable, Dict, Tuple

Number = Union[float, complex]

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
# Precedencia y asociatividad: higher precedence -> evaluated earlier.
OPERATORS: Dict[str, Tuple[int, str]] = {
    '+': (2, 'L'),
    '-': (2, 'L'),
    '*': (3, 'L'),
    '/': (3, 'L'),
    '^': (4, 'R'),  # right-associative
}

# Funciones disponibles (nombre -> callable)
FUNCTIONS: Dict[str, Callable[[Number], Number]] = {
    'sin': lambda x: math.sin(x),
    'cos': lambda x: math.cos(x),
    'tan': lambda x: math.tan(x),
    'asin': lambda x: math.asin(x),
    'acos': lambda x: math.acos(x),
    'atan': lambda x: math.atan(x),
    'sqrt': lambda x: math.sqrt(x),
    'ln': lambda x: math.log(x),
    'log': lambda x: math.log10(x),
    'exp': lambda x: math.exp(x),
    'abs': lambda x: abs(x),
    # Para factorial aceptamos solo enteros no negativos
    'fact': lambda x: math.factorial(int(x)),
}

CONSTANTS: Dict[str, Number] = {
    'pi': math.pi,
    'e': math.e,
}

# ------------------------
# Tokenizer
# ------------------------
def tokenize(expr: str) -> List[Token]:
    """Convierte la expresión en una lista de tokens.
    Soporta: números (decimales), identificadores (funciones/constantes),
    operadores, paréntesis y comas (para futuras extensiones).
    """
    tokens: List[Token] = []
    i = 0
    n = len(expr)
    while i < n:
        ch = expr[i]
        if ch.isspace():
            i += 1
            continue
        if ch.isdigit() or (ch == '.' and i+1 < n and expr[i+1].isdigit()):
            # Número (float)
            j = i
            has_dot = False
            while j < n and (expr[j].isdigit() or expr[j] == '.'):
                if expr[j] == '.':
                    if has_dot:
                        raise TokenizeError("Número mal formado con varios puntos")
                    has_dot = True
                j += 1
            tokens.append(Token('NUMBER', expr[i:j]))
            i = j
            continue
        if ch.isalpha():
            j = i
            while j < n and (expr[j].isalpha()):
                j += 1
            name = expr[i:j].lower()
            tokens.append(Token('IDENT', name))
            i = j
            continue
        if ch in '+-*/^(),':
            # Distinguimos comas/parentesis/operadores
            ttype = 'OP' if ch in '+-*/^' else 'LP' if ch == '(' else 'RP' if ch == ')' else 'COMMA'
            tokens.append(Token(ttype, ch))
            i += 1
            continue
        raise TokenizeError(f"Carácter no soportado: '{ch}' en la posición {i}")
    return tokens

# ------------------------
# Shunting-yard -> RPN
# ------------------------
def shunting_yard(tokens: List[Token]) -> List[Token]:
    """Convierte una lista de tokens infix a RPN (postfix) usando shunting-yard."""
    output: List[Token] = []
    stack: List[Token] = []
    i = 0
    n = len(tokens)
    while i < n:
        tok = tokens[i]
        if tok.type == 'NUMBER' or (tok.type == 'IDENT' and tok.value in CONSTANTS):
            output.append(tok)
        elif tok.type == 'IDENT':
            # Función (p.ej. sin( ... ))
            stack.append(tok)
        elif tok.type == 'COMMA':
            # Popers until left paren encountered
            while stack and stack[-1].type != 'LP':
                output.append(stack.pop())
            if not stack:
                raise ParseError("Coma fuera de función o paréntesis")
        elif tok.type == 'OP':
            op1 = tok.value
            # handle unary minus: if it's at start or after LP or another operator => unary
            if op1 == '-' and (i == 0 or tokens[i-1].type in ('OP','LP','COMMA')):
                # represent unary minus as 'u-' internally (higher precedence)
                op1 = 'u-'
                tok = Token('OP', op1)
                # unary minus precedence higher than ^ (as function)
                precedence = (5, 'R')
            else:
                precedence = OPERATORS.get(op1)
                if not precedence:
                    raise ParseError(f"Operador desconocido {op1}")
            # while top of stack is operator and has greater precedence, pop it
            while stack and stack[-1].type == 'OP':
                top = stack[-1].value
                top_prec = (5, 'R') if top == 'u-' else OPERATORS.get(top)
                if not top_prec:
                    break
                # Compare precedence
                if (top_prec[0] > precedence[0]) or (top_prec[0] == precedence[0] and precedence[1] == 'L'):
                    output.append(stack.pop())
                else:
                    break
            stack.append(tok)
        elif tok.type == 'LP':
            stack.append(tok)
        elif tok.type == 'RP':
            # Pop until LP
            while stack and stack[-1].type != 'LP':
                output.append(stack.pop())
            if not stack:
                raise ParseError("Paréntesis derecho no emparejado")
            stack.pop()  # pop left paren
            # If top of stack is a function, pop it to output
            if stack and stack[-1].type == 'IDENT':
                output.append(stack.pop())
        else:
            raise ParseError(f"Token no manejado en shunting yard: {tok}")
        i += 1
    while stack:
        t = stack.pop()
        if t.type in ('LP','RP'):
            raise ParseError("Paréntesis no emparejados")
        output.append(t)
    return output

# ------------------------
# Evaluador de RPN
# ------------------------
def eval_rpn(rpn: List[Token]) -> Number:
    stack: List[Number] = []
    for tok in rpn:
        if tok.type == 'NUMBER':
            stack.append(float(tok.value))
        elif tok.type == 'IDENT':
            if tok.value in CONSTANTS:
                stack.append(CONSTANTS[tok.value])
            elif tok.value in FUNCTIONS:
                # pop one argument
                if not stack:
                    raise EvalError(f"Falta argumento para la función {tok.value}")
                arg = stack.pop()
                try:
                    res = FUNCTIONS[tok.value](arg)
                except Exception as e:
                    raise EvalError(f"Error en función {tok.value}: {e}")
                stack.append(res)
            else:
                raise EvalError(f"Identificador desconocido: {tok.value}")
        elif tok.type == 'OP':
            if tok.value == 'u-':  # unary minus
                if not stack:
                    raise EvalError("Falta operando para unario -")
                a = stack.pop()
                stack.append(-a)
                continue
            if len(stack) < 2:
                raise EvalError(f"Operador {tok.value} requiere dos operandos")
            b = stack.pop()
            a = stack.pop()
            if tok.value == '+':
                stack.append(a + b)
            elif tok.value == '-':
                stack.append(a - b)
            elif tok.value == '*':
                stack.append(a * b)
            elif tok.value == '/':
                if b == 0:
                    raise EvalError("División por cero")
                stack.append(a / b)
            elif tok.value == '^':
                stack.append(a ** b)
            else:
                raise EvalError(f"Operador desconocido en evaluación: {tok.value}")
        else:
            raise EvalError(f"Token no manejado en evaluación: {tok}")
    if len(stack) != 1:
        raise EvalError("Expresión inválida, pila no reducida a un resultado")
    return stack[0]

# ------------------------
# Función pública
# ------------------------
def evaluate(expression: str) -> Number:
    """Función de alto nivel: recibe una cadena y devuelve el resultado (float o complex)."""
    if not expression or not expression.strip():
        raise CalcError("Expresión vacía")
    tokens = tokenize(expression)
    rpn = shunting_yard(tokens)
    result = eval_rpn(rpn)
    return result

# Si quieres prueba rápida
if __name__ == "__main__":
    tests = [
        "2+2",
        "3+4*2/(1-5)^2^3",
        "sin(pi/2)",
        "-3^2",
        "sqrt(9)+ln(e)"
    ]
    for t in tests:
        print(t, "=", evaluate(t))
