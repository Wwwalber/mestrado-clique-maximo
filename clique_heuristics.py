"""
Heurística GRASP para o Problema do Clique Máximo - Atividade APA

Este módulo implementa o algoritmo GRASP (Greedy Randomized Adaptive Search Procedure)
para encontrar cliques de grande tamanho em grafos, complementando o algoritmo exato CliSAT.

FUNDAMENTAÇÃO TEÓRICA:
O GRASP é uma metaheurística amplamente estudada na literatura para problemas de
otimização combinatória, incluindo o clique máximo (Feo & Resende, 1995).

ALGORITMO:
1. Fase de Construção: Constrói solução usando critério guloso randomizado
2. Fase de Busca Local: Melhora solução através de operadores de vizinhança
3. Reinicialização: Repete o processo até critério de parada

COMPLEXIDADE: O(k × n³) onde k é o número de iterações e n é o número de vértices.

GARANTIAS: Heurística de alta qualidade com boa capacidade de escape de ótimos locais.

REFERÊNCIAS:
- Feo, T.A., Resende, M.G.C. (1995). Greedy Randomized Adaptive Search Procedures
- Pardalos, P.M., Xue, J. (1994). The maximum clique problem
"""

import networkx as nx
import time
from typing import List, Tuple
import logging
from grasp_maximum_clique import solve_maximum_clique_grasp, GRASPParameters

logger = logging.getLogger(__name__)


class GRASPCliqueHeuristic:
    """
    Implementação da heurística GRASP para o problema do clique máximo.
    
    O GRASP (Greedy Randomized Adaptive Search Procedure) é uma metaheurística
    que combina construção gulosa randomizada com busca local, sendo uma das
    abordagens mais eficazes para o problema do clique máximo.
    
    VANTAGENS:
    - Boa capacidade de escape de ótimos locais
    - Balanceamento entre exploração e explotação
    - Performance superior à heurística gulosa simples
    - Flexibilidade através de parâmetros configuráveis
    
    REFERÊNCIAS:
    - Feo, T.A., Resende, M.G.C. (1995). Greedy Randomized Adaptive Search Procedures
    - Pardalos, P.M., Xue, J. (1994). The maximum clique problem
    """
    
    def __init__(self, graph: nx.Graph, 
                 alpha: float = 0.3, 
                 max_iterations: int = 100,
                 time_limit: float = 60.0,
                 seed: int = 42):
        """
        Inicializar heurística GRASP para clique máximo.
        
        Args:
            graph: Grafo NetworkX de entrada
            alpha: Parâmetro de aleatoriedade (0=guloso, 1=aleatório)
            max_iterations: Número máximo de iterações
            time_limit: Limite de tempo em segundos
            seed: Semente para reprodutibilidade
        """
        self.graph = graph
        self.parameters = GRASPParameters(
            alpha=alpha,
            max_iterations=max_iterations,
            time_limit=time_limit,
            seed=seed,
            verbose=False  # Silencioso para não interferir no benchmark
        )
        
    def solve(self) -> Tuple[List, int, float]:
        """
        Executar o algoritmo GRASP para encontrar um clique máximo.
        
        Returns:
            Tuple (lista_vértices_clique, tamanho_clique, tempo_execução_segundos)
        """
        start_time = time.time()
        
        try:
            # Chamar a função GRASP com os parâmetros individuais
            clique, size, exec_time = solve_maximum_clique_grasp(
                graph=self.graph,
                alpha=self.parameters.alpha,
                max_iterations=self.parameters.max_iterations,
                time_limit=self.parameters.time_limit,
                seed=self.parameters.seed,
                verbose=self.parameters.verbose
            )
            
            # Converter conjunto para lista se necessário
            if isinstance(clique, set):
                clique = list(clique)
            
            return clique, size, exec_time
            
        except Exception as e:
            logger.error(f"Erro na execução do GRASP: {e}")
            # Retornar solução trivial em caso de erro
            execution_time = time.time() - start_time
            return [], 0, execution_time

