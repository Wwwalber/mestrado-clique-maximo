"""
Sistema de benchmark CliSAT para instâncias APA.

Este módulo fornece funcionalidades específicas para avaliar o algoritmo CliSAT
nas instâncias selecionadas para a disciplina de Análise e Projeto de Algoritmos.
"""

import json
import time
import pandas as pd
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Optional, Tuple
import matplotlib.pyplot as plt
import seaborn as sns
import networkx as nx
import logging

from clisat_algorithm import CliSATSolver, solve_maximum_clique_clisat
from apa_instance_manager import APAInstanceManager

logger = logging.getLogger(__name__)


class APABenchmark:
    """Sistema de benchmark para as instâncias APA."""
    
    def __init__(self, results_dir: str = "benchmark_results"):
        """
        Inicializar sistema de benchmark.
        
        Args:
            results_dir: Diretório para salvar resultados
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        self.instance_manager = APAInstanceManager()
        
        # Valores ótimos conhecidos (quando disponíveis)
        self.known_optima = {
            'C125.9': 34,
            'C250.9': 44,
            'C500.9': 57,
            'C1000.9': 68,
            'C2000.9': 80,
            'DSJC1000_5': 15,
            'DSJC500_5': 13,
            'C2000.5': 16,
            'C4000.5': 18,
            'MANN_a27': 126,
            'MANN_a45': 345,
            'MANN_a81': 1100,
            'brock200_2': 12,
            'brock200_4': 17,
            'brock400_2': 29,
            'brock400_4': 33,
            'brock800_2': 24,
            'brock800_4': 26,
            'gen200_p0.9_44': 44,
            'gen200_p0.9_55': 55,
            'gen400_p0.9_55': 55,
            'gen400_p0.9_65': 65,
            'gen400_p0.9_75': 75,
            'hamming10-4': 40,
            'hamming8-4': 16,
            'keller4': 11,
            'keller5': 27,
            'keller6': 59,
            'p_hat300-1': 8,
            'p_hat300-2': 25,
            'p_hat300-3': 36,
            'p_hat700-1': 11,
            'p_hat700-2': 44,
            'p_hat700-3': 62,
            'p_hat1500-1': 12,
            'p_hat1500-2': 65,
            'p_hat1500-3': 94
        }
    
    def run_single_test(self, instance_name: str, time_limit: float = 300.0,
                       verbose: bool = True) -> Dict:
        """
        Executar teste em uma única instância.
        
        Args:
            instance_name: Nome da instância
            time_limit: Limite de tempo em segundos
            verbose: Imprimir informações detalhadas
            
        Returns:
            Dicionário com resultados do teste
        """
        if verbose:
            print(f"\n=== Testando {instance_name} ===")
        
        # Obter informações da instância
        instance_info = self.instance_manager.get_instance_info(instance_name)
        
        if verbose:
            print(f"Nós: {instance_info['nodes']}")
            print(f"Arestas: {instance_info['edges']:,}")
            print(f"Densidade: {instance_info['density']:.3f}")
            print(f"Ótimo conhecido: {self.known_optima.get(instance_name, 'N/A')}")
        
        # Carregar grafo
        try:
            graph = self.instance_manager.load_graph(instance_name)
        except Exception as e:
            return {
                'instance_name': instance_name,
                'status': 'LOAD_ERROR',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
        
        # Executar CliSAT
        start_time = time.time()
        
        try:
            solver = CliSATSolver(graph, time_limit=time_limit)
            clique_nodes, clique_size = solver.solve()
            
            execution_time = time.time() - start_time
            
            # Verificar se é um clique válido
            is_valid_clique = self._verify_clique(graph, clique_nodes)
            
            # Calcular gap se ótimo conhecido
            gap = None
            optimal_found = False
            known_optimal = self.known_optima.get(instance_name)
            
            if known_optimal is not None:
                gap = (known_optimal - clique_size) / known_optimal * 100
                optimal_found = (clique_size == known_optimal)
            
            result = {
                'instance_name': instance_name,
                'status': 'SUCCESS',
                'nodes': instance_info['nodes'],
                'edges': instance_info['edges'],
                'density': instance_info['density'],
                'found_clique_size': clique_size,
                'known_optimal': known_optimal,
                'gap_percent': gap,
                'optimal_found': optimal_found,
                'execution_time': execution_time,
                'time_limit': time_limit,
                'timeout': execution_time >= time_limit * 0.98,  # Considera timeout se ≥ 98% do tempo
                'is_valid_clique': is_valid_clique,
                'solver_stats': solver.stats if hasattr(solver, 'stats') else {},
                'timestamp': datetime.now().isoformat()
            }
            
            if verbose:
                print(f"Resultado: {clique_size}")
                print(f"Tempo: {execution_time:.2f}s")
                print(f"Gap: {gap:.1f}%" if gap is not None else "Gap: N/A")
                print(f"Ótimo: {'Sim' if optimal_found else 'Não'}")
                print(f"Válido: {'Sim' if is_valid_clique else 'Não'}")
            
            return result
            
        except Exception as e:
            execution_time = time.time() - start_time
            
            result = {
                'instance_name': instance_name,
                'status': 'SOLVER_ERROR',
                'nodes': instance_info['nodes'],
                'edges': instance_info['edges'],
                'density': instance_info['density'],
                'execution_time': execution_time,
                'time_limit': time_limit,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            
            if verbose:
                print(f"ERRO: {e}")
            
            return result
    
    def run_benchmark_suite(self, instances: Optional[List[str]] = None,
                          max_nodes: Optional[int] = None,
                          time_limit: float = 300.0,
                          save_results: bool = True) -> List[Dict]:
        """
        Executar benchmark em múltiplas instâncias.
        
        Args:
            instances: Lista específica de instâncias (None para todas)
            max_nodes: Filtro por número máximo de nós
            time_limit: Limite de tempo por instância
            save_results: Salvar resultados em arquivo
            
        Returns:
            Lista de resultados
        """
        if instances is None:
            instances = self.instance_manager.list_instances(max_nodes=max_nodes)
        
        print(f"=== BENCHMARK CLISAT APA ===")
        print(f"Instâncias: {len(instances)}")
        print(f"Tempo limite por instância: {time_limit}s")
        print(f"Tempo total estimado: {len(instances) * time_limit / 60:.1f} minutos")
        print()
        
        results = []
        
        for i, instance in enumerate(instances, 1):
            print(f"[{i}/{len(instances)}] {instance}")
            
            result = self.run_single_test(instance, time_limit, verbose=False)
            results.append(result)
            
            # Resumo rápido
            if result['status'] == 'SUCCESS':
                clique_size = result['found_clique_size']
                time_taken = result['execution_time']
                optimal = result.get('optimal_found', False)
                gap = result.get('gap_percent')
                
                status_str = "ÓTIMO" if optimal else f"GAP: {gap:.1f}%" if gap is not None else "OK"
                print(f"  Resultado: {clique_size} ({time_taken:.1f}s) - {status_str}")
            else:
                print(f"  FALHA: {result.get('error', result['status'])}")
            
            print()
        
        # Salvar resultados
        if save_results:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            results_file = self.results_dir / f"apa_benchmark_{timestamp}.json"
            
            with open(results_file, 'w') as f:
                json.dump(results, f, indent=2)
            
            print(f"Resultados salvos em: {results_file}")
        
        # Imprimir resumo
        self._print_benchmark_summary(results)
        
        return results
    
    def _verify_clique(self, graph: nx.Graph, clique_nodes: List) -> bool:
        """Verificar se um conjunto de nós forma um clique válido."""
        if not clique_nodes:
            return True
        
        clique_size = len(clique_nodes)
        subgraph = graph.subgraph(clique_nodes)
        expected_edges = clique_size * (clique_size - 1) // 2
        actual_edges = len(subgraph.edges())
        
        return actual_edges == expected_edges
    
    def _print_benchmark_summary(self, results: List[Dict]):
        """Imprimir resumo dos resultados do benchmark."""
        print("=== RESUMO DO BENCHMARK ===")
        
        total = len(results)
        successful = sum(1 for r in results if r['status'] == 'SUCCESS')
        
        print(f"Total de instâncias: {total}")
        print(f"Sucessos: {successful}")
        print(f"Taxa de sucesso: {successful/total*100:.1f}%")
        
        if successful > 0:
            success_results = [r for r in results if r['status'] == 'SUCCESS']
            
            # Estatísticas de tempo
            times = [r['execution_time'] for r in success_results]
            print(f"\nTempo de execução:")
            print(f"  Médio: {sum(times)/len(times):.1f}s")
            print(f"  Mínimo: {min(times):.1f}s")
            print(f"  Máximo: {max(times):.1f}s")
            
            # Estatísticas de gap
            gaps = [r['gap_percent'] for r in success_results if r['gap_percent'] is not None]
            if gaps:
                print(f"\nGap em relação ao ótimo:")
                print(f"  Médio: {sum(gaps)/len(gaps):.1f}%")
                print(f"  Mínimo: {min(gaps):.1f}%")
                print(f"  Máximo: {max(gaps):.1f}%")
            
            # Ótimos encontrados
            optima_found = sum(1 for r in success_results if r.get('optimal_found', False))
            optima_known = sum(1 for r in success_results if r.get('known_optimal') is not None)
            
            if optima_known > 0:
                print(f"\nÓtimos encontrados: {optima_found}/{optima_known} ({optima_found/optima_known*100:.1f}%)")
    
    def generate_analysis_report(self, results_file: str, output_dir: str = None):
        """
        Gerar relatório de análise detalhado.
        
        Args:
            results_file: Arquivo JSON com resultados
            output_dir: Diretório para salvar relatório
        """
        if output_dir is None:
            output_dir = self.results_dir
        else:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
        
        # Carregar resultados
        with open(results_file, 'r') as f:
            results = json.load(f)
        
        # Filtrar sucessos
        success_results = [r for r in results if r['status'] == 'SUCCESS']
        
        if not success_results:
            print("Nenhum resultado bem-sucedido para analisar")
            return
        
        # Criar DataFrame
        df = pd.DataFrame(success_results)
        
        # Gerar gráficos
        self._generate_plots(df, output_dir)
        
        # Gerar relatório de texto
        self._generate_text_report(df, output_dir)
        
        print(f"Relatório gerado em: {output_dir}")
    
    def _generate_plots(self, df: pd.DataFrame, output_dir: Path):
        """Gerar gráficos de análise."""
        plt.style.use('default')
        
        # 1. Tempo vs Tamanho do grafo
        plt.figure(figsize=(10, 6))
        plt.scatter(df['nodes'], df['execution_time'], alpha=0.7)
        plt.xlabel('Número de Nós')
        plt.ylabel('Tempo de Execução (s)')
        plt.title('Tempo de Execução vs Tamanho do Grafo')
        plt.yscale('log')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'tempo_vs_tamanho.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Gap vs Densidade
        gap_df = df[df['gap_percent'].notna()]
        if not gap_df.empty:
            plt.figure(figsize=(10, 6))
            plt.scatter(gap_df['density'], gap_df['gap_percent'], alpha=0.7)
            plt.xlabel('Densidade do Grafo')
            plt.ylabel('Gap (%)')
            plt.title('Gap vs Densidade do Grafo')
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir / 'gap_vs_densidade.png', dpi=300, bbox_inches='tight')
            plt.close()
        
        # 3. Distribuição dos tempos
        plt.figure(figsize=(10, 6))
        plt.hist(df['execution_time'], bins=20, alpha=0.7, edgecolor='black')
        plt.xlabel('Tempo de Execução (s)')
        plt.ylabel('Frequência')
        plt.title('Distribuição dos Tempos de Execução')
        plt.grid(True, alpha=0.3)
        plt.tight_layout()
        plt.savefig(output_dir / 'distribuicao_tempos.png', dpi=300, bbox_inches='tight')
        plt.close()
        
        # 4. Performance por família
        if 'instance_name' in df.columns:
            # Adicionar família
            def get_family(instance):
                if instance.startswith('C'):
                    return 'C-family'
                elif instance.startswith('DSJC'):
                    return 'DSJC'
                elif instance.startswith('MANN'):
                    return 'MANN'
                elif instance.startswith('brock'):
                    return 'brock'
                elif instance.startswith('gen'):
                    return 'gen'
                elif instance.startswith('hamming'):
                    return 'hamming'
                elif instance.startswith('keller'):
                    return 'keller'
                elif instance.startswith('p_hat'):
                    return 'p_hat'
                else:
                    return 'other'
            
            df['family'] = df['instance_name'].apply(get_family)
            
            # Box plot por família
            plt.figure(figsize=(12, 6))
            families = df['family'].unique()
            family_times = [df[df['family'] == family]['execution_time'].values for family in families]
            
            plt.boxplot(family_times, labels=families)
            plt.xlabel('Família de Grafos')
            plt.ylabel('Tempo de Execução (s)')
            plt.title('Distribuição de Tempos por Família')
            plt.yscale('log')
            plt.xticks(rotation=45)
            plt.grid(True, alpha=0.3)
            plt.tight_layout()
            plt.savefig(output_dir / 'tempos_por_familia.png', dpi=300, bbox_inches='tight')
            plt.close()
    
    def _generate_text_report(self, df: pd.DataFrame, output_dir: Path):
        """Gerar relatório de texto."""
        report_path = output_dir / 'relatorio_apa.txt'
        
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write("RELATÓRIO DE BENCHMARK - ALGORITMO CLISAT\n")
            f.write("Análise e Projeto de Algoritmos - Mestrado\n")
            f.write("=" * 50 + "\n\n")
            
            f.write(f"Data do benchmark: {datetime.now().strftime('%d/%m/%Y %H:%M')}\n")
            f.write(f"Total de instâncias analisadas: {len(df)}\n\n")
            
            f.write("ESTATÍSTICAS GERAIS\n")
            f.write("-" * 20 + "\n")
            f.write(f"Tempo total de execução: {df['execution_time'].sum():.1f}s\n")
            f.write(f"Tempo médio por instância: {df['execution_time'].mean():.1f}s\n")
            f.write(f"Tempo mínimo: {df['execution_time'].min():.1f}s\n")
            f.write(f"Tempo máximo: {df['execution_time'].max():.1f}s\n\n")
            
            # Estatísticas de gap
            gap_df = df[df['gap_percent'].notna()]
            if not gap_df.empty:
                f.write("ANÁLISE DE QUALIDADE\n")
                f.write("-" * 20 + "\n")
                f.write(f"Gap médio: {gap_df['gap_percent'].mean():.1f}%\n")
                f.write(f"Gap mínimo: {gap_df['gap_percent'].min():.1f}%\n")
                f.write(f"Gap máximo: {gap_df['gap_percent'].max():.1f}%\n")
                
                optima_found = (gap_df['gap_percent'] == 0).sum()
                f.write(f"Ótimos encontrados: {optima_found}/{len(gap_df)} ({optima_found/len(gap_df)*100:.1f}%)\n\n")
            
            # Top 5 melhores e piores resultados
            f.write("TOP 5 MELHORES RESULTADOS\n")
            f.write("-" * 30 + "\n")
            best_df = gap_df.nsmallest(5, 'gap_percent') if not gap_df.empty else df.nsmallest(5, 'execution_time')
            for _, row in best_df.iterrows():
                gap_str = f"{row['gap_percent']:.1f}%" if pd.notna(row.get('gap_percent')) else "N/A"
                f.write(f"{row['instance_name']}: gap {gap_str}, tempo {row['execution_time']:.1f}s\n")
            
            f.write("\nTOP 5 PIORES RESULTADOS\n")
            f.write("-" * 30 + "\n")
            worst_df = gap_df.nlargest(5, 'gap_percent') if not gap_df.empty else df.nlargest(5, 'execution_time')
            for _, row in worst_df.iterrows():
                gap_str = f"{row['gap_percent']:.1f}%" if pd.notna(row.get('gap_percent')) else "N/A"
                f.write(f"{row['instance_name']}: gap {gap_str}, tempo {row['execution_time']:.1f}s\n")


def main():
    """Função principal para demonstração."""
    benchmark = APABenchmark()
    
    # Exemplo de teste em instância pequena
    print("=== TESTE INDIVIDUAL ===")
    result = benchmark.run_single_test("C125.9", time_limit=60.0)
    
    if result['status'] == 'SUCCESS':
        print(f"Sucesso! Clique de tamanho {result['found_clique_size']}")
    else:
        print(f"Falha: {result.get('error', result['status'])}")


if __name__ == "__main__":
    main()
