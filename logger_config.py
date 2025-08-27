#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
📝 Configuração de Logger
Organizador de Extratos Bancários

Sistema de logging para toda a aplicação.
"""

import logging
import os
from pathlib import Path

def get_app_logger(name: str = "organizador") -> logging.Logger:
    """
    Cria ou retorna um logger configurado para a aplicação
    
    Args:
        name: Nome do logger
        
    Returns:
        Logger configurado
    """
    # Configura o logger
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Evita duplicação de handlers
    if not logger.handlers:
        # Cria handler para console
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Cria handler para arquivo
        log_dir = Path.home() / ".organizador_extratos" / "logs"
        log_dir.mkdir(parents=True, exist_ok=True)
        log_file = log_dir / f"{name}.log"
        
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setLevel(logging.INFO)
        
        # Cria formatador
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        console_handler.setFormatter(formatter)
        file_handler.setFormatter(formatter)
        
        # Adiciona handlers ao logger
        logger.addHandler(console_handler)
        logger.addHandler(file_handler)
    
    return logger

if __name__ == "__main__":
    # Teste do logger
    logger = get_app_logger("test")
    logger.info("Logger configurado com sucesso!")
    logger.warning("Este é um aviso de teste")
    logger.error("Este é um erro de teste")