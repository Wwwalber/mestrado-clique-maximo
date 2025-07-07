"""
Gerador de Resultados para Atividade APA

Este módulo gerencia a execução dos algoritmos (exato e heurístico) e 
gera a tabela de resultados no formato solicitado pelo professor.
"""

import json
import csv
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Tuple, Optional
import logging

import networkx as nx
import pandas as pd

from clisat_algortithmb import CliSAT, solve_maximum_clique_clisat
from clique_heuristics import solve_maximum_clique_heuristic
from apa_instance_manager import APAInstanceManager

logger = logging.getLogger(__name__)


class APAResultsManager:
    """
    Gerenciador de resultados para a atividade APA.
    Executa algoritmos exatos e heurísticos e gera relatórios formatados.
    """
    
    def __init__(self, results_dir: str = "benchmark_results"):
        """
        Inicializar gerenciador de resultados.
        
        Args:
            results_dir: Diretório para salvar resultados
        """
        self.results_dir = Path(results_dir)
        self.results_dir.mkdir(exist_ok=True)
        
        self.instance_manager = APAInstanceManager()
        
        # Valores ótimos conhecidos (base DIMACS)
        self.known_optimal = {
            'C125.9': 34, 'C250.9': 44, 'C500.9': 57, 'C1000.9': 68, 'C2000.9': 80,
            'C2000.5': 16, 'C4000.5': 18,
            'DSJC1000_5': 15, 'DSJC500_5': 13,
            'MANN_a27': 126, 'MANN_a45': 345, 'MANN_a81': 1100,
            'brock200_2': 12, 'brock200_4': 17, 'brock400_2': 29, 'brock400_4': 33,
            'brock800_2': 24, 'brock800_4': 26,
            'gen200_p0.9_44': 44, 'gen200_p0.9_55': 55,
            'gen400_p0.9_55': 55, 'gen400_p0.9_65': 65, 'gen400_p0.9_75': 75,
            'hamming10-4': 40, 'hamming8-4': 16,
            'keller4': 11, 'keller5': 27, 'keller6': 59,
            'p_hat300-1': 8, 'p_hat300-2': 25, 'p_hat300-3': 36,
            'p_hat700-1': 11, 'p_hat700-2': 44, 'p_hat700-3': 62,
            'p_hat1500-1': 12, 'p_hat1500-2': 65, 'p_hat1500-3': 94
        }
    
    def run_exact_algorithm(self, graph: nx.Graph, instance_name: str, 
                           time_limit: float = 300.0) -> Dict:
        """
        Executar algoritmo exato (CliSAT).
        
        Args:
            graph: Grafo a processar
            instance_name: Nome da instância
            time_limit: Limite de tempo em segundos
            
        Returns:
            Dicionário com resultados
        """
        logger.info(f"Executando CliSAT em {instance_name}...")
        
        start_time = time.time()
        try:
            # Executar CliSAT
            solver = CliSAT(graph, time_limit=time_limit)
            clique_nodes, clique_size = solver.solve()
            
            execution_time = time.time() - start_time
            success = True
            error_msg = None
            
            # Verificar se é um clique válido
            if clique_nodes:
                subgraph = graph.subgraph(clique_nodes)
                expected_edges = len(clique_nodes) * (len(clique_nodes) - 1) // 2
                actual_edges = len(subgraph.edges())
                is_valid_clique = (actual_edges == expected_edges)
            else:
                is_valid_clique = True  # Clique vazio é válido
            
        except Exception as e:
            logger.error(f"Erro no CliSAT para {instance_name}: {e}")
            clique_nodes = []
            clique_size = 0
            execution_time = time_limit
            success = False
            is_valid_clique = False
            error_msg = str(e)
        
        return {
            'instance_name': instance_name,
            'algorithm': 'CliSAT_Exact',
            'clique_nodes': clique_nodes,
            'clique_size': clique_size,
            'execution_time': execution_time,
            'success': success,
            'is_valid_clique': is_valid_clique,
            'error': error_msg,
            'time_limit_used': time_limit
        }
    
    def run_heuristic_algorithm(self, graph: nx.Graph, instance_name: str,
                              method: str = 'best') -> Dict:
        """
        Executar algoritmo heurístico.
        
        Args:
            graph: Grafo a processar
            instance_name: Nome da instância
            method: Método heurístico a usar
            
        Returns:
            Dicionário com resultados
        """
        logger.info(f"Executando heurística {method} em {instance_name}...")
        
        try:
            # Executar heurística GRASP (substituindo a antiga classe CliqueHeuristics)
            if method == 'best' or method == 'grasp':
                # Usar GRASP como a única heurística de alta qualidade
                clique_nodes, clique_size, execution_time = solve_maximum_clique_heuristic(
                    graph, alpha=0.3, max_iterations=100, time_limit=60.0
                )
                method_used = "grasp"
            else:
                # Para compatibilidade com outros métodos, usar GRASP com parâmetros padrão
                clique_nodes, clique_size, execution_time = solve_maximum_clique_heuristic(graph)
                method_used = method
            
            success = True
            error_msg = None
            
            # Verificar se é um clique válido
            if clique_nodes:
                subgraph = graph.subgraph(clique_nodes)
                expected_edges = len(clique_nodes) * (len(clique_nodes) - 1) // 2
                actual_edges = len(subgraph.edges())
                is_valid_clique = (actual_edges == expected_edges)
            else:
                is_valid_clique = True
            
        except Exception as e:
            logger.error(f"Erro na heurística {method} para {instance_name}: {e}")
            clique_nodes = []
            clique_size = 0
            execution_time = 0.0
            success = False
            is_valid_clique = False
            error_msg = str(e)
            method_used = method
        
        return {
            'instance_name': instance_name,
            'algorithm': f'Heuristic_{method_used}',
            'clique_nodes': clique_nodes,
            'clique_size': clique_size,
            'execution_time': execution_time,
            'success': success,
            'is_valid_clique': is_valid_clique,
            'error': error_msg,
            'heuristic_method': method_used
        }
    
    def run_full_comparison(self, instance_names: List[str] = None,
                           exact_time_limit: float = 300.0,
                           heuristic_method: str = 'best') -> List[Dict]:
        """
        Executar comparação completa entre algoritmo exato e heurística.
        
        Args:
            instance_names: Lista de instâncias (None para todas)
            exact_time_limit: Limite de tempo para algoritmo exato
            heuristic_method: Método heurístico a usar
            
        Returns:
            Lista de resultados
        """
        if instance_names is None:
            instance_names = self.instance_manager.get_all_instance_names()
        
        all_results = []
        
        for instance_name in instance_names:
            logger.info(f"\n=== Processando {instance_name} ===")
            
            try:
                # Carregar grafo
                graph = self.instance_manager.load_graph(instance_name)
                if graph is None:
                    logger.warning(f"Não foi possível carregar {instance_name}")
                    continue
                
                logger.info(f"Grafo carregado: {len(graph.nodes())} nós, {len(graph.edges())} arestas")
                
                # Executar algoritmo exato
                exact_result = self.run_exact_algorithm(graph, instance_name, exact_time_limit)
                all_results.append(exact_result)
                
                # Executar heurística
                heuristic_result = self.run_heuristic_algorithm(graph, instance_name, heuristic_method)
                all_results.append(heuristic_result)
                
                # Log dos resultados
                logger.info(f"Exato: {exact_result['clique_size']} em {exact_result['execution_time']:.2f}s")
                logger.info(f"Heurística: {heuristic_result['clique_size']} em {heuristic_result['execution_time']:.2f}s")
                
            except Exception as e:
                logger.error(f"Erro processando {instance_name}: {e}")
                continue
        
        return all_results
    
    def generate_apa_table(self, results: List[Dict], output_file: str = None) -> str:
        """
        Gerar tabela no formato solicitado pelo professor.
        
        Args:
            results: Lista de resultados
            output_file: Arquivo para salvar (None para apenas retornar string)
            
        Returns:
            String com a tabela formatada
        """
        # Organizar resultados por instância
        results_by_instance = {}
        for result in results:
            instance = result['instance_name']
            if instance not in results_by_instance:
                results_by_instance[instance] = {}
            
            if 'Exact' in result['algorithm']:
                results_by_instance[instance]['exact'] = result
            else:
                results_by_instance[instance]['heuristic'] = result
        
        # Criar tabela
        table_lines = []
        table_lines.append("| Instância | Número de clique ω(G) | Clique máximo | | Clique por heurística | |")
        table_lines.append("| | | Nº Clique máximo | Tempo de execução | Nº Clique por heurística | Tempo de execução |")
        table_lines.append("|-----------|----------------------|---------------|-------------------|------------------------|-------------------|")
        
        for instance_name in sorted(results_by_instance.keys()):
            instance_data = results_by_instance[instance_name]
            
            # Número de clique ótimo conhecido
            omega_g = self.known_optimal.get(instance_name, "?")
            
            # Resultado do algoritmo exato
            if 'exact' in instance_data:
                exact = instance_data['exact']
                exact_size = exact['clique_size'] if exact['success'] else "ERRO"
                exact_time = f"{exact['execution_time']:.2f}s" if exact['success'] else "TIMEOUT"
            else:
                exact_size = "N/A"
                exact_time = "N/A"
            
            # Resultado da heurística
            if 'heuristic' in instance_data:
                heuristic = instance_data['heuristic']
                heur_size = heuristic['clique_size'] if heuristic['success'] else "ERRO"
                heur_time = f"{heuristic['execution_time']:.2f}s" if heuristic['success'] else "ERRO"
            else:
                heur_size = "N/A"
                heur_time = "N/A"
            
            # Adicionar linha à tabela
            table_lines.append(f"| {instance_name:12} | {omega_g:20} | {exact_size:15} | {exact_time:17} | {heur_size:22} | {heur_time:17} |")
        
        table_content = "\n".join(table_lines)
        
        # Salvar arquivo se especificado
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(table_content)
            logger.info(f"Tabela salva em: {output_file}")
        
        return table_content
    
    def generate_detailed_report(self, results: List[Dict], output_file: str = None) -> str:
        """
        Gerar relatório detalhado dos resultados.
        
        Args:
            results: Lista de resultados
            output_file: Arquivo para salvar
            
        Returns:
            String com o relatório
        """
        report_lines = []
        report_lines.append("=" * 80)
        report_lines.append("RELATÓRIO DETALHADO - ATIVIDADE APA")
        report_lines.append("Problema do Clique Máximo")
        report_lines.append(f"Data/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}")
        report_lines.append("=" * 80)
        
        # Estatísticas gerais
        total_instances = len(set(r['instance_name'] for r in results))
        exact_results = [r for r in results if 'Exact' in r['algorithm']]
        heuristic_results = [r for r in results if 'Heuristic' in r['algorithm']]
        
        exact_success = sum(1 for r in exact_results if r['success'])
        heuristic_success = sum(1 for r in heuristic_results if r['success'])
        
        report_lines.append(f"\nESTATÍSTICAS GERAIS:")
        report_lines.append(f"Instâncias testadas: {total_instances}")
        report_lines.append(f"Algoritmo exato - Sucessos: {exact_success}/{len(exact_results)}")
        report_lines.append(f"Heurística - Sucessos: {heuristic_success}/{len(heuristic_results)}")
        
        # Análise de qualidade
        if exact_results and heuristic_results:
            report_lines.append(f"\nANÁLISE DE QUALIDADE:")
            
            # Organizar por instância
            results_by_instance = {}
            for result in results:
                instance = result['instance_name']
                if instance not in results_by_instance:
                    results_by_instance[instance] = {}
                
                if 'Exact' in result['algorithm']:
                    results_by_instance[instance]['exact'] = result
                else:
                    results_by_instance[instance]['heuristic'] = result
            
            gaps = []
            for instance, data in results_by_instance.items():
                if 'exact' in data and 'heuristic' in data:
                    exact_size = data['exact']['clique_size']
                    heur_size = data['heuristic']['clique_size']
                    
                    if exact_size > 0:
                        gap = (exact_size - heur_size) / exact_size * 100
                        gaps.append(gap)
                        
                        optimal_known = self.known_optimal.get(instance, None)
                        if optimal_known:
                            exact_gap = (optimal_known - exact_size) / optimal_known * 100 if optimal_known > 0 else 0
                            heur_gap = (optimal_known - heur_size) / optimal_known * 100 if optimal_known > 0 else 0
                        else:
                            exact_gap = heur_gap = None
                        
                        report_lines.append(f"{instance:15} - Exato: {exact_size:3d}, Heur: {heur_size:3d}, Gap: {gap:5.1f}%")
            
            if gaps:
                avg_gap = sum(gaps) / len(gaps)
                report_lines.append(f"\nGap médio heurística vs exato: {avg_gap:.2f}%")
        
        # Análise temporal
        report_lines.append(f"\nANÁLISE TEMPORAL:")
        
        if exact_results:
            exact_times = [r['execution_time'] for r in exact_results if r['success']]
            if exact_times:
                avg_exact_time = sum(exact_times) / len(exact_times)
                max_exact_time = max(exact_times)
                report_lines.append(f"Algoritmo exato - Tempo médio: {avg_exact_time:.2f}s, Máximo: {max_exact_time:.2f}s")
        
        if heuristic_results:
            heur_times = [r['execution_time'] for r in heuristic_results if r['success']]
            if heur_times:
                avg_heur_time = sum(heur_times) / len(heur_times)
                max_heur_time = max(heur_times)
                report_lines.append(f"Heurística - Tempo médio: {avg_heur_time:.2f}s, Máximo: {max_heur_time:.2f}s")
        
        # Instâncias mais desafiadoras
        if exact_results:
            exact_by_time = sorted([r for r in exact_results if r['success']], 
                                 key=lambda x: x['execution_time'], reverse=True)
            report_lines.append(f"\nINSTÂNCIAS MAIS DESAFIADORAS (por tempo):")
            for i, result in enumerate(exact_by_time[:5]):
                report_lines.append(f"{i+1}. {result['instance_name']:15} - {result['execution_time']:6.2f}s")
        
        report_content = "\n".join(report_lines)
        
        # Salvar arquivo se especificado
        if output_file:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(report_content)
            logger.info(f"Relatório salvo em: {output_file}")
        
        return report_content
    
    def save_results_json(self, results: List[Dict], filename: str = None) -> str:
        """
        Salvar resultados em formato JSON.
        
        Args:
            results: Lista de resultados
            filename: Nome do arquivo (None para gerar automaticamente)
            
        Returns:
            Caminho do arquivo salvo
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"apa_results_{timestamp}.json"
        
        filepath = self.results_dir / filename
        
        # Converter para formato serializável
        serializable_results = []
        for result in results:
            serializable_result = result.copy()
            # Converter nós do clique para lista se necessário
            if 'clique_nodes' in serializable_result:
                serializable_result['clique_nodes'] = list(serializable_result['clique_nodes'])
            serializable_results.append(serializable_result)
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump({
                'metadata': {
                    'generated_at': datetime.now().isoformat(),
                    'total_instances': len(set(r['instance_name'] for r in results)),
                    'total_results': len(results)
                },
                'results': serializable_results
            }, f, indent=2, ensure_ascii=False)
        
        logger.info(f"Resultados JSON salvos em: {filepath}")
        return str(filepath)
    
    def export_to_csv(self, results: List[Dict], filename: str = None) -> str:
        """
        Exportar resultados para CSV.
        
        Args:
            results: Lista de resultados
            filename: Nome do arquivo CSV
            
        Returns:
            Caminho do arquivo salvo
        """
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"apa_results_{timestamp}.csv"
        
        filepath = self.results_dir / filename
        
        # Preparar dados para CSV
        csv_data = []
        for result in results:
            csv_row = {
                'instance_name': result['instance_name'],
                'algorithm': result['algorithm'],
                'clique_size': result['clique_size'],
                'execution_time': result['execution_time'],
                'success': result['success'],
                'is_valid_clique': result['is_valid_clique'],
                'known_optimal': self.known_optimal.get(result['instance_name'], None),
                'gap_to_optimal': None
            }
            
            # Calcular gap para o ótimo conhecido
            if csv_row['known_optimal'] and csv_row['clique_size'] > 0:
                gap = (csv_row['known_optimal'] - csv_row['clique_size']) / csv_row['known_optimal'] * 100
                csv_row['gap_to_optimal'] = round(gap, 2)
            
            csv_data.append(csv_row)
        
        # Salvar CSV
        df = pd.DataFrame(csv_data)
        df.to_csv(filepath, index=False, encoding='utf-8')
        
        logger.info(f"Resultados CSV salvos em: {filepath}")
        return str(filepath)


# Exemplo de uso
if __name__ == "__main__":
    # Configurar logging
    logging.basicConfig(level=logging.INFO)
    
    # Criar gerenciador
    manager = APAResultsManager()
    
    # Testar com algumas instâncias pequenas
    test_instances = ['C125.9', 'brock200_2', 'keller4']
    
    print("Executando comparação em instâncias de teste...")
    results = manager.run_full_comparison(
        instance_names=test_instances,
        exact_time_limit=120.0,
        heuristic_method='best'
    )
    
    # Gerar tabela
    print("\n" + "="*80)
    print("TABELA DE RESULTADOS")
    print("="*80)
    table = manager.generate_apa_table(results)
    print(table)
    
    # Salvar resultados
    json_file = manager.save_results_json(results)
    csv_file = manager.export_to_csv(results)
    
    print(f"\nArquivos salvos:")
    print(f"- JSON: {json_file}")
    print(f"- CSV: {csv_file}")
