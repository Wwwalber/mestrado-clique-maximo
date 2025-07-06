"""
Script Principal para Execução do CliSAT com Grafos DIMACS

Este script oferece uma interface de linha de comando para:
1. Baixar grafos DIMACS
2. Executar testes individuais
3. Executar suítes de benchmark
4. Comparar resultados
"""

import argparse
import sys
import os
import json
from typing import List, Optional
import logging

from dimacs_loader import DIMACSLoader
from benchmark_clisat import CliSATBenchmark
from clisat_algortithmb import CliSAT

def setup_logging(verbose: bool = False):
    """Configurar sistema de logging."""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )

def list_graphs(loader: DIMACSLoader, max_size: Optional[int] = None):
    """Listar grafos disponíveis."""
    print("Grafos DIMACS disponíveis:")
    print("-" * 80)
    print(f"{'Nome':<20} {'Vértices':<10} {'Clique Conhecido':<15} {'Status':<10}")
    print("-" * 80)
    
    for name in sorted(loader.list_available_graphs()):
        info = loader.get_graph_info(name)
        if max_size and info['size'] > max_size:
            continue
            
        # Verificar se já foi baixado
        local_file = os.path.join(loader.data_dir, f"{name}.clq")
        status = "Baixado" if os.path.exists(local_file) else "Disponível"
        
        print(f"{name:<20} {info['size']:<10} {info['known_clique']:<15} {status:<10}")

def download_graphs(loader: DIMACSLoader, graph_names: Optional[List[str]] = None, 
                   max_size: Optional[int] = None):
    """Baixar grafos específicos ou suíte de teste."""
    if graph_names:
        # Baixar grafos específicos
        print(f"Baixando {len(graph_names)} grafos...")
        for name in graph_names:
            if loader.download_graph(name):
                print(f"✓ {name}")
            else:
                print(f"✗ {name}")
    else:
        # Baixar suíte de teste
        print(f"Baixando suíte de teste (max_size={max_size})...")
        downloaded = loader.download_test_suite(max_size)
        print(f"Baixados {len(downloaded)} grafos com sucesso.")

def run_single_test(graph_name: str, time_limit: float = 300.0, verbose: bool = False):
    """Executar teste em um único grafo."""
    print(f"Executando CliSAT no grafo {graph_name}...")
    print(f"Limite de tempo: {time_limit}s")
    print("-" * 50)
    
    # Criar benchmark e executar teste
    benchmark = CliSATBenchmark()
    result = benchmark.run_single_test(graph_name, time_limit)
    
    # Mostrar resultado
    if result['status'] == 'COMPLETED':
        print(f"✓ Teste concluído com sucesso!")
        print(f"  Grafo: {result['num_vertices']} vértices, {result['num_edges']} arestas")
        print(f"  Densidade: {result['density']:.3f}")
        print(f"  Clique encontrado: {result['found_clique_size']}")
        print(f"  Clique conhecido: {result.get('known_clique_size', 'N/A')}")
        print(f"  Tempo execução: {result['execution_time']:.2f}s")
        print(f"  Clique válido: {result['is_valid_clique']}")
        
        if result.get('is_optimal') is not None:
            print(f"  Solução ótima: {result['is_optimal']}")
        if result.get('gap') is not None:
            print(f"  Gap: {result['gap']:.1f}%")
            
        if verbose:
            print(f"  Estatísticas:")
            for key, value in result['stats'].items():
                print(f"    {key}: {value}")
            print(f"  Clique: {result['clique']}")
    else:
        print(f"✗ Erro durante execução:")
        print(f"  {result.get('error', 'Erro desconhecido')}")

def run_benchmark_suite(max_size: Optional[int] = None, time_limit: float = 300.0,
                       custom_graphs: Optional[List[str]] = None):
    """Executar suíte completa de benchmark."""
    print("Executando suíte de benchmark...")
    if custom_graphs:
        print(f"Grafos personalizados: {', '.join(custom_graphs)}")
    else:
        print(f"Tamanho máximo: {max_size}")
    print(f"Limite de tempo por grafo: {time_limit}s")
    print("-" * 50)
    
    # Criar e executar benchmark
    benchmark = CliSATBenchmark()
    results = benchmark.run_benchmark_suite(
        max_graph_size=max_size,
        time_limit_per_graph=time_limit,
        custom_graphs=custom_graphs
    )
    
    # Mostrar resumo
    completed = [r for r in results if r['status'] == 'COMPLETED']
    optimal = [r for r in completed if r.get('is_optimal', False)]
    
    print(f"\n{'='*50}")
    print(f"RESUMO DO BENCHMARK")
    print(f"{'='*50}")
    print(f"Grafos testados: {len(results)}")
    print(f"Testes concluídos: {len(completed)}")
    print(f"Soluções ótimas: {len(optimal)}")
    if completed:
        print(f"Taxa de sucesso: {len(completed)/len(results)*100:.1f}%")
        print(f"Taxa de otimalidade: {len(optimal)/len(completed)*100:.1f}%")
    
    # Gerar gráficos
    try:
        benchmark.generate_plots(results)
        print("Gráficos de análise gerados.")
    except Exception as e:
        print(f"Erro ao gerar gráficos: {e}")

