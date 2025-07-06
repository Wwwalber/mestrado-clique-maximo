#!/usr/bin/env python3
"""
Script Principal da Atividade APA - Análise e Projeto de Algoritmos

OBJETIVO: Implementar e avaliar algoritmos para o problema do clique máximo

ALGORITMOS IMPLEMENTADOS:
1. Algoritmo Exato: CliSAT (SAT-based exact algorithm)
2. Heurística: Gulosa baseada em grau (Greedy degree-based heuristic)

EXECUÇÃO:
python run_apa_activity.py --mode [test|small|medium|full] --time-limit [segundos]

INSTÂNCIAS TESTADAS (conforme solicitado pelo professor):
- Série C: C125.9, C250.9, C500.9, C1000.9, C2000.9
- Série DSJC: DSJC500_5, DSJC1000_5  
- Série brock: brock200_2, brock200_4, brock400_2, brock400_4, brock800_2, brock800_4
- Série gen: gen200_p0.9_44, gen200_p0.9_55, gen400_p0.9_55, gen400_p0.9_65, gen400_p0.9_75
- Série MANN: MANN_a27, MANN_a45, MANN_a81
- Série hamming: hamming8-4, hamming10-4
- Série keller: keller4, keller5, keller6
- Série p_hat: p_hat300-1/2/3, p_hat700-1/2/3, p_hat1500-1/2/3
- Outras: C2000.5, C4000.5

Autor: Walber
Disciplina: Análise e Projeto de Algoritmos (Mestrado)
Data: Julho 2025
"""

import argparse
import sys
import time
from pathlib import Path

# Adicionar diretório atual ao path
sys.path.append(str(Path(__file__).parent))

from apa_results_generator import run_apa_experiments, APAResultsGenerator
from apa_instance_manager import APAInstanceManager


def print_header():
    """Imprimir cabeçalho da atividade."""
    print("=" * 70)
    print("           ATIVIDADE APA - ALGORITMOS PARA CLIQUE MÁXIMO")
    print("                Análise e Projeto de Algoritmos")
    print("=" * 70)
    print()
    print("ALGORITMOS IMPLEMENTADOS:")
    print("1. Algoritmo Exato: CliSAT (SAT-based exact algorithm)")
    print("   - Baseado em SAT solving com branch-and-bound")
    print("   - Complexidade exponencial, mas exato")
    print("   - Referência: San Segundo et al. (2016)")
    print()
    print("2. Heurística: Gulosa baseada em grau")
    print("   - Seleção gulosa por maior grau efetivo")
    print("   - Complexidade O(n³)")
    print("   - Referência: Johnson & Trick (1996)")
    print()


def define_instance_groups():
    """Definir grupos de instâncias por dificuldade."""
    groups = {
        'test': ['C125.9', 'brock200_2', 'gen200_p0.9_44'],
        
        'small': [
            'C125.9', 'brock200_2', 'brock200_4', 'gen200_p0.9_44', 
            'gen200_p0.9_55', 'p_hat300-1', 'p_hat300-2', 'keller4'
        ],
        
        'medium': [
            'C125.9', 'C250.9', 'brock200_2', 'brock200_4', 'brock400_2', 
            'brock400_4', 'gen200_p0.9_44', 'gen200_p0.9_55', 'gen400_p0.9_55',
            'gen400_p0.9_65', 'MANN_a27', 'hamming8-4', 'keller4', 'keller5',
            'p_hat300-1', 'p_hat300-2', 'p_hat300-3', 'DSJC500_5'
        ],
        
        'full': None  # Todas as instâncias da lista APA
    }
    return groups


