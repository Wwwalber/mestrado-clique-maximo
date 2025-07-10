"""
Parâmetros padrão dos algoritmos

Este módulo centraliza os parâmetros de configuração para os diferentes
algoritmos de clique máximo.
"""

from dataclasses import dataclass
from typing import Optional


@dataclass
class CliSATParams:
    """Parâmetros para o algoritmo CliSAT."""
    time_limit: float = 600.0           # Limite de tempo em segundos (10 minutos) - OTIMIZADO PARA 11H
    log_interval: int = 1000            # Intervalo para logs (nós processados)
    time_interval: float = 30.0         # Intervalo de tempo para logs (segundos)
    monitor_mode: str = 'log'           # Modo de monitoramento
    
    def to_dict(self):
        """Converter para dicionário."""
        return {
            'time_limit': self.time_limit,
            'log_interval': self.log_interval,
            'time_interval': self.time_interval,
            'monitor_mode': self.monitor_mode
        }


@dataclass
class GRASPParams:
    """Parâmetros para o algoritmo GRASP."""
    alpha: float = 0.3                  # Parâmetro de aleatoriedade (0=guloso, 1=aleatório)
    max_iterations: int = 1000          # Número máximo de iterações
    time_limit: float = 180.0           # Limite de tempo em segundos (3 min) - OTIMIZADO PARA 11H
    max_no_improvement: int = 100       # Máximo de iterações sem melhoria
    local_search_intensity: int = 3     # Intensidade da busca local
    seed: Optional[int] = None          # Semente para reprodutibilidade
    verbose: bool = True                # Imprimir progresso
    
    def to_dict(self):
        """Converter para dicionário."""
        return {
            'alpha': self.alpha,
            'max_iterations': self.max_iterations,
            'time_limit': self.time_limit,
            'max_no_improvement': self.max_no_improvement,
            'local_search_intensity': self.local_search_intensity,
            'seed': self.seed,
            'verbose': self.verbose
        }


class AlgorithmParams:
    """
    Classe principal para gerenciar parâmetros dos algoritmos.
    """
    
    # Parâmetros padrão para diferentes cenários
    QUICK_TEST = {
        'clisat': CliSATParams(time_limit=60.0, monitor_mode='silent'),
        'grasp': GRASPParams(max_iterations=50, time_limit=30.0, verbose=False)
    }
    
    STANDARD_BENCHMARK = {
        'clisat': CliSATParams(time_limit=1800.0, monitor_mode='log'),  # 30 min
        'grasp': GRASPParams(max_iterations=500, time_limit=300.0, verbose=False)  # 5 min
    }
    
    INTENSIVE_SEARCH = {
        'clisat': CliSATParams(time_limit=7200.0, monitor_mode='log'),  # 2 horas
        'grasp': GRASPParams(max_iterations=2000, time_limit=1800.0, verbose=False)  # 30 min
    }
    
    @classmethod
    def get_params(cls, algorithm: str, preset: str = 'standard_benchmark'):
        """
        Obter parâmetros para um algoritmo e preset específicos.
        
        Args:
            algorithm: Nome do algoritmo ('clisat' ou 'grasp')
            preset: Preset de parâmetros ('quick_test', 'standard_benchmark', 'intensive_search')
            
        Returns:
            Parâmetros do algoritmo
            
        Raises:
            ValueError: Se algoritmo ou preset não for válido
        """
        presets = {
            'quick_test': cls.QUICK_TEST,
            'standard_benchmark': cls.STANDARD_BENCHMARK,
            'intensive_search': cls.INTENSIVE_SEARCH
        }
        
        if preset not in presets:
            raise ValueError(f"Preset '{preset}' não disponível. Opções: {list(presets.keys())}")
        
        if algorithm not in presets[preset]:
            raise ValueError(f"Algoritmo '{algorithm}' não disponível. Opções: {list(presets[preset].keys())}")
        
        return presets[preset][algorithm]
    
    @classmethod
    def list_presets(cls):
        """Listar presets disponíveis."""
        return ['quick_test', 'standard_benchmark', 'intensive_search']
    
    @classmethod
    def list_algorithms(cls):
        """Listar algoritmos disponíveis."""
        return ['clisat', 'grasp']
