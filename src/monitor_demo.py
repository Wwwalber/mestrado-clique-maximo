#!/usr/bin/env python3
"""
Demonstração dos diferentes modos de monitoramento do CliSAT
"""

import networkx as nx
from clisat_algortithmb import CliSAT, solve_maximum_clique_clisat
import time
import argparse

def create_test_graph(size='medium'):
    """Criar grafo de teste de tamanho variável."""
    if size == 'small':
        # Grafo pequeno para teste rápido
        G = nx.Graph()
        clique = list(range(1, 6))  # Clique de 5
        for i in clique:
            for j in clique:
                if i < j:
                    G.add_edge(i, j)
        
        # Adicionar alguns vértices extras
        for i in range(6, 10):
            G.add_node(i)
            for j in clique[:3]:  # Conectar aos primeiros 3 do clique
                G.add_edge(i, j)
        
        return G
    
    elif size == 'medium':
        # Grafo médio para demonstração
        import random
        random.seed(42)
        G = nx.Graph()
        
        # Clique principal
        main_clique = list(range(1, 8))  # Clique de 7
        for i in main_clique:
            for j in main_clique:
                if i < j:
                    G.add_edge(i, j)
        
        # Adicionar vértices com conexões parciais
        for i in range(8, 20):
            G.add_node(i)
            for j in main_clique:
                if random.random() < 0.6:
                    G.add_edge(i, j)
        
        # Conectar alguns dos novos vértices entre si
        for i in range(8, 20):
            for j in range(i+1, 20):
                if random.random() < 0.3:
                    G.add_edge(i, j)
        
        return G
    
    elif size == 'large':
        # Grafo maior para teste de performance
        import random
        random.seed(123)
        G = nx.Graph()
        
        # Clique principal maior
        main_clique = list(range(1, 12))  # Clique de 11
        for i in main_clique:
            for j in main_clique:
                if i < j:
                    G.add_edge(i, j)
        
        # Muitos vértices extras
        for i in range(12, 50):
            G.add_node(i)
            for j in main_clique:
                if random.random() < 0.4:
                    G.add_edge(i, j)
        
        # Conectar vértices extras
        for i in range(12, 50):
            for j in range(i+1, 50):
                if random.random() < 0.2:
                    G.add_edge(i, j)
        
        return G

def demo_log_mode():
    """Demonstrar modo de log tradicional."""
    print("🔍 DEMONSTRAÇÃO: MODO LOG TRADICIONAL")
    print("=" * 60)
    
    G = create_test_graph('medium')
    print(f"Grafo: {G.number_of_nodes()} vértices, {G.number_of_edges()} arestas")
    print("Características: Log sequencial com histórico preservado\n")
    
    solver = CliSAT(G, time_limit=10.0, log_interval=3, time_interval=2.0, monitor_mode='log')
    clique, size = solver.solve()
    
    print(f"\nResultado: Clique máximo de tamanho {size}")
    return clique, size

def demo_realtime_mode():
    """Demonstrar modo de monitoramento em tempo real."""
    print("📊 DEMONSTRAÇÃO: MODO TEMPO REAL")
    print("=" * 60)
    
    G = create_test_graph('medium')
    print(f"Grafo: {G.number_of_nodes()} vértices, {G.number_of_edges()} arestas")
    print("Características: Dashboard atualizado na mesma posição")
    print("Pressione Ctrl+C para interromper se necessário\n")
    
    time.sleep(2)  # Pausa para ler
    
    solver = CliSAT(G, time_limit=15.0, log_interval=2, time_interval=1.0, monitor_mode='realtime')
    clique, size = solver.solve()
    
    print(f"\nResultado: Clique máximo de tamanho {size}")
    return clique, size

def demo_both_mode():
    """Demonstrar modo híbrido."""
    print("🔄 DEMONSTRAÇÃO: MODO HÍBRIDO (LOG + TEMPO REAL)")
    print("=" * 60)
    
    G = create_test_graph('medium')
    print(f"Grafo: {G.number_of_nodes()} vértices, {G.number_of_edges()} arestas")
    print("Características: Dashboard em tempo real + logs para eventos especiais\n")
    
    time.sleep(2)
    
    solver = CliSAT(G, time_limit=12.0, log_interval=4, time_interval=2.0, monitor_mode='both')
    clique, size = solver.solve()
    
    print(f"\nResultado: Clique máximo de tamanho {size}")
    return clique, size

def demo_silent_mode():
    """Demonstrar modo silencioso."""
    print("🤫 DEMONSTRAÇÃO: MODO SILENCIOSO")
    print("=" * 60)
    
    G = create_test_graph('small')
    print(f"Grafo: {G.number_of_nodes()} vértices, {G.number_of_edges()} arestas")
    print("Características: Sem monitoramento, apenas resultado final\n")
    
    start = time.time()
    solver = CliSAT(G, time_limit=5.0, monitor_mode='silent')
    clique, size = solver.solve()
    end = time.time()
    
    print(f"Executado em {end-start:.2f}s - Resultado: Clique máximo de tamanho {size}")
    return clique, size

def compare_modes():
    """Comparar diferentes modos lado a lado."""
    print("⚡ COMPARAÇÃO DOS MODOS DE MONITORAMENTO")
    print("=" * 60)
    
    G = create_test_graph('small')
    modes = ['silent', 'log', 'realtime']
    
    for mode in modes:
        print(f"\n🔹 Testando modo: {mode.upper()}")
        print("-" * 30)
        
        start = time.time()
        clique, size = solve_maximum_clique_clisat(
            G, time_limit=3.0, log_interval=2, time_interval=1.0, monitor_mode=mode
        )
        end = time.time()
        
        print(f"Tempo: {end-start:.2f}s | Clique: {size} vértices")
        time.sleep(1)

def main():
    parser = argparse.ArgumentParser(description='Demo dos modos de monitoramento CliSAT')
    parser.add_argument('--mode', choices=['log', 'realtime', 'both', 'silent', 'compare'], 
                        default='compare', help='Modo de demonstração')
    parser.add_argument('--size', choices=['small', 'medium', 'large'], 
                        default='medium', help='Tamanho do grafo')
    
    args = parser.parse_args()
    
    print("🚀 DEMONSTRAÇÃO DOS MODOS DE MONITORAMENTO CliSAT")
    print("=" * 60)
    print("Modos disponíveis:")
    print("  📝 log      - Logs sequenciais tradicionais")
    print("  📊 realtime - Dashboard em tempo real")
    print("  🔄 both     - Híbrido (dashboard + logs de eventos)")
    print("  🤫 silent   - Silencioso (só resultado final)")
    print("=" * 60)
    
    if args.mode == 'log':
        demo_log_mode()
    elif args.mode == 'realtime':
        demo_realtime_mode()
    elif args.mode == 'both':
        demo_both_mode()
    elif args.mode == 'silent':
        demo_silent_mode()
    elif args.mode == 'compare':
        compare_modes()

if __name__ == "__main__":
    main()
