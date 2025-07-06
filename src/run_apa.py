#!/usr/bin/env python3
"""
Script principal para a atividade APA - Algoritmo CliSAT

Este script fornece uma interface de linha de comando para executar
o algoritmo CliSAT nas instâncias específicas da disciplina de
Análise e Projeto de Algoritmos do mestrado.

Uso:
    python run_apa.py --help
    python run_apa.py --list
    python run_apa.py --download --max-size 500
    python run_apa.py --test C125.9 --time-limit 120
    python run_apa.py --benchmark --max-size 300 --time-limit 180
"""

import argparse
import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Adicionar diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from apa_instance_manager import APAInstanceManager
from apa_benchmark import APABenchmark


def cmd_list_instances(args):
    """Comando para listar instâncias disponíveis."""
    manager = APAInstanceManager()
    
    print("=== INSTÂNCIAS APA DISPONÍVEIS ===\n")
    
    instances = manager.list_instances(
        max_nodes=args.max_size,
        min_nodes=args.min_size
    )
    
    if not instances:
        print("Nenhuma instância encontrada com os filtros especificados.")
        return
    
    print(f"Total: {len(instances)} instâncias\n")
    
    # Agrupar por família para melhor organização
    families = {}
    for instance in instances:
        family = instance.split('_')[0] if '_' in instance else instance.split('.')[0]
        if family not in families:
            families[family] = []
        families[family].append(instance)
    
    for family, family_instances in sorted(families.items()):
        print(f"Família {family}:")
        for instance in sorted(family_instances):
            info = manager.get_instance_info(instance)
            print(f"  {instance:<15} - {info['nodes']:>4} nós, {info['edges']:>8,} arestas, "
                  f"densidade {info['density']:.3f}")
        print()


def cmd_download_instances(args):
    """Comando para baixar instâncias."""
    manager = APAInstanceManager()
    
    if args.instances:
        # Baixar instâncias específicas
        instances = args.instances
        print(f"Baixando {len(instances)} instâncias específicas...")
    else:
        # Baixar todas ou filtradas por tamanho
        instances = manager.list_instances(max_nodes=args.max_size)
        print(f"Baixando {len(instances)} instâncias (máximo {args.max_size} nós)...")
    
    downloaded = manager.download_all_instances(
        max_nodes=args.max_size if not args.instances else None,
        force=args.force
    )
    
    print(f"\nDownload concluído: {len(downloaded)} instâncias baixadas com sucesso")


def cmd_test_single(args):
    """Comando para testar uma única instância."""
    benchmark = APABenchmark()
    
    print(f"=== TESTE INDIVIDUAL: {args.instance} ===\n")
    
    result = benchmark.run_single_test(
        args.instance,
        time_limit=args.time_limit,
        verbose=True
    )
    
    print(f"\n=== RESULTADO ===")
    if result['status'] == 'SUCCESS':
        print(f"✓ Sucesso!")
        print(f"  Clique encontrado: {result['found_clique_size']}")
        print(f"  Tempo: {result['execution_time']:.2f}s")
        
        if result.get('known_optimal'):
            gap = result.get('gap_percent', 0)
            print(f"  Ótimo conhecido: {result['known_optimal']}")
            print(f"  Gap: {gap:.1f}%")
            print(f"  Ótimo encontrado: {'Sim' if gap == 0 else 'Não'}")
        
        print(f"  Clique válido: {'Sim' if result['is_valid_clique'] else 'Não'}")
    else:
        print(f"✗ Falha: {result.get('error', result['status'])}")


def cmd_run_benchmark(args):
    """Comando para executar benchmark."""
    benchmark = APABenchmark()
    
    if args.instances:
        instances = args.instances
        print(f"=== BENCHMARK PERSONALIZADO ===")
        print(f"Instâncias específicas: {len(instances)}")
    else:
        instances = None
        print(f"=== BENCHMARK COMPLETO ===")
        if args.max_size:
            print(f"Filtro: máximo {args.max_size} nós")
    
    print(f"Tempo limite por instância: {args.time_limit}s")
    print()
    
    results = benchmark.run_benchmark_suite(
        instances=instances,
        max_nodes=args.max_size,
        time_limit=args.time_limit,
        save_results=True
    )
    
    # Gerar relatório se solicitado
    if args.generate_report and results:
        print("\nGerando relatório de análise...")
        # Encontrar arquivo mais recente
        results_files = list(benchmark.results_dir.glob("apa_benchmark_*.json"))
        if results_files:
            latest_file = max(results_files, key=lambda f: f.stat().st_mtime)
            benchmark.generate_analysis_report(str(latest_file))
            print("Relatório gerado com sucesso!")


