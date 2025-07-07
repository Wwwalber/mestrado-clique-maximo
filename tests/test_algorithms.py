"""
Teste simples dos algoritmos implementados para a atividade APA.

Este script testa os dois algoritmos (exato e heurística) em grafos simples
para validar a implementação antes de executar nos dados DIMACS.
"""

import networkx as nx
import time
from clisat_algortithmb import solve_maximum_clique_clisat
from clique_heuristics import solve_maximum_clique_heuristic


def create_test_graphs():
    """Criar grafos de teste com cliques conhecidos."""
    graphs = {}
    
    # Grafo 1: Clique pequeno (K4) + nós extras
    G1 = nx.Graph()
    # Clique de tamanho 4
    for i in range(1, 5):
        for j in range(i+1, 5):
            G1.add_edge(i, j)
    # Adicionar nós extras
    G1.add_edges_from([(5, 1), (5, 2), (6, 3), (6, 4)])
    graphs['small_clique'] = (G1, 4)  # (grafo, tamanho_clique_ótimo)
    
    # Grafo 2: Dois cliques separados
    G2 = nx.Graph()
    # Primeiro clique (1,2,3)
    G2.add_edges_from([(1, 2), (1, 3), (2, 3)])
    # Segundo clique (4,5,6,7)
    for i in range(4, 8):
        for j in range(i+1, 8):
            G2.add_edge(i, j)
    # Conectar os cliques com uma aresta
    G2.add_edge(3, 4)
    graphs['two_cliques'] = (G2, 4)
    
    # Grafo 3: Ciclo (clique máximo = 2)
    G3 = nx.cycle_graph(6)
    # Renomear nós para começar em 1
    G3 = nx.relabel_nodes(G3, {i: i+1 for i in range(6)})
    graphs['cycle'] = (G3, 2)
    
    # Grafo 4: Completo K5
    G4 = nx.complete_graph(5)
    # Renomear nós para começar em 1
    G4 = nx.relabel_nodes(G4, {i: i+1 for i in range(5)})
    graphs['complete'] = (G4, 5)
    
    return graphs


def test_algorithms():
    """Testar ambos algoritmos nos grafos de teste."""
    
    print("=" * 60)
    print("           TESTE DOS ALGORITMOS DA ATIVIDADE APA")
    print("=" * 60)
    print()
    print("Algoritmo Exato: CliSAT (SAT-based)")
    print("Heurística: Gulosa baseada em grau")
    print()
    
    graphs = create_test_graphs()
    
    results = []
    
    for graph_name, (graph, optimal_size) in graphs.items():
        print(f"Testando grafo: {graph_name}")
        print(f"  Vértices: {len(graph.nodes())}")
        print(f"  Arestas: {len(graph.edges())}")
        print(f"  Clique ótimo conhecido: {optimal_size}")
        
        # Testar algoritmo exato
        print("  Executando CliSAT (exato)...")
        try:
            start_time = time.time()
            exact_clique, exact_size = solve_maximum_clique_clisat(graph, time_limit=30)
            exact_time = time.time() - start_time
            
            exact_correct = (exact_size == optimal_size)
            print(f"    Resultado: tamanho {exact_size}, tempo {exact_time:.4f}s, {'✓' if exact_correct else '✗'}")
            
        except Exception as e:
            print(f"    Erro: {e}")
            exact_size, exact_time, exact_correct = 0, 30.0, False
        
        # Testar heurística
        print("  Executando heurística gulosa...")
        try:
            heur_clique, heur_size, heur_time = solve_maximum_clique_heuristic(graph)
            
            heur_quality = heur_size / optimal_size if optimal_size > 0 else 0
            print(f"    Resultado: tamanho {heur_size}, tempo {heur_time:.6f}s, qualidade {heur_quality:.3f}")
            
        except Exception as e:
            print(f"    Erro: {e}")
            heur_size, heur_time, heur_quality = 0, 0.0, 0.0
        
        # Calcular speedup
        speedup = exact_time / heur_time if heur_time > 0 else float('inf')
        
        results.append({
            'graph': graph_name,
            'nodes': len(graph.nodes()),
            'edges': len(graph.edges()),
            'optimal': optimal_size,
            'exact_size': exact_size,
            'exact_time': exact_time,
            'exact_correct': exact_correct,
            'heur_size': heur_size,
            'heur_time': heur_time,
            'heur_quality': heur_quality,
            'speedup': speedup
        })
        
        print()
    
    # Resumo dos resultados
    print("=" * 60)
    print("RESUMO DOS TESTES")
    print("=" * 60)
    
    total_tests = len(results)
    exact_correct_count = sum(1 for r in results if r['exact_correct'])
    avg_heur_quality = sum(r['heur_quality'] for r in results) / total_tests
    avg_speedup = sum(r['speedup'] for r in results if r['speedup'] != float('inf')) / total_tests
    
    print(f"Total de testes: {total_tests}")
    print(f"Algoritmo exato correto: {exact_correct_count}/{total_tests}")
    print(f"Qualidade média da heurística: {avg_heur_quality:.3f}")
    print(f"Speedup médio: {avg_speedup:.1f}x")
    print()
    
    # Tabela detalhada
    print("RESULTADOS DETALHADOS:")
    print(f"{'Grafo':<15} {'Nós':>4} {'Ótimo':>5} {'Exato':>5} {'Heur':>5} {'Qual':>5} {'Speedup':>8}")
    print("-" * 60)
    
    for r in results:
        speedup_str = f"{r['speedup']:.1f}x" if r['speedup'] != float('inf') else "∞"
        print(f"{r['graph']:<15} {r['nodes']:>4} {r['optimal']:>5} {r['exact_size']:>5} "
              f"{r['heur_size']:>5} {r['heur_quality']:>5.3f} {speedup_str:>8}")
    
    print()
    
    if exact_correct_count == total_tests:
        print("✓ TODOS OS TESTES PASSARAM!")
        print("Os algoritmos estão funcionando corretamente.")
        print("Pronto para executar nos dados DIMACS.")
    else:
        print("✗ Alguns testes falharam.")
        print("Verifique a implementação antes de prosseguir.")
    
    return results


if __name__ == "__main__":
    test_algorithms()
