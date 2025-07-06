#!/usr/bin/env python3
"""
Script principal para demonstrar o algoritmo CliSAT.

Este script executa uma demonstração completa do algoritmo CliSAT,
incluindo testes, comparações e exemplos práticos.
"""

import sys
import argparse
import time
from pathlib import Path

# Adicionar o diretório atual ao path para importações
sys.path.append(str(Path(__file__).parent))

from clisat_algortithmb import solve_maximum_clique_clisat, CliSAT
from test_clisat import run_test_suite, generate_random_graph, generate_planted_clique_graph
from examples import run_social_network_example, run_protein_interaction_example
import networkx as nx


def print_header():
    """Imprimir cabeçalho do programa."""
    print("=" * 60)
    print("           IMPLEMENTAÇÃO DO ALGORITMO CLISAT")
    print("        SAT-based Algorithm for Maximum Clique")
    print("=" * 60)
    print()
    print("Baseado na pesquisa:")
    print("'CliSAT: A new exact algorithm for hard maximum clique problems'")
    print("Por P. San Segundo, F. Furini, D. Álvarez, et al.")
    print()


def demo_basic_usage():
    """Demonstração básica do uso do CliSAT."""
    print("=== Demonstração Básica ===\n")
    
    # Criar um grafo simples
    G = nx.Graph()
    
    # Adicionar um clique de tamanho 4
    clique_nodes = [1, 2, 3, 4]
    for i in clique_nodes:
        for j in clique_nodes:
            if i != j:
                G.add_edge(i, j)
    
    # Adicionar alguns nós extras conectados parcialmente
    G.add_edges_from([(5, 1), (5, 2), (6, 3), (6, 4), (7, 1), (7, 5)])
    
    print(f"Grafo criado com {len(G.nodes())} vértices e {len(G.edges())} arestas")
    print(f"Densidade: {nx.density(G):.3f}")
    print(f"Nós: {sorted(G.nodes())}")
    print(f"Arestas: {sorted(G.edges())}")
    
    print("\nExecutando CliSAT...")
    start_time = time.time()
    clique, size = solve_maximum_clique_clisat(G, time_limit=60)
    elapsed_time = time.time() - start_time
    
    print(f"\nResultado:")
    print(f"Clique máximo encontrado: {sorted(clique)}")
    print(f"Tamanho do clique: {size}")
    print(f"Tempo de execução: {elapsed_time:.3f} segundos")
    
    # Verificar se é um clique válido
    if clique:
        subgraph = G.subgraph(clique)
        expected_edges = len(clique) * (len(clique) - 1) // 2
        actual_edges = len(subgraph.edges())
        is_valid = (actual_edges == expected_edges)
        print(f"Verificação: {'✓ Clique válido' if is_valid else '✗ Clique inválido'}")
    
    return clique, size


def demo_challenging_graph():
    """Demonstração com grafo mais desafiador."""
    print("\n=== Grafo Desafiador ===\n")
    
    # Criar grafo com clique plantado
    print("Criando grafo com clique plantado...")
    G, planted_clique = generate_planted_clique_graph(20, 6, 0.4, seed=123)
    
    print(f"Grafo criado com {len(G.nodes())} vértices e {len(G.edges())} arestas")
    print(f"Densidade: {nx.density(G):.3f}")
    print(f"Clique plantado: {sorted(planted_clique)} (tamanho: {len(planted_clique)})")
    
    print("\nExecutando CliSAT...")
    start_time = time.time()
    found_clique, found_size = solve_maximum_clique_clisat(G, time_limit=300)
    elapsed_time = time.time() - start_time
    
    print(f"\nResultado:")
    print(f"Clique encontrado: {sorted(found_clique)}")
    print(f"Tamanho encontrado: {found_size}")
    print(f"Tamanho plantado: {len(planted_clique)}")
    print(f"Tempo de execução: {elapsed_time:.3f} segundos")
    
    # Verificar se encontrou o clique plantado ou um equivalente
    if found_size >= len(planted_clique):
        print("✓ CliSAT encontrou clique de tamanho igual ou maior que o plantado")
    else:
        print("⚠ CliSAT não encontrou o clique plantado completo")
        print("  (isso pode acontecer se houver múltiplos cliques máximos)")
    
    return found_clique, found_size


def demo_performance_comparison():
    """Demonstração de comparação de performance."""
    print("\n=== Comparação de Performance ===\n")
    
    print("Testando CliSAT em grafos de diferentes tamanhos...")
    
    test_cases = [
        (10, 0.6, "Pequeno Denso"),
        (15, 0.4, "Médio Moderado"),
        (20, 0.3, "Médio Esparso"),
        (25, 0.2, "Grande Esparso")
    ]
    
    results = []
    
    for n, p, description in test_cases:
        print(f"\nTeste: {description} ({n} vértices, p={p})")
        
        # Gerar grafo
        G = generate_random_graph(n, p, seed=456)
        print(f"  Grafo: {len(G.nodes())} vértices, {len(G.edges())} arestas")
        
        # Executar CliSAT
        start_time = time.time()
        clique, size = solve_maximum_clique_clisat(G, time_limit=120)
        elapsed_time = time.time() - start_time
        
        result = {
            'description': description,
            'vertices': n,
            'edges': len(G.edges()),
            'clique_size': size,
            'time': elapsed_time
        }
        results.append(result)
        
        print(f"  Resultado: clique de tamanho {size} em {elapsed_time:.3f}s")
    
    # Resumo dos resultados
    print(f"\n{'='*50}")
    print("RESUMO DA PERFORMANCE")
    print(f"{'='*50}")
    print(f"{'Teste':<15} {'Vértices':<8} {'Arestas':<8} {'Clique':<6} {'Tempo (s)':<10}")
    print("-" * 50)
    
    for result in results:
        print(f"{result['description']:<15} "
              f"{result['vertices']:<8} "
              f"{result['edges']:<8} "
              f"{result['clique_size']:<6} "
              f"{result['time']:<10.3f}")
    
    return results


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(description='Demonstração do algoritmo CliSAT')
    parser.add_argument('--mode', choices=['basic', 'full', 'test', 'examples'], 
                       default='basic',
                       help='Modo de execução (default: basic)')
    parser.add_argument('--time-limit', type=float, default=300.0,
                       help='Tempo limite em segundos (default: 300)')
    parser.add_argument('--quiet', action='store_true',
                       help='Modo silencioso')
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_header()
    
    try:
        if args.mode == 'basic':
            # Demonstração básica
            demo_basic_usage()
            
        elif args.mode == 'full':
            # Demonstração completa
            demo_basic_usage()
            demo_challenging_graph()
            demo_performance_comparison()
            
        elif args.mode == 'test':
            # Suite de testes
            print("Executando suite de testes completa...\n")
            run_test_suite()
            
        elif args.mode == 'examples':
            # Exemplos práticos
            print("Executando exemplos práticos...\n")
            run_social_network_example()
            run_protein_interaction_example()
        
        if not args.quiet:
            print(f"\n{'='*60}")
            print("DEMONSTRAÇÃO CONCLUÍDA COM SUCESSO")
            print(f"{'='*60}")
            print("\nO algoritmo CliSAT combina técnicas de SAT solving com")
            print("branch-and-bound para resolver eficientemente o problema")
            print("do clique máximo em grafos.")
            print("\nPara mais informações, consulte:")
            print("- clisat_algortithmb.py: Implementação principal")
            print("- test_clisat.py: Testes e comparações")
            print("- examples.py: Aplicações práticas")
    
    except KeyboardInterrupt:
        print("\n\nExecução interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro durante execução: {e}")
        if not args.quiet:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
