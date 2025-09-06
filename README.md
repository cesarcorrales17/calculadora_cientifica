# ProCalc 2025 🧮

## Calculadora Científica Avanzada

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Tests](https://img.shields.io/badge/Tests-Passing-brightgreen.svg)]()

Una calculadora científica profesional desarrollada en Python con interfaz gráfica moderna, funciones matemáticas avanzadas y capacidades de graficación.

![ProCalc 2025 Screenshot](https://via.placeholder.com/800x600/1a1a1a/00a6fb?text=ProCalc+2025)

## ✨ Características Principales

### 🎯 Funcionalidades Core
- **Parser matemático avanzado** con soporte para expresiones complejas
- **Interfaz gráfica moderna** con tema oscuro/claro
- **Historial de operaciones** con exportación/importación
- **Sistema de memoria** completo (MC, MR, M+, M-, MS)
- **Múltiples modos angulares** (Grados, Radianes, Gradianes)
- **Soporte para números complejos**
- **Precisión configurable** hasta 20 dígitos decimales

### 📊 Funciones Matemáticas

#### Operaciones Básicas
- Suma (+), Resta (-), Multiplicación (×), División (÷)
- Potenciación (^), Módulo (%)
- Paréntesis anidados

#### Funciones Trigonométricas
- `sin`, `cos`, `tan` (con soporte para grados/radianes)
- `asin`, `acos`, `atan` (inversas)
- `sinh`, `cosh`, `tanh` (hiperbólicas)

#### Funciones Logarítmicas y Exponenciales
- `ln` (logaritmo natural), `log` (base 10), `log2` (base 2)
- `exp` (e^x), `exp2` (2^x), `exp10` (10^x)
- `sqrt` (raíz cuadrada), `cbrt` (raíz cúbica)

#### Funciones Especiales
- `factorial` / `fact` (factorial)
- `gamma` (función gamma)
- `abs` (valor absoluto), `sign` (signo)
- `floor`, `ceil`, `round`, `trunc`

#### Constantes Matemáticas
- `pi` (π ≈ 3.14159...)
- `e` (número de Euler ≈ 2.71828...)
- `tau` (2π ≈ 6.28318...)
- `phi` (razón áurea ≈ 1.618...)
- `i`, `j` (unidad imaginaria)

### 📈 Graficador de Funciones
- Visualización de funciones matemáticas
- Zoom y navegación interactiva
- Múltiples funciones en el mismo gráfico
- Exportación de gráficos

### 🎨 Interfaz de Usuario
- **Diseño profesional** inspirado en calculadoras Casio/HP
- **Temas personalizables** (oscuro/claro)
- **Atajos de teclado** completos
- **Display dual** (expresión + resultado)
- **Panel de estado** con modo angular y memoria

## 🚀 Instalación

### Requisitos del Sistema
- Python 3.8 o superior
- Sistema operativo: Windows, macOS, Linux

### Instalación Rápida

```bash
# Clonar el repositorio
git clone https://github.com/cesarcorrales17/calculadora_cientifica.git
cd calculadora_cientifica

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar la aplicación
python main.py
```

### Instalación de Desarrollo

```bash
# Instalar dependencias de desarrollo
pip install -r requirements.txt
pip install pytest pytest-cov black flake8 mypy

# Ejecutar tests
pytest tests/ -v

# Formatear código
black backend/ frontend/ tests/

# Linting
flake8 backend/ frontend/
```

## 📖 Uso

### Inicio Rápido

1. **Ejecutar la aplicación:**
   ```bash
   python main.py
   ```

2. **Operaciones básicas:**
   - Usar botones o teclado para introducir expresiones
   - Presionar `=` o `Enter` para calcular
   - El historial se mantiene automáticamente

3. **Funciones avanzadas:**
   ```
   sin(pi/2)      # Resultado: 1
   sqrt(16) + 5   # Resultado: 9
   2^(3+1)        # Resultado: 16
   factorial(5)   # Resultado: 120
   ```

### Atajos de Teclado

| Tecla | Acción |
|-------|--------|
| `0-9` | Números |
| `+`, `-`, `*`, `/` | Operadores básicos |
| `^` | Potenciación |
| `.` | Punto decimal |
| `(`, `)` | Paréntesis |
| `Enter` | Calcular |
| `Backspace` | Borrar último carácter |
| `Escape` | Limpiar todo |

### Ejemplos de Uso

#### Cálculos Básicos
```
2 + 3 * 4        # = 14
(2 + 3) * 4      # = 20
10 / (2 + 3)     # = 2
```

#### Funciones Científicas
```
sin(30)          # = 0.5 (en modo grados)
ln(e^2)          # = 2
sqrt(-1)         # = i (número complejo)
```

#### Constantes
```
2 * pi           # = 6.283...
e^1              # = 2.718...
phi - 1          # = 0.618...
```

## 🏗️ Arquitectura

### Estructura del Proyecto
```
calculadora_cientifica/
├── backend/
│   ├── __init__.py
│   └── parser.py           # Parser matemático y evaluador
├── frontend/
│   ├── __init__.py
│   └── gui.py             # Interfaz gráfica
├── tests/
│   ├── __init__.py
│   └── test_parser.py     # Suite de tests
├── logs/                  # Archivos de log (generados)
├── main.py               # Punto de entrada
├── requirements.txt      # Dependencias
├── README.md            # Este archivo
└── LICENSE              # Licencia MIT
```

### Componentes Principales

#### Backend (`backend/parser.py`)
- **Tokenizer**: Convierte expresiones en tokens
- **Shunting-yard**: Convierte infix a RPN (notación polaca reversa)
- **Evaluador RPN**: Calcula el resultado final
- **Manejo de errores**: Excepciones específicas y descriptivas

#### Frontend (`frontend/gui.py`)
- **Interfaz principal**: Ventana de la calculadora
- **Sistema de temas**: Manejo de colores y estilos
- **Gestión de eventos**: Clicks y teclado
- **Historial**: Almacenamiento y visualización de operaciones
- **Graficador**: Visualización de funciones (opcional)

## 🧪 Testing

El proyecto incluye una suite completa de tests que cubre:

- **Operaciones aritméticas básicas**
- **Funciones trigonométricas e hiperbólicas**
- **Funciones logarítmicas y exponenciales**
- **Manejo de números complejos**
- **Casos extremos y manejo de errores**
- **Tests de integración**

```bash
# Ejecutar todos los tests
pytest tests/ -v

# Tests con cobertura
pytest tests/ --cov=backend --cov=frontend

# Test específico
pytest tests/test_parser.py::TestBasicArithmetic -v
```

## 🎨 Personalización

### Temas
La calculadora soporta temas personalizables:

- **Tema Oscuro**: Interfaz moderna con fondo negro
- **Tema Claro**: Interfaz clásica con fondo blanco

### Configuraciones
- **Precisión decimal**: 6-20 dígitos
- **Modo angular**: Grados, Radianes, Gradianes
- **Formato de números**: Científico, Decimal

## 📊 Características Avanzadas

### Graficador de Funciones
```python
# Ejemplos de funciones para graficar
f(x) = sin(x)
f(x) = x^2 + 2*x - 1
f(x) = exp(-x^2)
f(x) = ln(x)
```

### Números Complejos
```python
sqrt(-1)         # = i
(1+2i) * (3-i)   # = 5+5i
abs(3+4i)        # = 5
```

### Historial Avanzado
- Almacenamiento automático de operaciones
- Exportación a archivos JSON
- Importación de historiales previos
- Búsqueda en el historial

## 🤝 Contribución

¡Las contribuciones son bienvenidas! Por favor:

1. Fork el repositorio
2. Crea una rama para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

### Estándares de Código
- Usar Black para formateo: `black .`
- Seguir PEP 8
- Añadir tests para nuevas funcionalidades
- Documentar funciones y clases

## 📝 Licencia

Este proyecto está bajo la Licencia MIT. Ver el archivo [LICENSE](LICENSE) para más detalles.

## 👨‍💻 Autor

**César David Corrales Díaz**
- GitHub: [@cesarcorrales17](https://github.com/cesarcorrales17)
- Email: cesarcorrales00@gmail.com

## 📈 Roadmap

### Versión 2.1 (Próximamente)
- [ ] Calculadora de matrices
- [ ] Resolución de ecuaciones
- [ ] Más funciones estadísticas
- [ ] Plugin system
- [ ] Exportación a LaTeX

### Versión 2.2
- [ ] Calculadora programable
- [ ] Interfaz web opcional
- [ ] API REST
- [ ] Base de datos para historial
- [ ] Sincronización en la nube