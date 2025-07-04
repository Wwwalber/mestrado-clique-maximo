"""
CliSAT: A SAT-based exact algorithm for maximum clique problems

This implementation is based on the research paper:
"CliSAT: A new exact algorithm for hard maximum clique problems"
by P. San Segundo, F. Furini, D. Álvarez, et al.

The algorithm combines SAT solving techniques with branch-and-bound
to find maximum cliques in graphs efficiently.
"""

import networkx as nx
import numpy as np
from pysat.solvers import Glucose3
from pysat.formula import CNF
from typing import List, Set, Tuple, Optional
import time
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CliSATSolver:
    """
    CliSAT algorithm implementation for maximum clique problem.
    
    This class implements the CliSAT algorithm which uses SAT solving
    combined with preprocessing and pruning techniques to find maximum cliques.
    """
    
    def __init__(self, graph: nx.Graph, time_limit: float = 3600.0):
        """
        Initialize the CliSAT solver.
        
        Args:
            graph: NetworkX graph
            time_limit: Maximum time limit in seconds (default: 1 hour)
        """
        self.graph = graph.copy()
        self.n = len(graph.nodes())
        self.time_limit = time_limit
        self.start_time = None
        
        # Mapear nós para índices inteiros
        self.node_to_index = {node: i for i, node in enumerate(sorted(graph.nodes()))}
        self.index_to_node = {i: node for node, i in self.node_to_index.items()}
        
        # Criar matriz de adjacência
        self.adj_matrix = self._create_adjacency_matrix()
        
        # Variáveis para o melhor clique encontrado
        self.best_clique = []
        self.best_size = 0
        
        # Estatísticas
        self.stats = {
            'nodes_explored': 0,
            'sat_calls': 0,
            'pruned_by_bound': 0,
            'preprocessing_reductions': 0
        }
    
    def _create_adjacency_matrix(self) -> np.ndarray:
        """Criar matriz de adjacência do grafo."""
        adj = np.zeros((self.n, self.n), dtype=bool)
        for i in range(self.n):
            for j in range(self.n):
                if i != j:
                    node_i = self.index_to_node[i]
                    node_j = self.index_to_node[j]
                    adj[i][j] = self.graph.has_edge(node_i, node_j)
        return adj
    
    def _time_exceeded(self) -> bool:
        """Verificar se o tempo limite foi excedido."""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.time_limit
    
    def _greedy_initial_clique(self) -> List[int]:
        """
        Encontrar um clique inicial usando algoritmo guloso.
        Isso fornece um limite inferior para o tamanho do clique máximo.
        """
        vertices = list(range(self.n))
        # Ordenar por grau decrescente
        vertices.sort(key=lambda v: np.sum(self.adj_matrix[v]), reverse=True)
        
        clique = []
        for v in vertices:
            # Verificar se v é adjacente a todos os vértices no clique atual
            if all(self.adj_matrix[v][u] for u in clique):
                clique.append(v)
        
        return clique
    
    def _upper_bound_coloring(self, vertices: List[int]) -> int:
        """
        Calcular limite superior usando coloração gulosa.
        O número cromático fornece um limite superior para o clique máximo.
        """
        if not vertices:
            return 0
            
        # Criar subgrafo com os vértices dados
        subgraph_adj = self.adj_matrix[np.ix_(vertices, vertices)]
        n_sub = len(vertices)
        
        # Coloração gulosa
        colors = [-1] * n_sub
        num_colors = 0
        
        for i in range(n_sub):
            # Encontrar cores usadas pelos vizinhos
            used_colors = set()
            for j in range(i):
                if subgraph_adj[i][j] and colors[j] != -1:
                    used_colors.add(colors[j])
            
            # Atribuir a menor cor disponível
            color = 0
            while color in used_colors:
                color += 1
            colors[i] = color
            num_colors = max(num_colors, color + 1)
        
        return num_colors
    
    def _create_sat_formula(self, vertices: List[int], k: int) -> CNF:
        """
        Criar fórmula SAT para verificar se existe clique de tamanho k
        no subgrafo induzido pelos vértices dados.
        
        Args:
            vertices: Lista de índices de vértices
            k: Tamanho do clique desejado
            
        Returns:
            Fórmula CNF
        """
        self.stats['sat_calls'] += 1
        
        cnf = CNF()
        n_vertices = len(vertices)
        
        if k > n_vertices:
            # Impossível ter clique maior que o número de vértices
            cnf.append([1, -1])  # Cláusula contraditória
            return cnf
        
        # Variáveis: x_i significa que o vértice i está no clique
        # Usar índices 1-based para o SAT solver
        
        # Exatamente k vértices devem estar no clique
        # At least k vertices
        if k <= n_vertices:
            # Pelo menos k vértices devem ser selecionados
            from itertools import combinations
            
            # Para garantir exatamente k vértices, usamos cardinalidade
            # Implementação simplificada: pelo menos k vértices
            for combo in combinations(range(n_vertices), n_vertices - k + 1):
                clause = [i + 1 for i in combo]
                cnf.append(clause)
        
        # Se dois vértices não são adjacentes, não podem estar ambos no clique
        for i in range(n_vertices):
            for j in range(i + 1, n_vertices):
                vi, vj = vertices[i], vertices[j]
                if not self.adj_matrix[vi][vj]:
                    # Se vi e vj não são adjacentes: ¬x_i ∨ ¬x_j
                    cnf.append([-(i + 1), -(j + 1)])
        
        return cnf
    
    def _solve_sat(self, cnf: CNF) -> Optional[List[int]]:
        """
        Resolver fórmula SAT e retornar solução se existir.
        
        Returns:
            Lista de variáveis verdadeiras ou None se UNSAT
        """
        with Glucose3() as solver:
            for clause in cnf.clauses:
                solver.add_clause(clause)
            
            if solver.solve():
                model = solver.get_model()
                return [var for var in model if var > 0]
            else:
                return None
    
    def _branch_and_bound(self, vertices: List[int], current_clique: List[int]):
        """
        Algoritmo principal de branch-and-bound com SAT.
        
        Args:
            vertices: Vértices candidatos
            current_clique: Clique atual sendo construído
        """
        self.stats['nodes_explored'] += 1
        
        if self._time_exceeded():
            return
        
        # Atualizar melhor clique se necessário
        if len(current_clique) > self.best_size:
            self.best_size = len(current_clique)
            self.best_clique = current_clique.copy()
            logger.info(f"Novo melhor clique encontrado: tamanho {self.best_size}")
        
        # Poda por limite superior
        upper_bound = len(current_clique) + self._upper_bound_coloring(vertices)
        if upper_bound <= self.best_size:
            self.stats['pruned_by_bound'] += 1
            return
        
        if not vertices:
            return
        
        # Tentar expandir o clique usando SAT
        target_size = len(current_clique) + len(vertices)
        
        # Busca binária para encontrar o maior clique possível
        left, right = self.best_size + 1, target_size
        
        while left <= right and not self._time_exceeded():
            mid = (left + right) // 2
            
            # Criar fórmula SAT para clique de tamanho mid
            all_candidates = current_clique + vertices
            cnf = self._create_sat_formula(all_candidates, mid)
            
            solution = self._solve_sat(cnf)
            
            if solution is not None:
                # SAT: existe clique de tamanho mid
                # Extrair o clique da solução
                clique_indices = [i - 1 for i in solution if i > 0 and i - 1 < len(all_candidates)]
                clique = [all_candidates[i] for i in clique_indices]
                
                if len(clique) > self.best_size:
                    self.best_size = len(clique)
                    self.best_clique = clique.copy()
                    logger.info(f"SAT encontrou clique de tamanho {len(clique)}")
                
                left = mid + 1
            else:
                # UNSAT: não existe clique de tamanho mid
                right = mid - 1
        
        # Branching: tentar adicionar cada vértice candidato
        for i, v in enumerate(vertices):
            if self._time_exceeded():
                break
                
            # Verificar se v é adjacente a todos no clique atual
            if all(self.adj_matrix[v][u] for u in current_clique):
                # Novos candidatos: vértices adjacentes a v
                new_vertices = [u for u in vertices[i+1:] 
                              if self.adj_matrix[v][u]]
                
                self._branch_and_bound(new_vertices, current_clique + [v])
    
    def _preprocess_graph(self):
        """
        Pré-processamento para reduzir o grafo.
        Remove vértices que certamente não podem estar no clique máximo.
        """
        logger.info("Iniciando pré-processamento...")
        original_size = self.n
        
        # Remover vértices isolados
        degrees = [np.sum(self.adj_matrix[i]) for i in range(self.n)]
        
        # Remoção iterativa de vértices com grau baixo
        removed = True
        while removed and not self._time_exceeded():
            removed = False
            current_best = max(self.best_size, len(self._greedy_initial_clique()))
            
            for i in range(self.n):
                if degrees[i] < current_best - 1:
                    # Vértice não pode estar em clique maior que current_best
                    self._remove_vertex(i)
                    removed = True
                    break
        
        reduction = original_size - self.n
        self.stats['preprocessing_reductions'] = reduction
        logger.info(f"Pré-processamento removeu {reduction} vértices")
    
    def _remove_vertex(self, vertex: int):
        """Remover vértice do grafo (implementação simplificada)."""
        # Em uma implementação completa, isso atualizaria as estruturas de dados
        pass
    
    def solve(self) -> Tuple[List, int]:
        """
        Resolver o problema do clique máximo.
        
        Returns:
            Tuple contendo (lista_de_nós_do_clique, tamanho_do_clique)
        """
        self.start_time = time.time()
        logger.info(f"Iniciando CliSAT para grafo com {self.n} vértices")
        
        # Pré-processamento
        self._preprocess_graph()
        
        # Clique inicial guloso para limite inferior
        initial_clique = self._greedy_initial_clique()
        self.best_clique = initial_clique
        self.best_size = len(initial_clique)
        logger.info(f"Clique inicial (guloso): tamanho {self.best_size}")
        
        if self._time_exceeded():
            logger.warning("Tempo limite excedido durante inicialização")
            return self._convert_result()
        
        # Algoritmo principal
        vertices = list(range(self.n))
        # Ordenar por grau decrescente para melhor performance
        vertices.sort(key=lambda v: np.sum(self.adj_matrix[v]), reverse=True)
        
        self._branch_and_bound(vertices, [])
        
        total_time = time.time() - self.start_time
        logger.info(f"CliSAT finalizado em {total_time:.2f}s")
        logger.info(f"Melhor clique encontrado: tamanho {self.best_size}")
        logger.info(f"Estatísticas: {self.stats}")
        
        return self._convert_result()
    
    def _convert_result(self) -> Tuple[List, int]:
        """Converter resultado de índices para nós originais."""
        if not self.best_clique:
            return [], 0
        
        original_nodes = [self.index_to_node[i] for i in self.best_clique]
        return original_nodes, self.best_size


