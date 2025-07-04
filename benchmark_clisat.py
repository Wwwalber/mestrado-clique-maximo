"""
Sistema de Benchmark para o Algoritmo CliSAT com Grafos DIMACS

Este módulo executa testes sistemáticos do algoritmo CliSAT usando
a base de dados DIMACS para problemas de clique máximo.
"""

import time
import json
import csv
import os
from datetime import datetime
from typing import Dict, List, Optional, Tuple
import networkx as nx
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from clisat_algorithm import CliSATSolver
from dimacs_loader import DIMACSLoader
import logging

logger = logging.getLogger(__name__)


class CliSATBenchmark:
    """Classe para executar benchmarks do CliSAT com grafos DIMACS."""
    
    def __init__(self, results_dir: str = "benchmark_results"):
        """
        Inicializar o sistema de benchmark.
        
        Args:
            results_dir: Diretório para salvar resultados
        """
        self.results_dir = results_dir
        self.dimacs_loader = DIMACSLoader()
        
        # Criar diretório de resultados
        os.makedirs(results_dir, exist_ok=True)
        
        # Configurar logging
        log_file = os.path.join(results_dir, f"benchmark_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log")
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.INFO)
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    def run_single_test(self, graph_name: str, time_limit: float = 300.0, 
                       algorithm_params: Optional[Dict] = None) -> Dict:
        """
        Executar um teste único do CliSAT em um grafo.
        
        Args:
            graph_name: Nome do grafo DIMACS
            time_limit: Limite de tempo em segundos
            algorithm_params: Parâmetros específicos do algoritmo
            
        Returns:
            Dicionário com resultados do teste
        """
        logger.info(f"Iniciando teste com {graph_name}")
        
        # Carregar grafo
        graph = self.dimacs_loader.load_graph(graph_name)
        if graph is None:
            return {
                'graph_name': graph_name,
                'status': 'ERROR',
                'error': 'Não foi possível carregar o grafo'
            }
        
        # Informações do grafo
        graph_info = self.dimacs_loader.get_graph_info(graph_name)
        num_vertices = len(graph.nodes())
        num_edges = len(graph.edges())
        density = nx.density(graph)
        known_clique_size = graph_info['known_clique'] if graph_info else None
        
        # Configurar solver
        solver = CliSATSolver(graph, time_limit=time_limit)
        
        # Executar algoritmo
        start_time = time.time()
        try:
            clique = solver.solve()
            end_time = time.time()
            execution_time = end_time - start_time
            
            # Verificar se é realmente um clique
            is_valid_clique = self._verify_clique(graph, clique)
            
            # Resultado
            result = {
                'graph_name': graph_name,
                'status': 'COMPLETED',
                'num_vertices': num_vertices,
                'num_edges': num_edges,
                'density': density,
                'known_clique_size': known_clique_size,
                'found_clique_size': len(clique),
                'clique': clique,
                'is_valid_clique': is_valid_clique,
                'execution_time': execution_time,
                'time_limit': time_limit,
                'is_optimal': len(clique) == known_clique_size if known_clique_size else None,
                'gap': (known_clique_size - len(clique)) / known_clique_size * 100 if known_clique_size else None,
                'stats': solver.stats,
                'timestamp': datetime.now().isoformat()
            }
            
            if known_clique_size:
                if len(clique) == known_clique_size:
                    logger.info(f"✓ {graph_name}: Solução ótima encontrada (clique = {len(clique)})")
                elif len(clique) > known_clique_size:
                    logger.warning(f"⚠ {graph_name}: Clique maior que o conhecido! ({len(clique)} > {known_clique_size})")
                else:
                    logger.info(f"• {graph_name}: Clique subótimo (encontrado = {len(clique)}, conhecido = {known_clique_size})")
            else:
                logger.info(f"• {graph_name}: Clique encontrado = {len(clique)} (ótimo desconhecido)")
            
        except Exception as e:
            end_time = time.time()
            execution_time = end_time - start_time
            
            result = {
                'graph_name': graph_name,
                'status': 'ERROR',
                'num_vertices': num_vertices,
                'num_edges': num_edges,
                'density': density,
                'known_clique_size': known_clique_size,
                'found_clique_size': 0,
                'clique': [],
                'is_valid_clique': False,
                'execution_time': execution_time,
                'time_limit': time_limit,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
            logger.error(f"✗ {graph_name}: Erro durante execução - {str(e)}")
        
        return result
    
    def _verify_clique(self, graph: nx.Graph, clique: List) -> bool:
        """
        Verificar se um conjunto de vértices forma um clique válido.
        
        Args:
            graph: Grafo NetworkX
            clique: Lista de vértices do clique
            
        Returns:
            True se é um clique válido
        """
        if len(clique) <= 1:
            return True
        
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                if not graph.has_edge(clique[i], clique[j]):
                    return False
        return True
    
    def run_benchmark_suite(self, max_graph_size: Optional[int] = 300, 
                           time_limit_per_graph: float = 300.0,
                           custom_graphs: Optional[List[str]] = None) -> List[Dict]:
        """
        Executar uma suíte completa de benchmarks.
        
        Args:
            max_graph_size: Tamanho máximo dos grafos a testar
            time_limit_per_graph: Limite de tempo por grafo
            custom_graphs: Lista específica de grafos para testar
            
        Returns:
            Lista com resultados de todos os testes
        """
        # Determinar grafos para teste
        if custom_graphs:
            test_graphs = custom_graphs
        else:
            test_graphs = self.dimacs_loader.get_test_suite(max_graph_size)
        
        logger.info(f"Iniciando benchmark com {len(test_graphs)} grafos")
        logger.info(f"Limite de tempo por grafo: {time_limit_per_graph}s")
        
        # Baixar grafos necessários
        logger.info("Verificando e baixando grafos...")
        successful_downloads = self.dimacs_loader.download_test_suite(max_graph_size)
        
        # Filtrar apenas grafos disponíveis
        available_graphs = [g for g in test_graphs if g in successful_downloads or 
                           os.path.exists(os.path.join(self.dimacs_loader.data_dir, f"{g}.clq"))]
        
        logger.info(f"Executando testes em {len(available_graphs)} grafos disponíveis")
        
        results = []
        total_start_time = time.time()
        
        for i, graph_name in enumerate(available_graphs, 1):
            logger.info(f"\n[{i}/{len(available_graphs)}] Testando {graph_name}...")
            
            result = self.run_single_test(graph_name, time_limit_per_graph)
            results.append(result)
            
            # Salvar resultado intermediário
            self._save_intermediate_result(result)
            
            # Mostrar progresso
            elapsed = time.time() - total_start_time
            avg_time = elapsed / i
            estimated_remaining = avg_time * (len(available_graphs) - i)
            logger.info(f"Progresso: {i}/{len(available_graphs)} ({i/len(available_graphs)*100:.1f}%)")
            logger.info(f"Tempo estimado restante: {estimated_remaining/60:.1f} minutos")
        
        # Salvar resultados finais
        self._save_results(results)
        
        total_time = time.time() - total_start_time
        logger.info(f"\nBenchmark concluído em {total_time/60:.1f} minutos")
        
        return results
    
    def _save_intermediate_result(self, result: Dict):
        """Salvar resultado intermediário."""
        filename = os.path.join(self.results_dir, f"result_{result['graph_name']}.json")
        with open(filename, 'w') as f:
            json.dump(result, f, indent=2, default=str)
    
    def _save_results(self, results: List[Dict]):
        """Salvar todos os resultados em diferentes formatos."""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        
        # JSON completo
        json_file = os.path.join(self.results_dir, f"benchmark_results_{timestamp}.json")
        with open(json_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        # CSV resumido
        csv_file = os.path.join(self.results_dir, f"benchmark_summary_{timestamp}.csv")
        self._save_csv_summary(results, csv_file)
        
        # Relatório em texto
        report_file = os.path.join(self.results_dir, f"benchmark_report_{timestamp}.txt")
        self._generate_text_report(results, report_file)
        
        logger.info(f"Resultados salvos em:")
        logger.info(f"  JSON: {json_file}")
        logger.info(f"  CSV: {csv_file}")
        logger.info(f"  Relatório: {report_file}")
    
    def _save_csv_summary(self, results: List[Dict], filename: str):
        """Salvar resumo em CSV."""
        with open(filename, 'w', newline='') as csvfile:
            fieldnames = ['graph_name', 'status', 'num_vertices', 'num_edges', 'density',
                         'known_clique_size', 'found_clique_size', 'is_optimal', 'gap',
                         'execution_time', 'is_valid_clique']
            writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
            
            writer.writeheader()
            for result in results:
                row = {field: result.get(field, '') for field in fieldnames}
                writer.writerow(row)
    
    def _generate_text_report(self, results: List[Dict], filename: str):
        """Gerar relatório detalhado em texto."""
        with open(filename, 'w') as f:
            f.write("RELATÓRIO DE BENCHMARK - ALGORITMO CLISAT\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Total de grafos testados: {len(results)}\n\n")
            
            # Estatísticas gerais
            completed = [r for r in results if r['status'] == 'COMPLETED']
            errors = [r for r in results if r['status'] == 'ERROR']
            optimal = [r for r in completed if r.get('is_optimal', False)]
            
            f.write("ESTATÍSTICAS GERAIS:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Testes concluídos: {len(completed)}\n")
            f.write(f"Testes com erro: {len(errors)}\n")
            f.write(f"Soluções ótimas: {len(optimal)}\n")
            if completed:
                f.write(f"Taxa de sucesso: {len(completed)/len(results)*100:.1f}%\n")
                f.write(f"Taxa de otimalidade: {len(optimal)/len(completed)*100:.1f}%\n")
            f.write("\n")
            
            # Resultados por grafo
            f.write("RESULTADOS DETALHADOS:\n")
            f.write("-" * 25 + "\n")
            for result in results:
                f.write(f"\nGrafo: {result['graph_name']}\n")
                f.write(f"  Status: {result['status']}\n")
                if result['status'] == 'COMPLETED':
                    f.write(f"  Vértices: {result['num_vertices']}\n")
                    f.write(f"  Arestas: {result['num_edges']}\n")
                    f.write(f"  Densidade: {result['density']:.3f}\n")
                    f.write(f"  Clique conhecido: {result.get('known_clique_size', 'N/A')}\n")
                    f.write(f"  Clique encontrado: {result['found_clique_size']}\n")
                    f.write(f"  Tempo execução: {result['execution_time']:.2f}s\n")
                    f.write(f"  Clique válido: {result['is_valid_clique']}\n")
                    if result.get('is_optimal') is not None:
                        f.write(f"  Ótimo: {result['is_optimal']}\n")
                    if result.get('gap') is not None:
                        f.write(f"  Gap: {result['gap']:.1f}%\n")
                elif result['status'] == 'ERROR':
                    f.write(f"  Erro: {result.get('error', 'Erro desconhecido')}\n")
    
    def generate_plots(self, results: List[Dict]):
        """Gerar gráficos de análise dos resultados."""
        if not results:
            return
        
        completed = [r for r in results if r['status'] == 'COMPLETED']
        if not completed:
            return
        
        # Configurar estilo
        plt.style.use('seaborn-v0_8')
        fig, axes = plt.subplots(2, 2, figsize=(15, 12))
        
        # 1. Tamanho do grafo vs Tempo de execução
        sizes = [r['num_vertices'] for r in completed]
        times = [r['execution_time'] for r in completed]
        
        axes[0, 0].scatter(sizes, times, alpha=0.7)
        axes[0, 0].set_xlabel('Número de Vértices')
        axes[0, 0].set_ylabel('Tempo de Execução (s)')
        axes[0, 0].set_title('Tamanho do Grafo vs Tempo de Execução')
        axes[0, 0].set_yscale('log')
        
        # 2. Densidade vs Tamanho do clique encontrado
        densities = [r['density'] for r in completed]
        clique_sizes = [r['found_clique_size'] for r in completed]
        
        axes[0, 1].scatter(densities, clique_sizes, alpha=0.7)
        axes[0, 1].set_xlabel('Densidade do Grafo')
        axes[0, 1].set_ylabel('Tamanho do Clique Encontrado')
        axes[0, 1].set_title('Densidade vs Tamanho do Clique')
        
        # 3. Histograma de gaps (para grafos com solução conhecida)
        gaps = [r['gap'] for r in completed if r.get('gap') is not None and r['gap'] >= 0]
        if gaps:
            axes[1, 0].hist(gaps, bins=20, alpha=0.7, edgecolor='black')
            axes[1, 0].set_xlabel('Gap (%)')
            axes[1, 0].set_ylabel('Frequência')
            axes[1, 0].set_title('Distribuição dos Gaps')
        
        # 4. Taxa de sucesso por faixa de tamanho
        size_ranges = [(0, 100), (100, 200), (200, 400), (400, 1000), (1000, float('inf'))]
        success_rates = []
        range_labels = []
        
        for min_size, max_size in size_ranges:
            range_results = [r for r in completed if min_size <= r['num_vertices'] < max_size]
            if range_results:
                optimal_count = len([r for r in range_results if r.get('is_optimal', False)])
                success_rate = optimal_count / len(range_results) * 100
                success_rates.append(success_rate)
                range_labels.append(f"{min_size}-{max_size if max_size != float('inf') else '∞'}")
        
        if success_rates:
            axes[1, 1].bar(range_labels, success_rates, alpha=0.7)
            axes[1, 1].set_xlabel('Faixa de Tamanho (vértices)')
            axes[1, 1].set_ylabel('Taxa de Otimalidade (%)')
            axes[1, 1].set_title('Taxa de Otimalidade por Tamanho')
            axes[1, 1].tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        
        # Salvar gráfico
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        plot_file = os.path.join(self.results_dir, f"benchmark_plots_{timestamp}.png")
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.show()
        
        logger.info(f"Gráficos salvos em: {plot_file}")


def main():
    """Função principal para executar benchmarks."""
    # Configurar logging
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
    
    # Criar benchmark
    benchmark = CliSATBenchmark()
    
    # Executar testes com grafos pequenos (até 200 vértices)
    print("Executando benchmark com grafos pequenos...")
    results = benchmark.run_benchmark_suite(
        max_graph_size=200,
        time_limit_per_graph=180.0  # 3 minutos por grafo
    )
    
    # Gerar gráficos
    benchmark.generate_plots(results)
    
    # Resumo final
    completed = [r for r in results if r['status'] == 'COMPLETED']
    optimal = [r for r in completed if r.get('is_optimal', False)]
    
    print(f"\n{'='*50}")
    print(f"RESUMO FINAL")
    print(f"{'='*50}")
    print(f"Total de grafos testados: {len(results)}")
    print(f"Testes concluídos: {len(completed)}")
    print(f"Soluções ótimas encontradas: {len(optimal)}")
    if completed:
        print(f"Taxa de sucesso: {len(completed)/len(results)*100:.1f}%")
        print(f"Taxa de otimalidade: {len(optimal)/len(completed)*100:.1f}%")
    print(f"{'='*50}")


if __name__ == "__main__":
    main()
