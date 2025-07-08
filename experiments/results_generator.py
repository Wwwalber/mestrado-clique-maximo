"""
Módulo para Geração de Resultados da Atividade APA

Este módulo executa tanto o algoritmo exato (CliSAT) quanto a heurística gulosa
nas instâncias DIMACS especificadas e gera a tabela de resultados no formato
solicitado pelo professor.

ESTRUTURA DA ATIVIDADE:
1. Algoritmo Exato: CliSAT (SAT-based exact algorithm)
2. Heurística: Gulosa baseada em grau (Greedy degree-based heuristic)

FORMATO DA TABELA DE RESULTADOS:
- Instance: Nome da instância DIMACS
- Nodes: Número de vértices
- Edges: Número de arestas  
- Exact_Size: Tamanho do clique encontrado pelo algoritmo exato
- Exact_Time: Tempo de execução do algoritmo exato (segundos)
- Heuristic_Size: Tamanho do clique encontrado pela heurística
- Heuristic_Time: Tempo de execução da heurística (segundos)
- Quality: Razão heuristic_size/exact_size (qualidade da heurística)
"""

import pandas as pd
import networkx as nx
import time
import os
from typing import Dict, List, Tuple, Optional
import logging

import sys
from pathlib import Path

# Adicionar diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from algorithms.clisat_exact import solve_maximum_clique_clisat
from algorithms.algorithm_interface import solve_maximum_clique_heuristic
from data.instance_manager import APAInstanceManager

logger = logging.getLogger(__name__)


