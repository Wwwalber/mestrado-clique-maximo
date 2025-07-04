"""
Módulo de utilitários para testes e comparações do algoritmo CliSAT.
Inclui geradores de grafos de teste e funções de benchmark.
"""

import networkx as nx
import numpy as np
import time
import random
from typing import List, Tuple, Dict
import matplotlib.pyplot as plt
from clisat_algorithm import solve_maximum_clique_clisat


def generate_random_graph(n: int, p: float, seed: int = None) -> nx.Graph:
    """
    Gerar grafo aleatório usando modelo Erdős–Rényi.
    
    Args:
        n: Número de vértices
        p: Probabilidade de aresta entre cada par de vértices
        seed: Semente para reprodutibilidade
        
    Returns:
        Grafo NetworkX
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    return nx.erdos_renyi_graph(n, p, seed=seed)


def generate_planted_clique_graph(n: int, clique_size: int, p: float = 0.5, seed: int = None) -> Tuple[nx.Graph, List]:
    """
    Gerar grafo com clique plantado (planted clique).
    
    Args:
        n: Número total de vértices
        clique_size: Tamanho do clique plantado
        p: Probabilidade de arestas fora do clique
        seed: Semente para reprodutibilidade
        
    Returns:
        Tuple contendo (grafo, vértices_do_clique_plantado)
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    if clique_size > n:
        raise ValueError("Tamanho do clique não pode ser maior que o número de vértices")
    
    # Criar grafo base
    G = nx.erdos_renyi_graph(n, p, seed=seed)
    
    # Selecionar vértices para o clique plantado
    clique_vertices = random.sample(list(G.nodes()), clique_size)
    
    # Garantir que o clique plantado seja completo
    for i in clique_vertices:
        for j in clique_vertices:
            if i != j:
                G.add_edge(i, j)
    
    return G, clique_vertices


def generate_dimacs_like_graph(n: int, density: float = 0.5, seed: int = None) -> nx.Graph:
    """
    Gerar grafo similar aos benchmarks DIMACS.
    
    Args:
        n: Número de vértices
        density: Densidade do grafo (0 a 1)
        seed: Semente para reprodutibilidade
        
    Returns:
        Grafo NetworkX
    """
    if seed is not None:
        np.random.seed(seed)
        random.seed(seed)
    
    # Usar modelo de grafo aleatório com densidade específica
    m = int(density * n * (n - 1) / 2)  # Número de arestas
    return nx.gnm_random_graph(n, m, seed=seed)


def benchmark_algorithm(graph: nx.Graph, algorithm_name: str = "CliSAT", time_limit: float = 300.0) -> Dict:
    """
    Executar benchmark de um algoritmo em um grafo.
    
    Args:
        graph: Grafo para teste
        algorithm_name: Nome do algoritmo
        time_limit: Tempo limite em segundos
        
    Returns:
        Dicionário com resultados do benchmark
    """
    print(f"\n=== Benchmark {algorithm_name} ===")
    print(f"Grafo: {len(graph.nodes())} vértices, {len(graph.edges())} arestas")
    print(f"Densidade: {nx.density(graph):.3f}")
    
    start_time = time.time()
    
    try:
        if algorithm_name == "CliSAT":
            clique, size = solve_maximum_clique_clisat(graph, time_limit)
        elif algorithm_name == "NetworkX":
            # Usar algoritmo de clique máximo do NetworkX para comparação
            cliques = list(nx.find_cliques(graph))
            if cliques:
                clique = max(cliques, key=len)
                size = len(clique)
            else:
                clique, size = [], 0
        else:
            raise ValueError(f"Algoritmo '{algorithm_name}' não reconhecido")
        
        elapsed_time = time.time() - start_time
        
        # Verificar se o resultado é válido
        is_valid = verify_clique(graph, clique)
        
        result = {
            'algorithm': algorithm_name,
            'clique': clique,
            'size': size,
            'time': elapsed_time,
            'valid': is_valid,
            'graph_nodes': len(graph.nodes()),
            'graph_edges': len(graph.edges()),
            'density': nx.density(graph)
        }
        
        print(f"Resultado: clique de tamanho {size}")
        print(f"Tempo: {elapsed_time:.2f}s")
        print(f"Válido: {'Sim' if is_valid else 'Não'}")
        
        return result
        
    except Exception as e:
        elapsed_time = time.time() - start_time
        print(f"Erro durante execução: {e}")
        return {
            'algorithm': algorithm_name,
            'clique': [],
            'size': 0,
            'time': elapsed_time,
            'valid': False,
            'error': str(e),
            'graph_nodes': len(graph.nodes()),
            'graph_edges': len(graph.edges()),
            'density': nx.density(graph)
        }


def verify_clique(graph: nx.Graph, vertices: List) -> bool:
    """
    Verificar se um conjunto de vértices forma um clique válido.
    
    Args:
        graph: Grafo
        vertices: Lista de vértices
        
    Returns:
        True se for um clique válido, False caso contrário
    """
    if not vertices:
        return True
    
    # Verificar se todos os vértices existem no grafo
    if not all(v in graph.nodes() for v in vertices):
        return False
    
    # Verificar se todos os pares são adjacentes
    for i, v in enumerate(vertices):
        for u in vertices[i+1:]:
            if not graph.has_edge(v, u):
                return False
    
    return True


