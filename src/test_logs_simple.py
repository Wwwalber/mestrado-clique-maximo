#!/usr/bin/env python3
"""
Teste rápido dos logs do CliSAT
"""

import networkx as nx
from clisat_algortithmb import CliSAT
import random

def main():
    # Criar grafo de teste
    random.seed(42)
    G = nx.Graph()
    
    # Criar grafo com clique conhecido e estrutura complexa
    # Clique de tamanho 4
    clique = [1, 2, 3, 4]
    for i in clique:
        for j in clique:
            if i < j:
                G.add_edge(i, j)
    
    # Adicionar mais vértices com conexões parciais
    for i in range(5, 13):
        G.add_node(i)
        # Conectar cada novo vértice a alguns do clique
        for j in clique:
            if random.random() < 0.6:
                G.add_edge(i, j)
    
    # Adicionar algumas arestas entre os novos vértices
    for i in range(5, 13):
        for j in range(i+1, 13):
            if random.random() < 0.4:
                G.add_edge(i, j)
    
    print(f"Grafo criado: {len(G.nodes())} vértices, {len(G.edges())} arestas")
    print(f"Densidade: {nx.density(G):.3f}")
    print()
    
    # Executar CliSAT com intervalo de log pequeno
    solver = CliSAT(G, time_limit=15.0, log_interval=2)
    clique, size = solver.solve()
    
    print(f"\nResultado: clique de tamanho {size}")
    print(f"Vértices: {clique}")

if __name__ == "__main__":
    main()
