#!/usr/bin/env python3
"""
Demonstração completa dos logs periódicos do CliSAT
"""

import networkx as nx
from clisat_algortithmb import solve_maximum_clique_clisat
import time

def create_demo_graph():
    """Criar um grafo demonstrativo."""
    G = nx.Graph()
    
    # Clique principal de tamanho 6
    main_clique = list(range(1, 7))
    for i in main_clique:
        for j in main_clique:
            if i < j:
                G.add_edge(i, j)
    
    # Adicionar vértices com conexões parciais
    for i in range(7, 15):
        G.add_node(i)
        # Conectar aleatoriamente
        import random
        random.seed(42)
        for j in main_clique:
            if random.random() < 0.7:
                G.add_edge(i, j)
    
    # Adicionar algumas arestas entre os novos vértices
    for i in range(7, 15):
        for j in range(i+1, 15):
            if random.random() < 0.3:
                G.add_edge(i, j)
    
    return G

def main():
    print("🚀 DEMONSTRAÇÃO DOS LOGS PERIÓDICOS DO CliSAT")
    print("=" * 60)
    
    G = create_demo_graph()
    
    print(f"📊 Grafo de demonstração:")
    print(f"   🔢 Vértices: {G.number_of_nodes()}")
    print(f"   🔗 Arestas: {G.number_of_edges()}")
    print(f"   📏 Densidade: {nx.density(G):.3f}")
    print()
    
    print("🎯 Configuração dos logs:")
    print("   📋 Log a cada 5 nós processados")
    print("   ⏰ Log a cada 3 segundos de tempo")
    print("   ⏱️  Limite máximo: 20 segundos")
    print()
    
    # Executar com configuração de logs demonstrativa
    start = time.time()
    clique, size = solve_maximum_clique_clisat(
        G, 
        time_limit=20.0,     # 20 segundos
        log_interval=5,      # A cada 5 nós
        time_interval=3.0    # A cada 3 segundos
    )
    total_time = time.time() - start
    
    print(f"\n🏆 RESULTADO FINAL:")
    print(f"   📏 Tamanho do clique máximo: {size}")
    print(f"   📋 Vértices: {clique}")
    print(f"   ⏱️  Tempo total: {total_time:.2f}s")
    print(f"   ✅ Clique válido: {all(G.has_edge(u, v) for u in clique for v in clique if u < v)}")
    print("=" * 60)

if __name__ == "__main__":
    main()
