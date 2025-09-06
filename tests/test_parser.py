# tests/test_parser.py
"""
Suite de pruebas completa para el parser matemático.
Cubre todos los casos de uso y edge cases.
"""

import pytest
import math
import cmath
import sys
from pathlib import Path

# Agregar el directorio padre al path para importar módulos
sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.parser import (
    evaluate, 
    format_result,
    tokenize, 
    shunting_yard, 
    eval_rpn,
    CalcError, 
    TokenizeError, 
    ParseError, 
    EvalError,
    Token
)

class TestBasicArithmetic:
    """Tests para operaciones aritméticas básicas."""
    
    def test_addition(self):
        assert evaluate("2+3") == 5
        assert evaluate("0+0") == 0
        assert evaluate("-5+3") == -2
        
    def test_subtraction(self):
        assert evaluate("5-3") == 2
        assert evaluate("0-5") == -5
        assert evaluate("-3-2") == -5
        
    def test_multiplication(self):
        assert evaluate("3*4") == 12
        assert evaluate("-2*3") == -6
        assert evaluate("0*100") == 0
        
    def test_division(self):
        assert evaluate("10/2") == 5
        assert evaluate("1/4") == 0.25
        assert evaluate("-8/2") == -4
        
    def test_division_by_zero(self):
        with pytest.raises(EvalError, match="División por cero"):
            evaluate("1/0")
            
    def test_power(self):
        assert evaluate("2^3") == 8
        assert evaluate("5^0") == 1
        assert evaluate("9^0.5") == 3
        
    def test_modulo(self):
        assert evaluate("10%3") == 1
        assert evaluate("7%7") == 0
        
    def test_operator_precedence(self):
        assert evaluate("2+3*4") == 14  # No 20
        assert evaluate("10-6/2") == 7   # No 2
        assert evaluate("2^3^2") == 512  # Right associative: 2^(3^2)

class TestComplexExpressions:
    """Tests para expresiones complejas."""
    
    def test_parentheses(self):
        assert evaluate("(2+3)*4") == 20
        assert evaluate("2*(3+4)") == 14
        assert evaluate("((2+3)*4)/5") == 4
        
    def test_nested_parentheses(self):
        assert evaluate("2*((3+4)*2)") == 28
        assert evaluate("(((1+2)*3)+4)*5") == 65
        
    def test_unary_minus(self):
        assert evaluate("-5") == -5
        assert evaluate("-(3+2)") == -5
        assert evaluate("-(-5)") == 5
        assert evaluate("2*-3") == -6
        
    def test_scientific_notation(self):
        assert evaluate("1e3") == 1000
        assert evaluate("2.5e2") == 250
        assert evaluate("1e-3") == 0.001

class TestTrigonometricFunctions:
    """Tests para funciones trigonométricas."""
    
    def test_sin(self):
        assert abs(evaluate("sin(0)") - 0) < 1e-10
        assert abs(evaluate("sin(pi/2)") - 1) < 1e-10
        assert abs(evaluate("sin(pi)") - 0) < 1e-10
        
    def test_cos(self):
        assert abs(evaluate("cos(0)") - 1) < 1e-10
        assert abs(evaluate("cos(pi/2)") - 0) < 1e-10
        assert abs(evaluate("cos(pi)") - (-1)) < 1e-10
        
    def test_tan(self):
        assert abs(evaluate("tan(0)") - 0) < 1e-10
        assert abs(evaluate("tan(pi/4)") - 1) < 1e-10
        
    def test_inverse_trig(self):
        assert abs(evaluate("asin(0)") - 0) < 1e-10
        assert abs(evaluate("acos(1)") - 0) < 1e-10
        assert abs(evaluate("atan(1)") - math.pi/4) < 1e-10
        
    def test_hyperbolic(self):
        assert abs(evaluate("sinh(0)") - 0) < 1e-10
        assert abs(evaluate("cosh(0)") - 1) < 1e-10
        assert abs(evaluate("tanh(0)") - 0) < 1e-10

