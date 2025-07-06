#!/usr/bin/env python3
"""
Teste específico para ver logs de novos cliques descobertos
"""

import networkx as nx
from clisat_algortithmb import CliSAT

def create_challenging_graph():
    """Criar grafo que força descoberta gradual de cliques maiores."""
    G = nx.Graph()
    
    # Começar com um clique pequeno
    small_clique = [1, 2, 3]
    for i in small_clique:
        for j in small_clique:
            if i < j:
                G.add_edge(i, j)
    
    # Adicionar vértices que podem formar cliques maiores
    # mas só são descobertos durante a busca
    G.add_node(4)
    G.add_edges_from([(4, 1), (4, 2), (4, 3)])  # Agora temos clique de 4
    
    G.add_node(5)
    G.add_edges_from([(5, 1), (5, 2)])  # Conectado parcialmente
    
    G.add_node(6)
    G.add_edges_from([(6, 1), (6, 2), (6, 3), (6, 4)])  # Completa clique de 5
    
    # Adicionar vértices extras para criar complexidade na busca
    for i in range(7, 11):
        G.add_node(i)
        # Conectar aleatoriamente para criar caminhos que precisam ser explorados
        if i == 7:
            G.add_edges_from([(7, 1), (7, 5)])
        elif i == 8:
            G.add_edges_from([(8, 2), (8, 5)])
        elif i == 9:
            G.add_edges_from([(9, 3)])
        elif i == 10:
            G.add_edges_from([(10, 4)])
    
    return G

def main():
    print("=== Teste de Logs de Descoberta de Cliques ===")
    
    G = create_challenging_graph()
    
    print(f"Grafo criado: {len(G.nodes())} vértices, {len(G.edges())} arestas")
    print(f"Densidade: {nx.density(G):.3f}")
    print(f"Arestas: {list(G.edges())}")
    print()
    
    # Usar heurística inicial pior para forçar descoberta gradual
    # Modificar temporariamente a heurística
    solver = CliSAT(G, time_limit=10.0, log_interval=1)
    
    # Forçar clique inicial menor modificando o algoritmo guloso
    solver.max_clique = [1, 2, 3]  # Clique de tamanho 3
    solver.lb = 3
    
    print("🎯 Clique inicial forçado:")
    print(f"   📏 Tamanho: {solver.lb}")
    print(f"   📋 Vértices: {solver.max_clique}")
    print()
    
    # Agora executar o solve para ver descoberta gradual
    clique, size = solver.solve()
    
    print(f"\nResultado final: clique de tamanho {size}")
    print(f"Vértices: {clique}")

if __name__ == "__main__":
    main()
