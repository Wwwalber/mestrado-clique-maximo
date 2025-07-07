"""
Configuração de logging para o projeto

Este módulo centraliza a configuração de logging para todos os componentes.
"""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


def setup_logging(
    level: str = 'INFO',
    log_file: Optional[str] = None,
    console_output: bool = True,
    format_style: str = 'detailed'
) -> logging.Logger:
    """
    Configurar sistema de logging do projeto.
    
    Args:
        level: Nível de logging ('DEBUG', 'INFO', 'WARNING', 'ERROR')
        log_file: Arquivo para salvar logs (None para não salvar)
        console_output: Se deve imprimir logs no console
        format_style: Estilo do formato ('simple', 'detailed', 'timestamp')
        
    Returns:
        Logger configurado
    """
    
    # Limpar handlers existentes
    logging.getLogger().handlers.clear()
    
    # Definir formatos
    formats = {
        'simple': '%(levelname)s: %(message)s',
        'detailed': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        'timestamp': '%(asctime)s [%(levelname)s] %(message)s'
    }
    
    formatter = logging.Formatter(
        formats.get(format_style, formats['detailed']),
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Configurar nível
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    # Criar logger principal
    logger = logging.getLogger('clique_maximum')
    logger.setLevel(log_level)
    
    # Handler para console
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Handler para arquivo
    if log_file:
        # Criar diretório se necessário
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        
        # Log inicial no arquivo
        logger.info(f"=== INÍCIO DA SESSÃO: {datetime.now()} ===")
    
    return logger


def get_default_log_file() -> str:
    """
    Obter nome padrão do arquivo de log baseado na data/hora atual.
    
    Returns:
        Caminho do arquivo de log
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    return f"data_files/logs/clique_maximum_{timestamp}.log"


def setup_algorithm_logging(algorithm_name: str, verbose: bool = True) -> logging.Logger:
    """
    Configurar logging específico para um algoritmo.
    
    Args:
        algorithm_name: Nome do algoritmo
        verbose: Se deve ser verboso
        
    Returns:
        Logger configurado para o algoritmo
    """
    level = 'INFO' if verbose else 'WARNING'
    log_file = f"data_files/logs/{algorithm_name}_execution.log"
    
    return setup_logging(
        level=level,
        log_file=log_file,
        console_output=verbose,
        format_style='timestamp'
    )


def setup_experiment_logging(experiment_name: str) -> logging.Logger:
    """
    Configurar logging para experimentos.
    
    Args:
        experiment_name: Nome do experimento
        
    Returns:
        Logger configurado para o experimento
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    log_file = f"data_files/logs/experiment_{experiment_name}_{timestamp}.log"
    
    return setup_logging(
        level='INFO',
        log_file=log_file,
        console_output=True,
        format_style='detailed'
    )


# Configurações pré-definidas
LOGGING_CONFIGS = {
    'development': {
        'level': 'DEBUG',
        'console_output': True,
        'format_style': 'detailed'
    },
    'production': {
        'level': 'INFO',
        'console_output': True,
        'format_style': 'timestamp'
    },
    'silent': {
        'level': 'ERROR',
        'console_output': False,
        'format_style': 'simple'
    },
    'verbose': {
        'level': 'DEBUG',
        'console_output': True,
        'format_style': 'detailed'
    }
}