class TestLogarithmicFunctions:
    """Tests para funciones logarítmicas y exponenciales."""
    
    def test_natural_log(self):
        assert abs(evaluate("ln(1)") - 0) < 1e-10
        assert abs(evaluate("ln(e)") - 1) < 1e-10
        assert abs(evaluate("ln(e^2)") - 2) < 1e-10
        
    def test_log_base_10(self):
        assert abs(evaluate("log(1)") - 0) < 1e-10
        assert abs(evaluate("log(10)") - 1) < 1e-10
        assert abs(evaluate("log(100)") - 2) < 1e-10
        
    def test_exponential(self):
        assert abs(evaluate("exp(0)") - 1) < 1e-10
        assert abs(evaluate("exp(1)") - math.e) < 1e-10
        
    def test_sqrt(self):
        assert evaluate("sqrt(4)") == 2
        assert evaluate("sqrt(9)") == 3
        assert abs(evaluate("sqrt(2)") - math.sqrt(2)) < 1e-10

class TestConstants:
    """Tests para constantes matemáticas."""
    
    def test_pi(self):
        assert abs(evaluate("pi") - math.pi) < 1e-10
        assert abs(evaluate("2*pi") - 2*math.pi) < 1e-10
        
    def test_e(self):
        assert abs(evaluate("e") - math.e) < 1e-10
        assert abs(evaluate("e^2") - math.e**2) < 1e-10
        
    def test_other_constants(self):
        assert abs(evaluate("tau") - 2*math.pi) < 1e-10
        assert abs(evaluate("phi") - (1 + math.sqrt(5))/2) < 1e-10

class TestSpecialFunctions:
    """Tests para funciones especiales."""
    
    def test_factorial(self):
        assert evaluate("factorial(0)") == 1
        assert evaluate("factorial(5)") == 120
        assert evaluate("fact(4)") == 24
        
    def test_abs(self):
        assert evaluate("abs(-5)") == 5
        assert evaluate("abs(3)") == 3
        assert evaluate("abs(0)") == 0
        
    def test_floor_ceil(self):
        assert evaluate("floor(3.7)") == 3
        assert evaluate("ceil(3.2)") == 4
        assert evaluate("round(3.6)") == 4
        
    def test_sign(self):
        assert evaluate("sign(5)") == 1
        assert evaluate("sign(-3)") == -1
        assert evaluate("sign(0)") == 0

class TestComplexNumbers:
    """Tests para números complejos."""
    
    def test_imaginary_unit(self):
        result = evaluate("i")
        assert isinstance(result, complex)
        assert result == 1j
        
    def test_complex_arithmetic(self):
        result = evaluate("1+i")
        assert result == complex(1, 1)
        
    def test_complex_functions(self):
        result = evaluate("sqrt(-1)")
        assert isinstance(result, complex)
        assert abs(result - 1j) < 1e-10

class TestErrorHandling:
    """Tests para manejo de errores."""
    
    def test_empty_expression(self):
        with pytest.raises(CalcError, match="Expresión vacía"):
            evaluate("")
            
    def test_invalid_syntax(self):
        with pytest.raises(CalcError):
            evaluate("2++3")
            
    def test_unmatched_parentheses(self):
        with pytest.raises(ParseError, match="Paréntesis no balanceados"):
            evaluate("(2+3")
            
    def test_unknown_function(self):
        with pytest.raises(EvalError, match="Función/constante desconocida"):
            evaluate("unknown_func(5)")
            
    def test_invalid_character(self):
        with pytest.raises(TokenizeError, match="Carácter no soportado"):
            evaluate("2@3")

class TestTokenizer:
    """Tests específicos para el tokenizador."""
    
    def test_number_tokenization(self):
        tokens = tokenize("123.456")
        assert len(tokens) == 1
        assert tokens[0].type == 'NUMBER'
        assert tokens[0].value == '123.456'
        
    def test_function_tokenization(self):
        tokens = tokenize("sin(x)")
        assert tokens[0].type == 'IDENT'
        assert tokens[0].value == 'sin'
        
    def test_operator_tokenization(self):
        tokens = tokenize("2+3*4")
        operators = [t for t in tokens if t.type == 'OP']
        assert len(operators) == 2
        assert operators[0].value == '+'
        assert operators[1].value == '*'