def solve_maximum_clique_clisat(graph: nx.Graph, time_limit: float = 3600.0) -> Tuple[List, int]:
    """
    Função conveniente para resolver o problema do clique máximo usando CliSAT.
    
    Args:
        graph: Grafo NetworkX
        time_limit: Tempo limite em segundos
        
    Returns:
        Tuple contendo (lista_de_nós_do_clique, tamanho_do_clique)
    """
    solver = CliSATSolver(graph, time_limit)
    return solver.solve()


# Exemplo de uso
if __name__ == "__main__":
    # Criar um grafo de exemplo
    G = nx.Graph()
    
    # Adicionar um clique de tamanho 4
    clique_nodes = [1, 2, 3, 4]
    for i in clique_nodes:
        for j in clique_nodes:
            if i != j:
                G.add_edge(i, j)
    
    # Adicionar alguns nós extras
    G.add_edges_from([(5, 1), (5, 2), (6, 3), (6, 4), (7, 1)])
    
    print("Grafo de exemplo:")
    print(f"Nós: {list(G.nodes())}")
    print(f"Arestas: {list(G.edges())}")
    
    # Resolver usando CliSAT
    clique, size = solve_maximum_clique_clisat(G, time_limit=60.0)
    
    print(f"\nResultado CliSAT:")
    print(f"Clique máximo: {clique}")
    print(f"Tamanho: {size}")
    
    # Verificar se o resultado é válido
    if clique:
        subgraph = G.subgraph(clique)
        is_clique = len(subgraph.edges()) == len(clique) * (len(clique) - 1) // 2
        print(f"Verificação: {'Válido' if is_clique else 'Inválido'}")