class APAResultsGenerator:
    """
    Classe para executar experimentos e gerar resultados da atividade APA.
    """
    
    def __init__(self, data_dir: str = "dimacs_data", results_dir: str = "benchmark_results"):
        """
        Inicializar gerador de resultados.
        
        Args:
            data_dir: Diretório onde estão os arquivos DIMACS
            results_dir: Diretório para salvar os resultados
        """
        self.data_dir = data_dir
        self.results_dir = results_dir
        self.instance_manager = APAInstanceManager(data_dir)
        
        # Criar diretório de resultados se não existir
        os.makedirs(results_dir, exist_ok=True)
        
        # Configurar logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(f'{results_dir}/apa_execution.log'),
                logging.StreamHandler()
            ]
        )
    
    def run_single_instance(self, instance_name: str, time_limit_exact: int = 1800, 
                          time_limit_heuristic: int = 60) -> Dict:
        """
        Executar algoritmos em uma única instância.
        
        Args:
            instance_name: Nome da instância (ex: 'C125.9')
            time_limit_exact: Tempo limite para algoritmo exato (segundos)
            time_limit_heuristic: Tempo limite para heurística (segundos)
            
        Returns:
            Dicionário com resultados da execução
        """
        logger.info(f"Processando instância: {instance_name}")
        
        # Carregar grafo
        try:
            graph = self.instance_manager.load_instance(instance_name)
            if graph is None:
                logger.error(f"Não foi possível carregar a instância {instance_name}")
                return None
                
        except Exception as e:
            logger.error(f"Erro ao carregar {instance_name}: {e}")
            return None
        
        result = {
            'Instance': instance_name,
            'Nodes': len(graph.nodes()),
            'Edges': len(graph.edges()),
        }
        
        logger.info(f"  Grafo: {result['Nodes']} vértices, {result['Edges']} arestas")
        
        # Executar algoritmo exato (CliSAT)
        logger.info("  Executando algoritmo exato (CliSAT)...")
        try:
            start_time = time.time()
            exact_clique, exact_size = solve_maximum_clique_clisat(graph, time_limit=time_limit_exact)
            exact_time = time.time() - start_time
            
            result['Exact_Size'] = exact_size
            result['Exact_Time'] = round(exact_time, 3)
            result['Exact_Status'] = 'COMPLETED'
            
            logger.info(f"    Clique exato: tamanho {exact_size}, tempo {exact_time:.3f}s")
            
        except Exception as e:
            logger.error(f"    Erro no algoritmo exato: {e}")
            result['Exact_Size'] = 0
            result['Exact_Time'] = time_limit_exact
            result['Exact_Status'] = 'ERROR'
        
        # Executar heurística gulosa
        logger.info("  Executando heurística gulosa...")
        try:
            start_time = time.time()
            heur_clique, heur_size, heur_time = solve_maximum_clique_heuristic(graph)
            
            # Limitar tempo se necessário
            if heur_time > time_limit_heuristic:
                logger.warning(f"    Heurística excedeu tempo limite: {heur_time:.3f}s")
                result['Heuristic_Status'] = 'TIMEOUT'
            else:
                result['Heuristic_Status'] = 'COMPLETED'
            
            result['Heuristic_Size'] = heur_size
            result['Heuristic_Time'] = round(heur_time, 6)
            
            logger.info(f"    Clique heurístico: tamanho {heur_size}, tempo {heur_time:.6f}s")
            
        except Exception as e:
            logger.error(f"    Erro na heurística: {e}")
            result['Heuristic_Size'] = 0
            result['Heuristic_Time'] = 0
            result['Heuristic_Status'] = 'ERROR'
        
        # Calcular qualidade da heurística
        if result['Exact_Size'] > 0:
            result['Quality'] = round(result['Heuristic_Size'] / result['Exact_Size'], 3)
        else:
            result['Quality'] = 0.0
        
        # Calcular speedup (quantas vezes mais rápido é a heurística)
        if result['Heuristic_Time'] > 0:
            result['Speedup'] = round(result['Exact_Time'] / result['Heuristic_Time'], 1)
        else:
            result['Speedup'] = float('inf')
        
        logger.info(f"    Qualidade: {result['Quality']:.3f}, Speedup: {result['Speedup']}x")
        logger.info(f"  Instância {instance_name} concluída")
        
        return result
    
    def run_all_instances(self, instances: List[str] = None, 
                         time_limit_exact: int = 1800,
                         time_limit_heuristic: int = 60) -> pd.DataFrame:
        """
        Executar algoritmos em todas as instâncias especificadas.
        
        Args:
            instances: Lista de instâncias para testar (None = todas da atividade)
            time_limit_exact: Tempo limite para algoritmo exato
            time_limit_heuristic: Tempo limite para heurística
            
        Returns:
            DataFrame com todos os resultados
        """
        if instances is None:
            instances = self.instance_manager.get_apa_instance_list()
        
        logger.info(f"Iniciando experimentos com {len(instances)} instâncias")
        logger.info(f"Tempo limite exato: {time_limit_exact}s, heurística: {time_limit_heuristic}s")
        
        results = []
        completed = 0
        total = len(instances)
        
        for instance_name in instances:
            logger.info(f"\n[{completed + 1}/{total}] Processando {instance_name}")
            
            result = self.run_single_instance(
                instance_name, 
                time_limit_exact=time_limit_exact,
                time_limit_heuristic=time_limit_heuristic
            )
            
            if result:
                results.append(result)
                completed += 1
                
                # Salvar resultados parciais a cada 5 instâncias
                if completed % 5 == 0:
                    partial_df = pd.DataFrame(results)
                    partial_df.to_csv(f'{self.results_dir}/partial_results_{completed}.csv', index=False)
                    logger.info(f"Resultados parciais salvos: {completed} instâncias")
        
        # Criar DataFrame final
        results_df = pd.DataFrame(results)
        
        logger.info(f"\nExperimentos concluídos: {completed}/{total} instâncias")
        
        return results_df
    
    def generate_summary_statistics(self, results_df: pd.DataFrame) -> Dict:
        """
        Gerar estatísticas resumidas dos resultados.
        
        Args:
            results_df: DataFrame com os resultados
            
        Returns:
            Dicionário com estatísticas
        """
        stats = {}
        
        # Estatísticas gerais
        stats['total_instances'] = len(results_df)
        stats['exact_completed'] = sum(results_df['Exact_Status'] == 'COMPLETED')
        stats['heuristic_completed'] = sum(results_df['Heuristic_Status'] == 'COMPLETED')
        
        # Estatísticas de tempo
        exact_times = results_df[results_df['Exact_Status'] == 'COMPLETED']['Exact_Time']
        heuristic_times = results_df[results_df['Heuristic_Status'] == 'COMPLETED']['Heuristic_Time']
        
        if not exact_times.empty:
            stats['exact_time_mean'] = round(exact_times.mean(), 3)
            stats['exact_time_median'] = round(exact_times.median(), 3)
            stats['exact_time_max'] = round(exact_times.max(), 3)
        
        if not heuristic_times.empty:
            stats['heuristic_time_mean'] = round(heuristic_times.mean(), 6)
            stats['heuristic_time_median'] = round(heuristic_times.median(), 6)
            stats['heuristic_time_max'] = round(heuristic_times.max(), 6)
        
        # Estatísticas de qualidade
        qualities = results_df[results_df['Quality'] > 0]['Quality']
        if not qualities.empty:
            stats['quality_mean'] = round(qualities.mean(), 3)
            stats['quality_median'] = round(qualities.median(), 3)
            stats['quality_min'] = round(qualities.min(), 3)
            stats['quality_max'] = round(qualities.max(), 3)
            stats['perfect_solutions'] = sum(qualities == 1.0)
        
        # Estatísticas de speedup
        speedups = results_df[results_df['Speedup'] != float('inf')]['Speedup']
        if not speedups.empty:
            stats['speedup_mean'] = round(speedups.mean(), 1)
            stats['speedup_median'] = round(speedups.median(), 1)
            stats['speedup_max'] = round(speedups.max(), 1)
        
        return stats
    
    def save_results(self, results_df: pd.DataFrame, filename: str = "apa_results.csv"):
        """
        Salvar resultados em arquivo CSV formatado para o professor.
        
        Args:
            results_df: DataFrame com os resultados
            filename: Nome do arquivo para salvar
        """
        filepath = os.path.join(self.results_dir, filename)
        
        # Ordenar por número de vértices para melhor visualização
        results_df_sorted = results_df.sort_values('Nodes')
        
        # Salvar CSV principal
        results_df_sorted.to_csv(filepath, index=False)
        logger.info(f"Resultados salvos em: {filepath}")
        
        # Gerar arquivo formatado para apresentação
        presentation_cols = [
            'Instance', 'Nodes', 'Edges', 'Exact_Size', 'Exact_Time', 
            'Heuristic_Size', 'Heuristic_Time', 'Quality'
        ]
        
        if all(col in results_df_sorted.columns for col in presentation_cols):
            presentation_df = results_df_sorted[presentation_cols].copy()
            
            # Formatar para apresentação
            presentation_df['Exact_Time'] = presentation_df['Exact_Time'].apply(lambda x: f"{x:.3f}")
            presentation_df['Heuristic_Time'] = presentation_df['Heuristic_Time'].apply(lambda x: f"{x:.6f}")
            presentation_df['Quality'] = presentation_df['Quality'].apply(lambda x: f"{x:.3f}")
            
            presentation_file = filepath.replace('.csv', '_presentation.csv')
            presentation_df.to_csv(presentation_file, index=False)
            logger.info(f"Tabela para apresentação salva em: {presentation_file}")
        
        # Gerar estatísticas resumidas
        stats = self.generate_summary_statistics(results_df_sorted)
        
        stats_file = filepath.replace('.csv', '_summary.txt')
        with open(stats_file, 'w') as f:
            f.write("=== RESUMO DOS RESULTADOS DA ATIVIDADE APA ===\n\n")
            f.write("ALGORITMOS TESTADOS:\n")
            f.write("1. Algoritmo Exato: CliSAT (SAT-based)\n")
            f.write("2. Heurística: Gulosa baseada em grau\n\n")
            
            f.write("ESTATÍSTICAS GERAIS:\n")
            f.write(f"Total de instâncias: {stats.get('total_instances', 0)}\n")
            f.write(f"Algoritmo exato completou: {stats.get('exact_completed', 0)}\n")
            f.write(f"Heurística completou: {stats.get('heuristic_completed', 0)}\n\n")
            
            if 'exact_time_mean' in stats:
                f.write("TEMPO DE EXECUÇÃO (Algoritmo Exato):\n")
                f.write(f"Média: {stats['exact_time_mean']}s\n")
                f.write(f"Mediana: {stats['exact_time_median']}s\n")
                f.write(f"Máximo: {stats['exact_time_max']}s\n\n")
            
            if 'heuristic_time_mean' in stats:
                f.write("TEMPO DE EXECUÇÃO (Heurística):\n")
                f.write(f"Média: {stats['heuristic_time_mean']}s\n")
                f.write(f"Mediana: {stats['heuristic_time_median']}s\n")
                f.write(f"Máximo: {stats['heuristic_time_max']}s\n\n")
            
            if 'quality_mean' in stats:
                f.write("QUALIDADE DA HEURÍSTICA:\n")
                f.write(f"Qualidade média: {stats['quality_mean']}\n")
                f.write(f"Qualidade mediana: {stats['quality_median']}\n")
                f.write(f"Melhor qualidade: {stats['quality_max']}\n")
                f.write(f"Pior qualidade: {stats['quality_min']}\n")
                f.write(f"Soluções ótimas encontradas: {stats.get('perfect_solutions', 0)}\n\n")
            
            if 'speedup_mean' in stats:
                f.write("SPEEDUP (Heurística vs Exato):\n")
                f.write(f"Speedup médio: {stats['speedup_mean']}x\n")
                f.write(f"Speedup mediano: {stats['speedup_median']}x\n")
                f.write(f"Speedup máximo: {stats['speedup_max']}x\n")
        
        logger.info(f"Resumo estatístico salvo em: {stats_file}")


