# tests/test_parser.py
import pytest
from backend.parser import evaluate, EvalError

def test_basic_arithmetic():
    assert evaluate("2+2") == 4
    assert evaluate("3+4*2/(1-5)^2^3") == pytest.approx(3.0001220703125)

def test_functions_and_constants():
    assert evaluate("sin(pi/2)") == pytest.approx(1.0)
    assert evaluate("sqrt(16)+ln(e)") == pytest.approx(4+1)

def test_unary_and_power():
    assert evaluate("-3+5") == 2
    assert evaluate("2^3^2") == 2**(3**2)

def test_error_cases():
    with pytest.raises(Exception):
        evaluate("2++2")
    with pytest.raises(Exception):
        evaluate("sin()")
