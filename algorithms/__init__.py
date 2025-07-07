"""
Algorithms package for Maximum Clique Problem

Este pacote contém as implementações dos algoritmos para o problema do clique máximo:
- CliSAT: Algoritmo exato baseado em SAT
- GRASP: Metaheurística de alta qualidade

Uso:
    from algorithms.clisat_exact import solve_maximum_clique_clisat
    from algorithms.grasp_heuristic import solve_maximum_clique_grasp
"""

__version__ = "1.0.0"
__author__ = "Walber"

# Importações principais para facilitar o uso
try:
    from .clisat_exact import solve_maximum_clique_clisat, CliSAT
    from .grasp_heuristic import solve_maximum_clique_grasp, GRASPMaximumClique
    from .algorithm_interface import AlgorithmInterface, AlgorithmResult
    
    __all__ = [
        'solve_maximum_clique_clisat',
        'solve_maximum_clique_grasp', 
        'CliSAT',
        'GRASPMaximumClique',
        'AlgorithmInterface',
        'AlgorithmResult'
    ]
except ImportError:
    # Módulos ainda não movidos
    __all__ = []