def cmd_show_summary(args):
    """Comando para mostrar resumo das instâncias."""
    manager = APAInstanceManager()
    manager.print_summary()


def cmd_analyze_results(args):
    """Comando para analisar resultados existentes."""
    benchmark = APABenchmark()
    
    if not Path(args.results_file).exists():
        print(f"Arquivo de resultados não encontrado: {args.results_file}")
        return
    
    print(f"Analisando resultados de: {args.results_file}")
    benchmark.generate_analysis_report(args.results_file, args.output_dir)
    print("Análise concluída!")


def main():
    """Função principal."""
    parser = argparse.ArgumentParser(
        description="Algoritmo CliSAT para Análise e Projeto de Algoritmos",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:
  
  # Listar todas as instâncias
  python run_apa.py --list
  
  # Listar instâncias pequenas
  python run_apa.py --list --max-size 300
  
  # Baixar instâncias pequenas
  python run_apa.py --download --max-size 500
  
  # Testar uma instância específica
  python run_apa.py --test C125.9 --time-limit 120
  
  # Benchmark em instâncias pequenas
  python run_apa.py --benchmark --max-size 300 --time-limit 180
  
  # Benchmark em instâncias específicas
  python run_apa.py --benchmark --instances C125.9 C250.9 brock200_2
  
  # Analisar resultados existentes
  python run_apa.py --analyze benchmark_results/apa_benchmark_20250101_120000.json
        """
    )
    
    # Argumentos globais
    parser.add_argument('--max-size', type=int, help='Número máximo de nós')
    parser.add_argument('--min-size', type=int, help='Número mínimo de nós')
    parser.add_argument('--time-limit', type=float, default=300.0, 
                       help='Tempo limite em segundos (padrão: 300)')
    parser.add_argument('--instances', nargs='+', help='Instâncias específicas')
    parser.add_argument('--force', action='store_true', 
                       help='Forçar download mesmo se arquivo existir')
    parser.add_argument('--quiet', action='store_true', help='Modo silencioso')
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponíveis')
    
    # Comando list
    parser_list = subparsers.add_parser('list', help='Listar instâncias disponíveis')
    
    # Comando download
    parser_download = subparsers.add_parser('download', help='Baixar instâncias')
    
    # Comando test
    parser_test = subparsers.add_parser('test', help='Testar uma instância')
    parser_test.add_argument('instance', help='Nome da instância')
    
    # Comando benchmark
    parser_benchmark = subparsers.add_parser('benchmark', help='Executar benchmark')
    parser_benchmark.add_argument('--generate-report', action='store_true',
                                help='Gerar relatório de análise')
    
    # Comando summary
    parser_summary = subparsers.add_parser('summary', help='Mostrar resumo das instâncias')
    
    # Comando analyze
    parser_analyze = subparsers.add_parser('analyze', help='Analisar resultados')
    parser_analyze.add_argument('results_file', help='Arquivo JSON com resultados')
    parser_analyze.add_argument('--output-dir', help='Diretório de saída')
    
    # Parse arguments
    args = parser.parse_args()
    
    # Configurar logging
    if args.quiet:
        logging.getLogger().setLevel(logging.WARNING)
    
    # Executar comando
    if args.command == 'list':
        cmd_list_instances(args)
    elif args.command == 'download':
        cmd_download_instances(args)
    elif args.command == 'test':
        cmd_test_single(args)
    elif args.command == 'benchmark':
        cmd_run_benchmark(args)
    elif args.command == 'summary':
        cmd_show_summary(args)
    elif args.command == 'analyze':
        cmd_analyze_results(args)
    else:
        # Modo compatibilidade - argumentos antigos
        if args.instances and len(args.instances) == 1 and not any([
            args.command, '--download' in sys.argv, '--benchmark' in sys.argv
        ]):
            # Assumir teste individual
            args.instance = args.instances[0]
            cmd_test_single(args)
        else:
            parser.print_help()


if __name__ == "__main__":
    main()
