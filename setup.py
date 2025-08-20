#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Setup script para o Organizador de Extratos Bancários
"""

from setuptools import setup, find_packages
import os

# Lê o README para a descrição longa
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Lê os requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="organizador-extratos-bancarios",
    version="2.0.0",
    author="Assistente IA",
    author_email="",
    description="Organizador inteligente de extratos bancários com IA",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Intended Audience :: End Users/Desktop",
        "Topic :: Office/Business :: Financial",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Operating System :: MacOS",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pyinstaller>=5.0",
            "pytest>=6.0",
            "black",
            "flake8",
        ],
        "build": [
            "pyinstaller>=5.0",
            "auto-py-to-exe",
        ]
    },
    entry_points={
        "console_scripts": [
            "organizador-extratos=organizador_extratos_gui:main",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.json"],
    },
    keywords="extratos bancários organização IA gemini pdf ofx",
    project_urls={
        "Bug Reports": "",
        "Source": "",
        "Documentation": "",
    },
)