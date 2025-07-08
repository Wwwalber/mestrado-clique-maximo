"""
Configuration package for Maximum Clique Problem

Este pacote contém configurações centralizadas:
- Parâmetros dos algoritmos
- Configurações de experimentos
- Configuração de logs
"""

__version__ = "1.0.0"

try:
    from .algorithm_params import AlgorithmParams
    from .experiment_config import ExperimentConfig
    from .logging_config import setup_logging
    
    __all__ = [
        'AlgorithmParams',
        'ExperimentConfig',
        'setup_logging'
    ]
except ImportError:
    __all__ = []