class TestShuntingYard:
    """Tests para el algoritmo Shunting-yard."""
    
    def test_simple_conversion(self):
        tokens = tokenize("2+3")
        rpn = shunting_yard(tokens)
        assert len(rpn) == 3
        assert rpn[0].value == '2'
        assert rpn[1].value == '3'
        assert rpn[2].value == '+'
        
    def test_precedence_conversion(self):
        tokens = tokenize("2+3*4")
        rpn = shunting_yard(tokens)
        # Debería ser: 2 3 4 * +
        assert rpn[0].value == '2'
        assert rpn[1].value == '3'
        assert rpn[2].value == '4'
        assert rpn[3].value == '*'
        assert rpn[4].value == '+'

class TestRPNEvaluator:
    """Tests para el evaluador RPN."""
    
    def test_simple_evaluation(self):
        tokens = [
            Token('NUMBER', '2'),
            Token('NUMBER', '3'),
            Token('OP', '+')
        ]
        result = eval_rpn(tokens)
        assert result == 5

class TestFormatting:
    """Tests para formateo de resultados."""
    
    def test_integer_formatting(self):
        assert format_result(5.0) == "5"
        
    def test_float_formatting(self):
        assert format_result(3.14159, 3) == "3.14"
        
    def test_complex_formatting(self):
        result = format_result(complex(1, 2))
        assert "1" in result and "2i" in result
        
    def test_scientific_notation(self):
        result = format_result(1e6)
        assert "1e" in result.lower() or "1000000" in result

class TestEdgeCases:
    """Tests para casos extremos y edge cases."""
    
    def test_very_large_numbers(self):
        result = evaluate("10^100")
        assert result == 10**100
        
    def test_very_small_numbers(self):
        result = evaluate("10^-10")
        assert abs(result - 1e-10) < 1e-15
        
    def test_nested_functions(self):
        result = evaluate("sin(cos(pi/4))")
        expected = math.sin(math.cos(math.pi/4))
        assert abs(result - expected) < 1e-10
        
    def test_multiple_unary_minus(self):
        assert evaluate("--5") == 5
        assert evaluate("---5") == -5
        
    def test_factorial_edge_cases(self):
        assert evaluate("factorial(0)") == 1
        assert evaluate("factorial(1)") == 1
        
        with pytest.raises(EvalError):
            evaluate("factorial(-1)")

class TestPerformance:
    """Tests de rendimiento básicos."""
    
    def test_complex_expression_performance(self):
        """Test que una expresión compleja se evalúe en tiempo razonable."""
        import time
        
        complex_expr = "sin(cos(tan(ln(exp(sqrt(2^3))))))"
        
        start = time.time()
        result = evaluate(complex_expr)
        end = time.time()
        
        assert end - start < 1.0  # Debería tomar menos de 1 segundo
        assert isinstance(result, (int, float, complex))

# Tests de integración
class TestIntegration:
    """Tests de integración para verificar que todo funciona junto."""
    
    def test_calculator_workflow(self):
        """Simula un workflow típico de uso de la calculadora."""
        # Operación básica
        result1 = evaluate("2+2")
        assert result1 == 4
        
        # Usar resultado anterior (simulado)
        result2 = evaluate(f"{result1}*3")
        assert result2 == 12
        
        # Función científica
        result3 = evaluate("sqrt(144)")
        assert result3 == 12
        
        # Expresión compleja
        result4 = evaluate("sin(pi/2) + cos(0)")
        assert abs(result4 - 2) < 1e-10

if __name__ == "__main__":
    # Ejecutar todos los tests
    pytest.main([__file__, "-v", "--tb=short"])