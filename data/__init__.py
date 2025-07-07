"""
Data package for Maximum Clique Problem

Este pacote contém módulos para carregamento e gerenciamento de dados:
- DIMACS loader para grafos de benchmark
- Gerenciador de instâncias da atividade
- Utilitários para grafos

Uso:
    from data.dimacs_loader import DIMACSLoader
    from data.instance_manager import InstanceManager
"""

__version__ = "1.0.0"

try:
    from .dimacs_loader import DIMACSLoader
    from .instance_manager import InstanceManager
    from .graph_utils import GraphUtils
    
    __all__ = [
        'DIMACSLoader',
        'InstanceManager', 
        'GraphUtils'
    ]
except ImportError:
    __all__ = []