# Função principal para executar os experimentos
def run_apa_experiments(instances: List[str] = None, 
                       time_limit_exact: int = 1800,
                       time_limit_heuristic: int = 60,
                       save_file: str = "apa_results.csv") -> pd.DataFrame:
    """
    Função principal para executar todos os experimentos da atividade APA.
    
    Args:
        instances: Lista de instâncias para testar (None = todas)
        time_limit_exact: Tempo limite para algoritmo exato (segundos)
        time_limit_heuristic: Tempo limite para heurística (segundos)
        save_file: Nome do arquivo para salvar os resultados
        
    Returns:
        DataFrame com os resultados
    """
    generator = APAResultsGenerator()
    
    # Executar experimentos
    results_df = generator.run_all_instances(
        instances=instances,
        time_limit_exact=time_limit_exact,
        time_limit_heuristic=time_limit_heuristic
    )
    
    # Salvar resultados
    generator.save_results(results_df, save_file)
    
    return results_df


if __name__ == "__main__":
    # Executar experimentos em algumas instâncias menores para teste
    test_instances = ['C125.9', 'brock200_2', 'gen200_p0.9_44', 'p_hat300-1']
    
    print("=== EXECUTANDO EXPERIMENTOS DE TESTE ===")
    print(f"Instâncias de teste: {test_instances}")
    print("Tempo limite exato: 1800s, heurística: 60s")
    
    results = run_apa_experiments(
        instances=test_instances,
        time_limit_exact=1800,
        time_limit_heuristic=60,
        save_file="test_results.csv"
    )
    
    print(f"\nResultados:")
    print(results.to_string(index=False))