def compare_algorithms(graph: nx.Graph, time_limit: float = 300.0) -> Dict:
    """
    Comparar CliSAT com algoritmo do NetworkX.
    
    Args:
        graph: Grafo para teste
        time_limit: Tempo limite para cada algoritmo
        
    Returns:
        Dicionário com resultados da comparação
    """
    results = {}
    
    # Testar CliSAT
    results['CliSAT'] = benchmark_algorithm(graph, "CliSAT", time_limit)
    
    # Testar NetworkX (apenas para grafos pequenos)
    if len(graph.nodes()) <= 50:  # Limite para evitar tempos muito longos
        results['NetworkX'] = benchmark_algorithm(graph, "NetworkX", time_limit)
    else:
        print("\nGrafo muito grande para comparação com NetworkX")
        results['NetworkX'] = None
    
    # Resumo da comparação
    print(f"\n=== Resumo da Comparação ===")
    clisat_result = results['CliSAT']
    print(f"CliSAT: tamanho {clisat_result['size']}, tempo {clisat_result['time']:.2f}s")
    
    if results['NetworkX']:
        nx_result = results['NetworkX']
        print(f"NetworkX: tamanho {nx_result['size']}, tempo {nx_result['time']:.2f}s")
        
        if clisat_result['size'] >= nx_result['size']:
            print("✓ CliSAT encontrou clique de tamanho igual ou maior")
        else:
            print("⚠ NetworkX encontrou clique maior")
    
    return results


def run_test_suite():
    """Executar suite de testes com diferentes tipos de grafos."""
    print("=== Suite de Testes CliSAT ===\n")
    
    test_cases = [
        {
            'name': 'Grafo Pequeno Denso',
            'graph': generate_random_graph(10, 0.7, seed=42),
            'time_limit': 60
        },
        {
            'name': 'Clique Plantado',
            'graph': generate_planted_clique_graph(15, 5, 0.3, seed=42)[0],
            'time_limit': 60
        },
        {
            'name': 'Grafo Médio',
            'graph': generate_random_graph(20, 0.5, seed=42),
            'time_limit': 120
        },
        {
            'name': 'Grafo Esparso',
            'graph': generate_random_graph(25, 0.2, seed=42),
            'time_limit': 120
        },
        {
            'name': 'Grafo DIMACS-like',
            'graph': generate_dimacs_like_graph(30, 0.4, seed=42),
            'time_limit': 300
        }
    ]
    
    all_results = []
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n{'='*50}")
        print(f"Teste {i}: {test_case['name']}")
        print(f"{'='*50}")
        
        results = compare_algorithms(test_case['graph'], test_case['time_limit'])
        results['test_name'] = test_case['name']
        all_results.append(results)
    
    # Resumo final
    print(f"\n{'='*50}")
    print("RESUMO FINAL")
    print(f"{'='*50}")
    
    for result in all_results:
        clisat = result['CliSAT']
        print(f"\n{result['test_name']}:")
        print(f"  CliSAT: tamanho {clisat['size']}, tempo {clisat['time']:.2f}s")
        if result['NetworkX']:
            nx_res = result['NetworkX']
            print(f"  NetworkX: tamanho {nx_res['size']}, tempo {nx_res['time']:.2f}s")
    
    return all_results


def visualize_graph_with_clique(graph: nx.Graph, clique: List, title: str = "Grafo com Clique Máximo"):
    """
    Visualizar grafo destacando o clique encontrado.
    
    Args:
        graph: Grafo NetworkX
        clique: Lista de vértices do clique
        title: Título do gráfico
    """
    plt.figure(figsize=(12, 8))
    
    # Layout do grafo
    pos = nx.spring_layout(graph, seed=42)
    
    # Desenhar todas as arestas em cinza claro
    nx.draw_networkx_edges(graph, pos, edge_color='lightgray', alpha=0.5)
    
    # Destacar arestas do clique
    if len(clique) > 1:
        clique_edges = [(u, v) for u in clique for v in clique if u != v and graph.has_edge(u, v)]
        nx.draw_networkx_edges(graph, pos, edgelist=clique_edges, 
                              edge_color='red', width=2, alpha=0.8)
    
    # Desenhar todos os nós
    non_clique_nodes = [n for n in graph.nodes() if n not in clique]
    if non_clique_nodes:
        nx.draw_networkx_nodes(graph, pos, nodelist=non_clique_nodes, 
                              node_color='lightblue', node_size=300, alpha=0.7)
    
    # Destacar nós do clique
    if clique:
        nx.draw_networkx_nodes(graph, pos, nodelist=clique, 
                              node_color='red', node_size=500, alpha=0.9)
    
    # Adicionar rótulos
    nx.draw_networkx_labels(graph, pos, font_size=10, font_weight='bold')
    
    plt.title(f"{title}\nClique: {clique} (tamanho: {len(clique)})")
    plt.axis('off')
    plt.tight_layout()
    plt.show()


if __name__ == "__main__":
    # Executar suite de testes
    results = run_test_suite()
    
    # Exemplo de visualização
    print("\n=== Exemplo de Visualização ===")
    G, planted_clique = generate_planted_clique_graph(12, 4, 0.3, seed=42)
    clique, size = solve_maximum_clique_clisat(G, time_limit=60)
    
    print(f"Clique plantado: {planted_clique}")
    print(f"Clique encontrado: {clique}")
    
    # Descomentar para mostrar visualização (requer display)
    # visualize_graph_with_clique(G, clique, "Exemplo: Clique Plantado vs Encontrado")
