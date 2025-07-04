"""
Heurística Gulosa para o Problema do Clique Máximo - Atividade APA

Este módulo implementa uma heurística gulosa baseada em grau para encontrar cliques
de grande tamanho em grafos, complementando o algoritmo exato CliSAT.

FUNDAMENTAÇÃO TEÓRICA:
A heurística gulosa é um algoritmo clássico para o problema do clique máximo,
amplamente estudada na literatura (Johnson & Trick, 1996; Bomze et al., 1999).

ALGORITMO:
1. Inicializa com o vértice de maior grau
2. A cada iteração, seleciona o vértice de maior grau entre os candidatos válidos
3. Um vértice é candidato se é adjacente a todos os vértices já no clique
4. Remove vértices que não são adjacentes ao vértice selecionado
5. Repete até não haver mais candidatos válidos

COMPLEXIDADE: O(n³) no pior caso, onde n é o número de vértices.

GARANTIAS: A heurística gulosa não oferece garantia de aproximação constante
para o problema do clique máximo, mas na prática produz soluções de boa qualidade.

REFERÊNCIAS:
- Johnson, D. S., & Trick, M. A. (1996). Cliques, Coloring, and Satisfiability
- Bomze, I. M., et al. (1999). The maximum clique problem. Handbook of combinatorial optimization
"""

import networkx as nx
import numpy as np
import random
import time
from typing import List, Set, Tuple, Dict
import logging

logger = logging.getLogger(__name__)


class GreedyCliqueHeuristic:
    """
    Implementação da heurística gulosa baseada em grau para o problema do clique máximo.
    
    Esta é uma das heurísticas mais estudadas e utilizadas na literatura para o problema
    do clique máximo. A estratégia gulosa seleciona a cada iteração o vértice de maior
    grau entre os candidatos válidos (vértices adjacentes a todos no clique atual).
    
    VANTAGENS:
    - Simplicidade de implementação e compreensão
    - Tempo de execução relativamente baixo
    - Boa performance empírica em muitos tipos de grafos
    
    DESVANTAGENS:
    - Não oferece garantia de aproximação
    - Pode ficar presa em ótimos locais
    - Performance dependente da estrutura do grafo
    """
    
    def __init__(self, graph: nx.Graph, seed: int = 42):
        """
        Inicializar heurística gulosa para clique máximo.
        
        Args:
            graph: Grafo NetworkX de entrada
            seed: Semente para reprodutibilidade (para quebra de empates aleatórios)
        """
        self.graph = graph
        self.nodes = list(graph.nodes())
        self.n = len(self.nodes)
        random.seed(seed)
        np.random.seed(seed)
        
    def solve(self) -> Tuple[List, int, float]:
        """
        Executar a heurística gulosa baseada em grau.
        
        ALGORITMO DETALHADO:
        1. Calcula o grau de todos os vértices
        2. Inicializa o clique vazio e conjunto de candidatos com todos os vértices
        3. Enquanto houver candidatos válidos:
           a) Entre os candidatos, seleciona o de maior grau efetivo
           b) Adiciona o vértice selecionado ao clique
           c) Remove da lista de candidatos todos os vértices não adjacentes ao selecionado
        4. Retorna o clique encontrado
        
        CRITÉRIO DE DESEMPATE:
        Em caso de empate no grau efetivo, utiliza o grau original do vértice no grafo.
        
        Returns:
            Tuple (lista_vértices_clique, tamanho_clique, tempo_execução_segundos)
        """
        start_time = time.time()
        
        # Pré-calcular graus para critério de desempate
        original_degrees = dict(self.graph.degree())
        
        # Inicializar estruturas
        clique = []
        candidates = set(self.nodes)
        
        while candidates:
            # Calcular grau efetivo de cada candidato
            # (número de vizinhos entre os candidatos restantes)
            candidate_scores = []
            
            for v in candidates:
                # Verificar se v é adjacente a todos no clique atual
                if all(self.graph.has_edge(v, u) for u in clique):
                    # Calcular grau efetivo: vizinhos em candidates
                    effective_degree = sum(1 for u in candidates 
                                         if u != v and self.graph.has_edge(v, u))
                    
                    # Usar grau original como critério de desempate
                    candidate_scores.append((effective_degree, original_degrees[v], v))
            
            # Se não há candidatos válidos, terminar
            if not candidate_scores:
                break
            
            # Selecionar candidato com maior pontuação
            # Ordenar por: (grau_efetivo, grau_original) em ordem decrescente
            candidate_scores.sort(reverse=True)
            chosen_vertex = candidate_scores[0][2]
            
            # Adicionar vértice escolhido ao clique
            clique.append(chosen_vertex)
            candidates.remove(chosen_vertex)
            
            # Remover da lista de candidatos todos os vértices
            # que não são adjacentes ao vértice escolhido
            non_adjacent = []
            for v in candidates:
                if not self.graph.has_edge(chosen_vertex, v):
                    non_adjacent.append(v)
            
            for v in non_adjacent:
                candidates.remove(v)
        
        execution_time = time.time() - start_time
        return clique, len(clique), execution_time

def solve_maximum_clique_heuristic(graph: nx.Graph) -> Tuple[List, int, float]:
    """
    Função conveniente para resolver o problema do clique máximo usando heurística gulosa.
    
    Esta função implementa a heurística gulosa baseada em grau, que é uma das abordagens
    mais clássicas e estudadas para o problema do clique máximo.
    
    Args:
        graph: Grafo NetworkX de entrada
        
    Returns:
        Tuple (lista_vértices_clique, tamanho_clique, tempo_execução_segundos)
        
    EXEMPLO DE USO:
    >>> G = nx.Graph()
    >>> G.add_edges_from([(1,2), (1,3), (2,3), (3,4)])
    >>> clique, size, time = solve_maximum_clique_heuristic(G)
    >>> print(f"Clique encontrado: {clique}, tamanho: {size}")
    """
    heuristic = GreedyCliqueHeuristic(graph)
    return heuristic.solve()


# Exemplo de uso e validação
if __name__ == "__main__":
    # Criar um grafo de teste com clique conhecido
    print("=== TESTE DA HEURÍSTICA GULOSA ===")
    print("Referência: Johnson, D. S., & Trick, M. A. (1996)")
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
    
    # Executar heurística
    print("Executando heurística gulosa baseada em grau...")
    clique_found, size_found, time_exec = solve_maximum_clique_heuristic(G)
    
    print(f"Resultado da heurística:")
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
    print("=== ANÁLISE TEÓRICA ===")
    print("Complexidade de tempo: O(n³)")
    print("Complexidade de espaço: O(n)")
    print("Garantia de aproximação: Nenhuma (problema NP-difícil)")
    print("Vantagens: Simples, rápida, boa performance empírica")
    print("Desvantagens: Pode ficar presa em ótimos locais")
