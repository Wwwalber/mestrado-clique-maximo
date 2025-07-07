"""
Interface comum para algoritmos de clique máximo

Este módulo define interfaces e estruturas comuns para padronizar
a comunicação entre diferentes algoritmos de clique máximo.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Tuple, Optional, Dict, Any
import networkx as nx
import time
import logging

logger = logging.getLogger(__name__)


@dataclass
class AlgorithmResult:
    """
    Resultado padrão de um algoritmo de clique máximo.
    """
    clique: List[int]                    # Vértices do clique encontrado
    clique_size: int                     # Tamanho do clique
    execution_time: float                # Tempo de execução em segundos
    algorithm_name: str                  # Nome do algoritmo utilizado
    is_optimal: bool = False             # Se é garantidamente ótimo
    iterations: Optional[int] = None     # Número de iterações (se aplicável)
    additional_info: Dict[str, Any] = None  # Informações adicionais
    
    def __post_init__(self):
        if self.additional_info is None:
            self.additional_info = {}
        
        # Validar consistência
        if len(self.clique) != self.clique_size:
            self.clique_size = len(self.clique)


class AlgorithmInterface(ABC):
    """
    Interface abstrata para algoritmos de clique máximo.
    
    Define o padrão comum que todos os algoritmos devem seguir.
    """
    
    def __init__(self, graph: nx.Graph, **kwargs):
        """
        Inicializar algoritmo.
        
        Args:
            graph: Grafo NetworkX
            **kwargs: Parâmetros específicos do algoritmo
        """
        self.graph = graph
        self.n_nodes = len(graph.nodes())
        self.n_edges = len(graph.edges())
        
    @abstractmethod
    def solve(self) -> AlgorithmResult:
        """
        Executar o algoritmo para encontrar o clique máximo.
        
        Returns:
            AlgorithmResult com os resultados
        """
        pass
    
    @property
    @abstractmethod
    def algorithm_name(self) -> str:
        """Nome do algoritmo."""
        pass
    
    @property
    @abstractmethod
    def is_exact(self) -> bool:
        """Se o algoritmo é exato (garante ótimo) ou heurístico."""
        pass
    
    def validate_clique(self, clique: List[int]) -> bool:
        """
        Validar se um conjunto de vértices forma um clique válido.
        
        Args:
            clique: Lista de vértices
            
        Returns:
            True se é um clique válido, False caso contrário
        """
        if len(clique) <= 1:
            return True
        
        # Verificar se todos os vértices existem no grafo
        for vertex in clique:
            if vertex not in self.graph:
                return False
        
        # Verificar se todos os pares são adjacentes
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                if not self.graph.has_edge(clique[i], clique[j]):
                    return False
        
        return True
    
    def get_graph_info(self) -> Dict[str, Any]:
        """
        Obter informações básicas do grafo.
        
        Returns:
            Dicionário com informações do grafo
        """
        return {
            'nodes': self.n_nodes,
            'edges': self.n_edges,
            'density': nx.density(self.graph),
            'is_connected': nx.is_connected(self.graph),
            'diameter': nx.diameter(self.graph) if nx.is_connected(self.graph) else None,
            'average_clustering': nx.average_clustering(self.graph)
        }


# Funções de conveniência para compatibilidade
def solve_maximum_clique_clisat(graph: nx.Graph, 
                               time_limit: float = 3600.0,
                               **kwargs) -> Tuple[List[int], int, float]:
    """
    Interface de compatibilidade para CliSAT.
    
    Args:
        graph: Grafo NetworkX
        time_limit: Limite de tempo em segundos
        **kwargs: Parâmetros adicionais
        
    Returns:
        Tupla (clique, tamanho, tempo)
    """
    from .clisat_exact import CliSAT
    
    solver = CliSAT(graph, time_limit=time_limit, **kwargs)
    result = solver.solve()
    
    return result


def solve_maximum_clique_heuristic(graph: nx.Graph,
                                  alpha: float = 0.3,
                                  max_iterations: int = 100,
                                  time_limit: float = 60.0,
                                  seed: int = 42,
                                  **kwargs) -> Tuple[List[int], int, float]:
    """
    Interface de compatibilidade para GRASP.
    
    Args:
        graph: Grafo NetworkX
        alpha: Parâmetro de aleatoriedade GRASP
        max_iterations: Número máximo de iterações
        time_limit: Limite de tempo em segundos
        seed: Semente aleatória
        **kwargs: Parâmetros adicionais
        
    Returns:
        Tupla (clique, tamanho, tempo)
    """
    from .grasp_heuristic import solve_maximum_clique_grasp
    
    return solve_maximum_clique_grasp(
        graph=graph,
        alpha=alpha,
        max_iterations=max_iterations,
        time_limit=time_limit,
        seed=seed,
        verbose=kwargs.get('verbose', False)
    )


# Função factory para criar algoritmos
def create_algorithm(algorithm_type: str, graph: nx.Graph, **params) -> AlgorithmInterface:
    """
    Factory para criar instâncias de algoritmos.
    
    Args:
        algorithm_type: Tipo do algoritmo ('clisat', 'grasp')
        graph: Grafo NetworkX
        **params: Parâmetros específicos do algoritmo
        
    Returns:
        Instância do algoritmo
        
    Raises:
        ValueError: Se o tipo de algoritmo não é suportado
    """
    if algorithm_type.lower() == 'clisat':
        from .clisat_exact import CliSAT
        return CliSAT(graph, **params)
    elif algorithm_type.lower() == 'grasp':
        from .grasp_heuristic import GRASPMaximumClique
        return GRASPMaximumClique(graph, **params)
    else:
        raise ValueError(f"Tipo de algoritmo não suportado: {algorithm_type}")
