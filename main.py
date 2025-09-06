#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ProCalc 2025 - Calculadora Científica Avanzada
Punto de entrada principal de la aplicación.

Autor: César David Corrales Díaz
Versión: 2.0.0
Licencia: MIT
"""

import sys
import os
import logging
from pathlib import Path

# Agregar el directorio del proyecto al path de Python
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

def setup_logging():
    """Configura el sistema de logging."""
    log_dir = project_root / "logs"
    log_dir.mkdir(exist_ok=True)
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler(log_dir / "calculator.log", encoding='utf-8'),
            logging.StreamHandler(sys.stdout)
        ]
    )

def check_dependencies():
    """Verifica las dependencias requeridas."""
    missing_deps = []
    
    try:
        import tkinter
    except ImportError:
        missing_deps.append("tkinter")
    
    # Dependencias opcionales
    optional_deps = []
    
    try:
        import matplotlib
    except ImportError:
        optional_deps.append("matplotlib")
    
    try:
        import numpy
    except ImportError:
        optional_deps.append("numpy")
    
    if missing_deps:
        print("❌ DEPENDENCIAS FALTANTES:")
        for dep in missing_deps:
            print(f"   - {dep}")
        print("\nPor favor instala las dependencias faltantes:")
        print("pip install -r requirements.txt")
        return False
    
    if optional_deps:
        print("⚠️  DEPENDENCIAS OPCIONALES FALTANTES:")
        for dep in optional_deps:
            print(f"   - {dep}")
        print("Algunas funciones pueden no estar disponibles.")
        print("Para funcionalidad completa: pip install -r requirements.txt")
    
    print("✅ Dependencias verificadas correctamente")
    return True

def print_welcome_message():
    """Imprime mensaje de bienvenida."""
    welcome_text = """
╔══════════════════════════════════════════════════════════════╗
║                    ProCalc 2025                              ║
║              Calculadora Científica Avanzada                ║
║                                                              ║
║  🧮 Funciones científicas completas                          ║
║  📊 Graficador de funciones integrado                       ║
║  🎨 Interfaz moderna con temas                              ║
║  📜 Historial de operaciones                                ║
║  💾 Sistema de memoria avanzado                             ║
║  🌐 Soporte para números complejos                         ║
║                                                              ║
║  Autor: César David Corrales Díaz                           ║
║  Versión: 2.0.0 | Licencia: MIT                            ║
╚══════════════════════════════════════════════════════════════╝
"""
    print(welcome_text)

def main():
    """Función principal de la aplicación."""
    try:
        # Configurar logging
        setup_logging()
        logger = logging.getLogger(__name__)
        
        print_welcome_message()
        
        # Verificar dependencias
        if not check_dependencies():
            input("\nPresiona Enter para continuar...")
            sys.exit(1)
        
        print("\n🚀 Iniciando ProCalc 2025...\n")
        
        # Importar y lanzar la calculadora
        try:
            from frontend.gui import lanzar_calculadora
            logger.info("Iniciando la aplicación de calculadora")
            lanzar_calculadora()
            
        except ImportError as e:
            logger.error(f"Error al importar módulos: {e}")
            print(f"❌ Error al importar módulos: {e}")
            print("Asegúrate de que todos los archivos estén en su lugar correcto.")
            sys.exit(1)
            
        except Exception as e:
            logger.error(f"Error inesperado al iniciar la aplicación: {e}")
            print(f"❌ Error inesperado: {e}")
            import traceback
            traceback.print_exc()
            sys.exit(1)
    
    except KeyboardInterrupt:
        print("\n\n👋 Aplicación interrumpida por el usuario")
        sys.exit(0)
    
    except Exception as e:
        print(f"❌ Error crítico: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()