#!/usr/bin/env python3
"""
Teste dos logs periódicos do CliSAT com um grafo maior.
"""

import networkx as nx
import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from clisat_algortithmb import CliSAT

def create_larger_test_graph():
    """Criar um grafo maior para testar os logs periódicos."""
    # Criar um grafo aleatório com densidade controlada
    n = 20  # 20 vértices
    G = nx.Graph()
    G.add_nodes_from(range(1, n+1))
    
    # Adicionar um clique inicial de tamanho 5
    clique_vertices = [1, 2, 3, 4, 5]
    for i in clique_vertices:
        for j in clique_vertices:
            if i < j:
                G.add_edge(i, j)
    
    # Adicionar algumas arestas aleatórias para tornar mais interessante
    import random
    random.seed(42)  # Para resultados reproduzíveis
    
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            if not G.has_edge(i, j) and random.random() < 0.3:
                G.add_edge(i, j)
    
    return G

def main():
    print("=== Teste de Logs Periódicos do CliSAT ===")
    
    # Criar grafo de teste
    G = create_larger_test_graph()
    
    print(f"Grafo de teste:")
    print(f"Vértices: {list(G.nodes())}")
    print(f"Arestas: {G.number_of_edges()}")
    print(f"Densidade: {nx.density(G):.3f}")
    print()
    
    # Executar CliSAT com intervalo de log menor para ver mais logs
    print("Executando CliSAT com logs periódicos...")
    solver = CliSAT(G, time_limit=30.0, log_interval=10)  # Log a cada 10 nós
    clique, size = solver.solve()
    
    print(f"\nResultado final:")
    print(f"Clique máximo: {clique}")
    print(f"Tamanho: {size}")
    
    # Verificar se é um clique válido
    subgraph = G.subgraph(clique)
    is_clique = nx.is_clique(G, clique)
    print(f"É um clique válido: {is_clique}")

if __name__ == "__main__":
    main()