def compare_with_known(results_file: str):
    """Comparar resultados com valores conhecidos."""
    try:
        with open(results_file, 'r') as f:
            results = json.load(f)
    except Exception as e:
        print(f"Erro ao carregar arquivo de resultados: {e}")
        return
    
    print("Comparação com valores conhecidos:")
    print("-" * 80)
    print(f"{'Grafo':<20} {'Encontrado':<10} {'Conhecido':<10} {'Status':<15} {'Gap':<10}")
    print("-" * 80)
    
    for result in results:
        if result['status'] != 'COMPLETED':
            continue
            
        found = result['found_clique_size']
        known = result.get('known_clique_size')
        
        if known:
            if found == known:
                status = "ÓTIMO"
                gap = "0.0%"
            elif found > known:
                status = "MELHOR QUE CONHECIDO!"
                gap = f"+{(found-known)/known*100:.1f}%"
            else:
                status = "SUBÓTIMO"
                gap = f"{result.get('gap', 0):.1f}%"
        else:
            status = "DESCONHECIDO"
            gap = "N/A"
        
        print(f"{result['graph_name']:<20} {found:<10} {known or 'N/A':<10} {status:<15} {gap:<10}")

def main():
    """Função principal com interface de linha de comando."""
    parser = argparse.ArgumentParser(
        description="CliSAT: Algoritmo SAT para Clique Máximo com Grafos DIMACS",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Listar grafos disponíveis
  python run_clisat.py --list

  # Baixar grafos pequenos (até 200 vértices)
  python run_clisat.py --download --max-size 200

  # Executar teste em um grafo específico
  python run_clisat.py --test brock200_1 --time-limit 180

  # Executar benchmark completo
  python run_clisat.py --benchmark --max-size 300 --time-limit 300

  # Executar teste em grafos específicos
  python run_clisat.py --benchmark --graphs brock200_1 brock200_2 C125.9

  # Comparar resultados
  python run_clisat.py --compare benchmark_results/benchmark_results_20250101_120000.json
        """
    )
    
    # Argumentos principais
    parser.add_argument('--list', action='store_true',
                       help='Listar grafos DIMACS disponíveis')
    parser.add_argument('--download', action='store_true',
                       help='Baixar grafos DIMACS')
    parser.add_argument('--test', type=str, metavar='GRAPH',
                       help='Executar teste em um grafo específico')
    parser.add_argument('--benchmark', action='store_true',
                       help='Executar suíte completa de benchmark')
    parser.add_argument('--compare', type=str, metavar='FILE',
                       help='Comparar resultados com valores conhecidos')
    
    # Parâmetros
    parser.add_argument('--max-size', type=int, default=None,
                       help='Tamanho máximo dos grafos (padrão: todos)')
    parser.add_argument('--time-limit', type=float, default=300.0,
                       help='Limite de tempo em segundos (padrão: 300)')
    parser.add_argument('--graphs', nargs='+', metavar='GRAPH',
                       help='Lista específica de grafos para testar')
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Saída detalhada')
    
    args = parser.parse_args()
    
    # Configurar logging
    setup_logging(args.verbose)
    
    # Verificar se pelo menos uma ação foi especificada
    if not any([args.list, args.download, args.test, args.benchmark, args.compare]):
        parser.print_help()
        return
    
    # Criar loader
    loader = DIMACSLoader()
    
    # Executar ações
    if args.list:
        list_graphs(loader, args.max_size)
    
    if args.download:
        download_graphs(loader, args.graphs, args.max_size)
    
    if args.test:
        run_single_test(args.test, args.time_limit, args.verbose)
    
    if args.benchmark:
        run_benchmark_suite(args.max_size, args.time_limit, args.graphs)
    
    if args.compare:
        compare_with_known(args.compare)

if __name__ == "__main__":
    main()
