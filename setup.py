#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para ProCalc 2025
Permite instalar la calculadora como un paquete de Python.
"""

from setuptools import setup, find_packages
import pathlib

# Directorio actual
HERE = pathlib.Path(__file__).parent

# El contenido del README para la descripción larga
README = (HERE / "README.md").read_text(encoding='utf-8')

# Información del paquete
setup(
    name="procalc-2025",
    version="2.0.0",
    description="Calculadora científica avanzada con interfaz gráfica moderna",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/cesarcorrales17/calculadora_cientifica",
    author="César David Corrales Díaz",
    author_email="cesar.corrales@example.com",
    license="MIT",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: Education",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: OS Independent",
        "Topic :: Scientific/Engineering :: Mathematics",
        "Topic :: Scientific/Engineering :: Visualization",
        "Topic :: Education",
        "Topic :: Utilities",
    ],
    keywords="calculator scientific math gui tkinter matplotlib",
    packages=find_packages(exclude=["tests", "tests.*"]),
    python_requires=">=3.8",
    install_requires=[
        "matplotlib>=3.9.0",
        "numpy>=1.26.0",
    ],
    extras_require={
        "full": [
            "sympy>=1.13.0",
            "scipy>=1.12.0",
            "mpmath>=1.3.0",
            "customtkinter>=5.2.0",
            "Pillow>=10.0.0",
            "pyperclip>=1.8.2",
        ],
        "dev": [
            "pytest>=8.0.0",
            "pytest-cov>=4.0.0",
            "black>=23.0.0",
            "flake8>=6.0.0",
            "mypy>=1.7.0",
        ],
        "docs": [
            "sphinx>=7.0.0",
            "sphinx-rtd-theme>=1.3.0",
        ],
    },
    entry_points={
        "console_scripts": [
            "procalc=main:main",
        ],
        "gui_scripts": [
            "procalc-gui=main:main",
        ],
    },
    package_data={
        "": ["*.txt", "*.md", "*.json", "*.png", "*.ico"],
    },
    include_package_data=True,
    zip_safe=False,
    project_urls={
        "Bug Reports": "https://github.com/cesarcorrales17/calculadora_cientifica/issues",
        "Source": "https://github.com/cesarcorrales17/calculadora_cientifica",
        "Documentation": "https://github.com/cesarcorrales17/calculadora_cientifica#readme",
    },
)