def main():
    """Função principal do script."""
    parser = argparse.ArgumentParser(
        description="Atividade APA - Algoritmos para Clique Máximo",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
EXEMPLOS DE USO:
  python run_apa_activity.py --mode test --time-limit 60
  python run_apa_activity.py --mode small --time-limit 300  
  python run_apa_activity.py --mode medium --time-limit 600
  python run_apa_activity.py --mode full --time-limit 1800

OBSERVAÇÕES:
- Modo 'test': 3 instâncias pequenas para validação rápida
- Modo 'small': ~8 instâncias menores (recomendado para desenvolvimento)
- Modo 'medium': ~18 instâncias médias (recomendado para avaliação)
- Modo 'full': Todas as 38 instâncias da atividade (pode demorar horas)
        """
    )
    
    parser.add_argument(
        '--mode', 
        choices=['test', 'small', 'medium', 'full'],
        default='small',
        help='Grupo de instâncias para testar (default: small)'
    )
    
    parser.add_argument(
        '--time-limit',
        type=int,
        default=300,
        help='Tempo limite em segundos para o algoritmo exato (default: 300)'
    )
    
    parser.add_argument(
        '--output',
        type=str,
        default=None,
        help='Nome do arquivo de saída (default: auto-gerado)'
    )
    
    parser.add_argument(
        '--download',
        action='store_true',
        help='Baixar instâncias DIMACS antes de executar'
    )
    
    parser.add_argument(
        '--quiet',
        action='store_true',
        help='Executar em modo silencioso (menos output)'
    )
    
    args = parser.parse_args()
    
    if not args.quiet:
        print_header()
    
    # Definir grupos de instâncias
    groups = define_instance_groups()
    instances = groups[args.mode]
    
    # Configurar arquivo de saída
    if args.output is None:
        timestamp = time.strftime("%Y%m%d_%H%M%S")
        args.output = f"apa_results_{args.mode}_{timestamp}.csv"
    
    # Informações sobre a execução
    if not args.quiet:
        print(f"CONFIGURAÇÃO DA EXECUÇÃO:")
        print(f"- Modo: {args.mode}")
        print(f"- Instâncias: {len(instances) if instances else 'todas (38)'}")
        print(f"- Tempo limite (exato): {args.time_limit}s")
        print(f"- Tempo limite (heurística): {min(60, args.time_limit//5)}s")
        print(f"- Arquivo de saída: {args.output}")
        print()
        
        if instances:
            print(f"INSTÂNCIAS A SEREM TESTADAS:")
            for i, inst in enumerate(instances, 1):
                print(f"  {i:2d}. {inst}")
            print()
    
    # Baixar instâncias se solicitado
    if args.download:
        print("Baixando instâncias DIMACS...")
        manager = APAInstanceManager()
        manager.download_all_instances()
        print("Download concluído.\n")
    
    # Confirmar execução para modos longos
    if args.mode in ['medium', 'full'] and not args.quiet:
        response = input("Esta execução pode demorar bastante. Continuar? [y/N]: ")
        if response.lower() not in ['y', 'yes', 's', 'sim']:
            print("Execução cancelada.")
            return
        print()
    
    # Executar experimentos
    try:
        print("INICIANDO EXPERIMENTOS...")
        print("=" * 50)
        
        start_time = time.time()
        
        results_df = run_apa_experiments(
            instances=instances,
            time_limit_exact=args.time_limit,
            time_limit_heuristic=min(60, args.time_limit // 5),
            save_file=args.output
        )
        
        total_time = time.time() - start_time
        
        print("=" * 50)
        print("EXPERIMENTOS CONCLUÍDOS!")
        print(f"Tempo total: {total_time:.1f} segundos ({total_time/60:.1f} minutos)")
        print()
        
        # Mostrar resumo dos resultados
        if not results_df.empty:
            print("RESUMO DOS RESULTADOS:")
            print(f"- Instâncias processadas: {len(results_df)}")
            
            exact_completed = sum(results_df['Exact_Status'] == 'COMPLETED')
            heur_completed = sum(results_df['Heuristic_Status'] == 'COMPLETED')
            
            print(f"- Algoritmo exato completou: {exact_completed}/{len(results_df)}")
            print(f"- Heurística completou: {heur_completed}/{len(results_df)}")
            
            if exact_completed > 0 and heur_completed > 0:
                # Calcular estatísticas básicas
                valid_results = results_df[
                    (results_df['Exact_Status'] == 'COMPLETED') & 
                    (results_df['Heuristic_Status'] == 'COMPLETED')
                ]
                
                if not valid_results.empty:
                    avg_quality = valid_results['Quality'].mean()
                    avg_speedup = valid_results['Speedup'].mean()
                    perfect_solutions = sum(valid_results['Quality'] == 1.0)
                    
                    print(f"- Qualidade média da heurística: {avg_quality:.3f}")
                    print(f"- Speedup médio: {avg_speedup:.1f}x")
                    print(f"- Soluções ótimas encontradas pela heurística: {perfect_solutions}")
            
            print()
            print(f"Resultados salvos em: benchmark_results/{args.output}")
            print("Arquivo de apresentação: benchmark_results/" + args.output.replace('.csv', '_presentation.csv'))
            print("Resumo estatístico: benchmark_results/" + args.output.replace('.csv', '_summary.txt'))
        
    except KeyboardInterrupt:
        print("\nExecução interrompida pelo usuário.")
        sys.exit(1)
    except Exception as e:
        print(f"\nErro durante a execução: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