def solve_maximum_clique_heuristic(graph: nx.Graph, 
                                   alpha: float = 0.3,
                                   max_iterations: int = 100,
                                   time_limit: float = 60.0) -> Tuple[List, int, float]:
    """
    Função conveniente para resolver o problema do clique máximo usando GRASP.
    
    Esta função implementa a metaheurística GRASP, que é uma abordagem de alta
    qualidade para o problema do clique máximo, combinando construção gulosa
    randomizada com busca local.
    
    Args:
        graph: Grafo NetworkX de entrada
        alpha: Parâmetro de aleatoriedade (0=guloso, 1=aleatório)
        max_iterations: Número máximo de iterações GRASP
        time_limit: Limite de tempo em segundos
        
    Returns:
        Tuple (lista_vértices_clique, tamanho_clique, tempo_execução_segundos)
        
    EXEMPLO DE USO:
    >>> G = nx.Graph()
    >>> G.add_edges_from([(1,2), (1,3), (2,3), (3,4)])
    >>> clique, size, time = solve_maximum_clique_heuristic(G)
    >>> print(f"Clique encontrado: {clique}, tamanho: {size}")
    """
    heuristic = GRASPCliqueHeuristic(graph, alpha, max_iterations, time_limit)
    return heuristic.solve()


# Exemplo de uso e validação
if __name__ == "__main__":
    # Criar um grafo de teste com clique conhecido
    print("=== TESTE DA HEURÍSTICA GRASP ===")
    print("Referência: Feo, T.A., Resende, M.G.C. (1995)")
    print()
    
    G = nx.Graph()
    
    # Adicionar um clique de tamanho 5 (solução ótima conhecida)
    clique_nodes = [1, 2, 3, 4, 5]
    for i in clique_nodes:
        for j in clique_nodes:
            if i != j:
                G.add_edge(i, j)
    
    # Adicionar alguns nós extras conectados parcialmente
    G.add_edges_from([(6, 1), (6, 2), (7, 3), (7, 4), (8, 1), (8, 5)])
    
    print(f"Grafo de teste:")
    print(f"- Vértices: {len(G.nodes())}")
    print(f"- Arestas: {len(G.edges())}")
    print(f"- Densidade: {nx.density(G):.3f}")
    print(f"- Clique ótimo conhecido: {sorted(clique_nodes)} (tamanho: {len(clique_nodes)})")
    print()
    
    # Executar heurística GRASP
    print("Executando heurística GRASP...")
    clique_found, size_found, time_exec = solve_maximum_clique_heuristic(
        G, alpha=0.3, max_iterations=50, time_limit=30.0
    )
    
    print(f"Resultado do GRASP:")
    print(f"- Clique encontrado: {sorted(clique_found)}")
    print(f"- Tamanho: {size_found}")
    print(f"- Tempo de execução: {time_exec:.6f} segundos")
    print(f"- Qualidade: {size_found}/{len(clique_nodes)} = {size_found/len(clique_nodes)*100:.1f}% do ótimo")
    
    # Verificar se é um clique válido
    if clique_found:
        subgraph = G.subgraph(clique_found)
        expected_edges = len(clique_found) * (len(clique_found) - 1) // 2
        actual_edges = len(subgraph.edges())
        is_valid = (actual_edges == expected_edges)
        print(f"- Verificação: {'✓ Clique válido' if is_valid else '✗ Clique inválido'}")
    
    print()
    print("=== ANÁLISE TEÓRICA DO GRASP ===")
    print("Complexidade de tempo: O(k × n³) onde k é o número de iterações")
    print("Complexidade de espaço: O(n)")
    print("Garantia de aproximação: Heurística de alta qualidade")
    print("Vantagens: Escape de ótimos locais, configurável, boa performance")
    print("Desvantagens: Mais complexo que heurística gulosa simples")
    print()
    
    # Testar diferentes valores de alpha
    print("=== TESTE DE DIFERENTES PARÂMETROS ===")
    alphas = [0.0, 0.3, 0.7, 1.0]
    for alpha in alphas:
        clique, size, time_taken = solve_maximum_clique_heuristic(
            G, alpha=alpha, max_iterations=20, time_limit=10.0
        )
        print(f"Alpha={alpha:.1f}: tamanho={size}, tempo={time_taken:.4f}s")
