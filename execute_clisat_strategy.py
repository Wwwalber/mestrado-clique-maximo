#!/usr/bin/env python3
"""
Estratégia de Execução do CliSAT para Todas as Instâncias

Este script implementa uma estratégia inteligente para executar o algoritmo CliSAT
em todas as instâncias DIMACS, organizando por grupos de dificuldade e implementando
checkpoints para evitar reprocessamento.

ESTRATÉGIAS IMPLEMENTADAS:
1. Execução por grupos de dificuldade (pequeno, médio, grande, crítico)
2. Sistema de checkpoint para retomar execuções interrompidas
3. Timeouts adaptativos baseados no tamanho das instâncias
4. Monitoramento em tempo real e logs detalhados
5. Geração automática da tabela de resultados
6. Backup automático dos resultados

Autor: Walber
Data: Julho 2025
"""

import os
import sys
import time
import json
import pandas as pd
import logging
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from datetime import datetime
import argparse

# Importar módulos do projeto
sys.path.append(str(Path(__file__).parent / "src"))
from apa_instance_manager import APAInstanceManager
from clisat_algortithmb import CliSAT, solve_maximum_clique_clisat
from dimacs_loader import DIMACSLoader
import networkx as nx

# Configurar logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('clisat_execution.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class CliSATExecutionStrategy:
    """
    Classe principal para execução estratégica do CliSAT em todas as instâncias.
    """
    
    def __init__(self, base_dir: str = None):
        """
        Inicializar estratégia de execução.
        
        Args:
            base_dir: Diretório base do projeto
        """
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent
        self.results_dir = self.base_dir / "execution_results"
        self.checkpoint_file = self.results_dir / "execution_checkpoint.json"
        self.final_results_file = self.results_dir / "clisat_final_results.csv"
        
        # Criar diretórios necessários
        self.results_dir.mkdir(exist_ok=True)
        
        # Inicializar gerenciadores
        self.instance_manager = APAInstanceManager()
        
        # Definir grupos de instâncias por dificuldade
        self.define_instance_groups()
        
        # Carregar checkpoint se existir
        self.execution_state = self.load_checkpoint()
        
        logger.info(f"Estratégia inicializada. Diretório: {self.base_dir}")

    def define_instance_groups(self):
        """
        Definir grupos de instâncias organizados por dificuldade computacional.
        """
        self.instance_groups = {
            # Grupo 1: Instâncias pequenas e rápidas (< 300 nós)
            'small_fast': {
                'instances': [
                    'C125.9', 'brock200_2', 'brock200_4', 'gen200_p0.9_44', 
                    'gen200_p0.9_55', 'keller4', 'hamming8-4'
                ],
                'time_limit': 300,  # 5 minutos
                'expected_time': '2-10 minutos por instância',
                'description': 'Instâncias pequenas, execução rápida'
            },
            
            # Grupo 2: Instâncias médias (300-800 nós)
            'medium': {
                'instances': [
                    'C250.9', 'brock400_2', 'brock400_4', 'gen400_p0.9_55',
                    'gen400_p0.9_65', 'gen400_p0.9_75', 'MANN_a27', 'DSJC500_5',
                    'p_hat300-1', 'p_hat300-2', 'p_hat300-3', 'keller5'
                ],
                'time_limit': 900,  # 15 minutos
                'expected_time': '5-20 minutos por instância',
                'description': 'Instâncias médias, tempo moderado'
            },
            
            # Grupo 3: Instâncias grandes (800-1500 nós)
            'large': {
                'instances': [
                    'C500.9', 'brock800_2', 'brock800_4', 'p_hat700-1', 
                    'p_hat700-2', 'p_hat700-3', 'MANN_a45', 'hamming10-4',
                    'C1000.9', 'DSJC1000_5', 'p_hat1500-1', 'p_hat1500-2'
                ],
                'time_limit': 1800,  # 30 minutos
                'expected_time': '10-45 minutos por instância',
                'description': 'Instâncias grandes, tempo considerável'
            },
            
            # Grupo 4: Instâncias críticas (> 1500 nós ou conhecidamente difíceis)
            'critical': {
                'instances': [
                    'C2000.9', 'C2000.5', 'p_hat1500-3', 'keller6', 
                    'MANN_a81', 'C4000.5'
                ],
                'time_limit': 3600,  # 1 hora
                'expected_time': '30-60 minutos por instância',
                'description': 'Instâncias críticas, tempo longo'
            }
        }
        
        logger.info("Grupos de instâncias definidos:")
        for group_name, group_info in self.instance_groups.items():
            logger.info(f"  {group_name}: {len(group_info['instances'])} instâncias")

    def load_checkpoint(self) -> Dict:
        """
        Carregar estado da execução a partir do checkpoint.
        
        Returns:
            Dicionário com estado da execução
        """
        if self.checkpoint_file.exists():
            try:
                with open(self.checkpoint_file, 'r') as f:
                    state = json.load(f)
                logger.info(f"Checkpoint carregado: {len(state.get('completed', []))} instâncias concluídas")
                return state
            except Exception as e:
                logger.warning(f"Erro ao carregar checkpoint: {e}")
        
        return {
            'completed': [],
            'failed': [],
            'current_group': None,
            'start_time': None,
            'results': []
        }

    def save_checkpoint(self):
        """
        Salvar estado atual da execução.
        """
        try:
            with open(self.checkpoint_file, 'w') as f:
                json.dump(self.execution_state, f, indent=2, default=str)
            logger.debug("Checkpoint salvo")
        except Exception as e:
            logger.error(f"Erro ao salvar checkpoint: {e}")

    def run_single_instance(self, instance_name: str, time_limit: int) -> Dict:
        """
        Executar CliSAT em uma única instância.
        
        Args:
            instance_name: Nome da instância
            time_limit: Limite de tempo em segundos
            
        Returns:
            Dicionário com resultados da execução
        """
        logger.info(f"Iniciando execução: {instance_name} (limit: {time_limit}s)")
        
        result = {
            'instance': instance_name,
            'time_limit': time_limit,
            'start_time': datetime.now().isoformat(),
            'status': 'RUNNING'
        }
        
        try:
            # Carregar instância
            graph = self.instance_manager.load_instance(instance_name)
            if graph is None:
                raise Exception(f"Não foi possível carregar a instância {instance_name}")
            
            # Obter informações da instância
            result['nodes'] = len(graph.nodes())
            result['edges'] = len(graph.edges())
            result['density'] = nx.density(graph)
            
            logger.info(f"  Grafo: {result['nodes']} nós, {result['edges']} arestas")
            
            # Executar CliSAT
            start_time = time.time()
            
            clique_nodes, clique_size = solve_maximum_clique_clisat(
                graph,
                time_limit=float(time_limit),
                monitor_mode='log'  # Log para acompanhar progresso
            )
            
            execution_time = time.time() - start_time
            
            # Validar resultado
            is_valid = True
            if clique_nodes and len(clique_nodes) > 1:
                clique_subgraph = graph.subgraph(clique_nodes)
                expected_edges = len(clique_nodes) * (len(clique_nodes) - 1) // 2
                actual_edges = len(clique_subgraph.edges())
                is_valid = (actual_edges == expected_edges)
            
            # Atualizar resultado
            result.update({
                'status': 'SUCCESS',
                'clique_size': clique_size,
                'execution_time': execution_time,
                'is_valid_clique': is_valid,
                'clique_nodes': clique_nodes if len(clique_nodes) <= 100 else f"[{len(clique_nodes)} nodes]",
                'end_time': datetime.now().isoformat()
            })
            
            # Verificar se é ótimo (se conhecido)
            known_optimal = self.instance_manager.get_known_clique_size(instance_name)
            if known_optimal:
                result['known_optimal'] = known_optimal
                result['is_optimal'] = (clique_size == known_optimal)
                if known_optimal > 0:
                    result['gap_percent'] = ((known_optimal - clique_size) / known_optimal) * 100
                else:
                    result['gap_percent'] = 0.0
            
            logger.info(f"  ✓ Sucesso: clique {clique_size} em {execution_time:.2f}s")
            if known_optimal:
                logger.info(f"    Ótimo conhecido: {known_optimal} (gap: {result.get('gap_percent', 0):.1f}%)")
                
        except Exception as e:
            execution_time = time.time() - start_time if 'start_time' in locals() else time_limit
            result.update({
                'status': 'ERROR',
                'error': str(e),
                'execution_time': execution_time,
                'clique_size': 0,
                'is_valid_clique': False,
                'end_time': datetime.now().isoformat()
            })
            logger.error(f"  ✗ Erro: {e}")
        
        return result

    def run_group(self, group_name: str, resume: bool = True) -> List[Dict]:
        """
        Executar todas as instâncias de um grupo.
        
        Args:
            group_name: Nome do grupo a executar
            resume: Se deve retomar execuções anteriores
            
        Returns:
            Lista de resultados
        """
        if group_name not in self.instance_groups:
            raise ValueError(f"Grupo '{group_name}' não encontrado")
        
        group_info = self.instance_groups[group_name]
        instances = group_info['instances']
        time_limit = group_info['time_limit']
        
        logger.info(f"\n{'='*60}")
        logger.info(f"EXECUTANDO GRUPO: {group_name.upper()}")
        logger.info(f"{'='*60}")
        logger.info(f"Descrição: {group_info['description']}")
        logger.info(f"Instâncias: {len(instances)}")
        logger.info(f"Tempo limite: {time_limit}s ({time_limit//60} minutos)")
        logger.info(f"Tempo estimado: {group_info['expected_time']}")
        
        # Filtrar instâncias já processadas se resumindo
        if resume:
            completed = set(self.execution_state.get('completed', []))
            remaining_instances = [inst for inst in instances if inst not in completed]
            if len(remaining_instances) < len(instances):
                logger.info(f"Resumindo: {len(instances) - len(remaining_instances)} já concluídas")
                instances = remaining_instances
        
        if not instances:
            logger.info("Todas as instâncias do grupo já foram processadas.")
            return []
        
        logger.info(f"Processando {len(instances)} instâncias...")
        
        results = []
        for i, instance_name in enumerate(instances, 1):
            logger.info(f"\n[{i}/{len(instances)}] Processando {instance_name}")
            
            # Executar instância
            result = self.run_single_instance(instance_name, time_limit)
            results.append(result)
            
            # Atualizar estado
            if result['status'] == 'SUCCESS':
                self.execution_state['completed'].append(instance_name)
            else:
                self.execution_state['failed'].append(instance_name)
            
            self.execution_state['results'].append(result)
            self.execution_state['current_group'] = group_name
            
            # Salvar checkpoint
            self.save_checkpoint()
            
            # Mostrar progresso
            successful = len([r for r in results if r['status'] == 'SUCCESS'])
            logger.info(f"Progresso do grupo: {i}/{len(instances)} ({successful} sucessos)")
        
        # Resumo do grupo
        successful = len([r for r in results if r['status'] == 'SUCCESS'])
        total_time = sum(r.get('execution_time', 0) for r in results)
        
        logger.info(f"\n{'='*40}")
        logger.info(f"RESUMO DO GRUPO {group_name.upper()}")
        logger.info(f"{'='*40}")
        logger.info(f"Instâncias processadas: {len(results)}")
        logger.info(f"Sucessos: {successful}/{len(results)} ({successful/len(results)*100:.1f}%)")
        logger.info(f"Tempo total: {total_time:.2f}s ({total_time/60:.1f} minutos)")
        logger.info(f"Tempo médio: {total_time/len(results):.2f}s por instância")
        
        return results

    def run_all_groups(self, groups: List[str] = None, resume: bool = True) -> pd.DataFrame:
        """
        Executar todos os grupos de instâncias.
        
        Args:
            groups: Lista de grupos a executar (None = todos)
            resume: Se deve retomar execuções anteriores
            
        Returns:
            DataFrame com todos os resultados
        """
        if groups is None:
            groups = list(self.instance_groups.keys())
        
        if self.execution_state['start_time'] is None:
            self.execution_state['start_time'] = datetime.now().isoformat()
        
        logger.info(f"\n{'='*70}")
        logger.info(f"EXECUÇÃO ESTRATÉGICA DO CLISAT")
        logger.info(f"{'='*70}")
        logger.info(f"Grupos a executar: {', '.join(groups)}")
        logger.info(f"Modo de retomada: {'Ativado' if resume else 'Desativado'}")
        
        total_instances = sum(len(self.instance_groups[g]['instances']) for g in groups)
        logger.info(f"Total de instâncias: {total_instances}")
        
        # Estimar tempo total
        total_time_estimate = sum(
            len(self.instance_groups[g]['instances']) * self.instance_groups[g]['time_limit'] 
            for g in groups
        )
        logger.info(f"Tempo máximo estimado: {total_time_estimate/3600:.1f} horas")
        
        start_time = time.time()
        all_results = []
        
        try:
            for group_name in groups:
                group_results = self.run_group(group_name, resume=resume)
                all_results.extend(group_results)
                
                # Backup parcial após cada grupo
                if group_results:
                    self.save_partial_results(all_results, f"backup_after_{group_name}")
        
        except KeyboardInterrupt:
            logger.info("\n⏹️  Execução interrompida pelo usuário")
            logger.info("O checkpoint foi salvo. Use --resume para continuar.")
        
        except Exception as e:
            logger.error(f"Erro durante execução: {e}")
        
        finally:
            total_execution_time = time.time() - start_time
            
            # Gerar resultados finais
            if all_results:
                df_results = self.generate_final_results(all_results)
                self.save_final_results(df_results)
                
                # Estatísticas finais
                successful = len([r for r in all_results if r['status'] == 'SUCCESS'])
                
                logger.info(f"\n{'='*70}")
                logger.info(f"EXECUÇÃO CONCLUÍDA")
                logger.info(f"{'='*70}")
                logger.info(f"Instâncias processadas: {len(all_results)}")
                logger.info(f"Sucessos: {successful}/{len(all_results)} ({successful/len(all_results)*100:.1f}%)")
                logger.info(f"Tempo total de execução: {total_execution_time/3600:.2f} horas")
                logger.info(f"Resultados salvos em: {self.final_results_file}")
                
                return df_results
        
        return pd.DataFrame()

    def generate_final_results(self, results: List[Dict]) -> pd.DataFrame:
        """
        Gerar DataFrame final com resultados formatados.
        
        Args:
            results: Lista de resultados das execuções
            
        Returns:
            DataFrame formatado para a tabela final
        """
        formatted_results = []
        
        for result in results:
            if result['status'] == 'SUCCESS':
                row = {
                    'Instance': result['instance'],
                    'Nodes': result.get('nodes', 0),
                    'Edges': result.get('edges', 0),
                    'Clique_Size': result.get('clique_size', 0),
                    'Execution_Time': round(result.get('execution_time', 0), 2),
                    'Is_Valid': result.get('is_valid_clique', False),
                    'Known_Optimal': result.get('known_optimal', 'N/A'),
                    'Is_Optimal': result.get('is_optimal', 'N/A'),
                    'Gap_Percent': round(result.get('gap_percent', 0), 2) if result.get('gap_percent') is not None else 'N/A',
                    'Status': 'SUCCESS'
                }
            else:
                row = {
                    'Instance': result['instance'],
                    'Nodes': result.get('nodes', 0),
                    'Edges': result.get('edges', 0),
                    'Clique_Size': 0,
                    'Execution_Time': round(result.get('execution_time', 0), 2),
                    'Is_Valid': False,
                    'Known_Optimal': 'N/A',
                    'Is_Optimal': False,
                    'Gap_Percent': 'N/A',
                    'Status': 'ERROR'
                }
            
            formatted_results.append(row)
        
        df = pd.DataFrame(formatted_results)
        df = df.sort_values(['Nodes', 'Instance'])
        
        return df

    def save_partial_results(self, results: List[Dict], suffix: str):
        """
        Salvar resultados parciais como backup.
        
        Args:
            results: Lista de resultados
            suffix: Sufixo para o nome do arquivo
        """
        try:
            backup_file = self.results_dir / f"partial_results_{suffix}.json"
            with open(backup_file, 'w') as f:
                json.dump(results, f, indent=2, default=str)
            logger.debug(f"Backup salvo: {backup_file}")
        except Exception as e:
            logger.warning(f"Erro ao salvar backup: {e}")

    def save_final_results(self, df: pd.DataFrame):
        """
        Salvar resultados finais em CSV e gerar tabela formatada.
        
        Args:
            df: DataFrame com resultados
        """
        try:
            # Salvar CSV
            df.to_csv(self.final_results_file, index=False)
            
            # Gerar tabela formatada para visualização
            table_file = self.results_dir / "formatted_results_table.txt"
            with open(table_file, 'w') as f:
                f.write("RESULTADOS FINAIS - ALGORITMO CLISAT\n")
                f.write("="*80 + "\n\n")
                f.write(df.to_string(index=False))
                f.write(f"\n\n")
                
                # Estatísticas resumidas
                successful = len(df[df['Status'] == 'SUCCESS'])
                optimal = len(df[df['Is_Optimal'] == True])
                
                f.write("ESTATÍSTICAS RESUMIDAS:\n")
                f.write("-"*40 + "\n")
                f.write(f"Total de instâncias: {len(df)}\n")
                f.write(f"Execuções bem-sucedidas: {successful}\n")
                f.write(f"Soluções ótimas encontradas: {optimal}\n")
                f.write(f"Taxa de sucesso: {successful/len(df)*100:.1f}%\n")
                if successful > 0:
                    f.write(f"Taxa de otimalidade: {optimal/successful*100:.1f}%\n")
                
                avg_time = df[df['Status'] == 'SUCCESS']['Execution_Time'].mean()
                f.write(f"Tempo médio de execução: {avg_time:.2f}s\n")
            
            logger.info(f"Tabela formatada salva em: {table_file}")
            
        except Exception as e:
            logger.error(f"Erro ao salvar resultados finais: {e}")

    def print_strategy_summary(self):
        """
        Imprimir resumo da estratégia de execução.
        """
        print("\n" + "="*70)
        print("ESTRATÉGIA DE EXECUÇÃO DO CLISAT")
        print("="*70)
        print()
        
        total_instances = 0
        total_max_time = 0
        
        for group_name, group_info in self.instance_groups.items():
            instances = group_info['instances']
            time_limit = group_info['time_limit']
            max_group_time = len(instances) * time_limit
            
            total_instances += len(instances)
            total_max_time += max_group_time
            
            print(f"Grupo {group_name.upper()}:")
            print(f"  • {len(instances)} instâncias")
            print(f"  • Limite: {time_limit}s ({time_limit//60} min) por instância")
            print(f"  • Tempo máximo do grupo: {max_group_time//3600:.1f}h")
            print(f"  • Descrição: {group_info['description']}")
            print()
        
        print(f"RESUMO TOTAL:")
        print(f"  • Total de instâncias: {total_instances}")
        print(f"  • Tempo máximo estimado: {total_max_time//3600:.1f} horas")
        print(f"  • Arquivos de resultado: {self.results_dir}")
        print()
        print("CARACTERÍSTICAS DA ESTRATÉGIA:")
        print("  ✓ Execução por grupos de dificuldade")
        print("  ✓ Sistema de checkpoint para retomada")
        print("  ✓ Timeouts adaptativos por tamanho")
        print("  ✓ Backup automático dos resultados")
        print("  ✓ Logs detalhados de monitoramento")
        print("  ✓ Validação automática dos cliques")
        print("  ✓ Comparação com ótimos conhecidos")
        print()


def main():
    """
    Função principal com interface de linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Estratégia de Execução do CliSAT para Todas as Instâncias",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Mostrar resumo da estratégia
  python execute_clisat_strategy.py --summary

  # Executar apenas instâncias pequenas
  python execute_clisat_strategy.py --groups small_fast

  # Executar todos os grupos
  python execute_clisat_strategy.py --all

  # Retomar execução interrompida
  python execute_clisat_strategy.py --resume

  # Executar grupos específicos
  python execute_clisat_strategy.py --groups small_fast medium
        """
    )
    
    parser.add_argument('--groups', nargs='+', 
                       choices=['small_fast', 'medium', 'large', 'critical'],
                       help='Grupos específicos para executar')
    
    parser.add_argument('--all', action='store_true',
                       help='Executar todos os grupos')
    
    parser.add_argument('--resume', action='store_true',
                       help='Retomar execução a partir do checkpoint')
    
    parser.add_argument('--no-resume', action='store_true',
                       help='Iniciar execução do zero (ignorar checkpoint)')
    
    parser.add_argument('--summary', action='store_true',
                       help='Mostrar apenas resumo da estratégia')
    
    parser.add_argument('--base-dir', type=str,
                       help='Diretório base do projeto')
    
    args = parser.parse_args()
    
    # Criar estratégia
    strategy = CliSATExecutionStrategy(base_dir=args.base_dir)
    
    if args.summary:
        strategy.print_strategy_summary()
        return
    
    if not (args.groups or args.all or args.resume):
        strategy.print_strategy_summary()
        print("\nUse --help para ver as opções de execução.")
        return
    
    # Determinar grupos a executar
    if args.all:
        groups_to_run = list(strategy.instance_groups.keys())
    elif args.groups:
        groups_to_run = args.groups
    elif args.resume:
        groups_to_run = list(strategy.instance_groups.keys())
    else:
        groups_to_run = []
    
    # Determinar modo de retomada
    resume_mode = True
    if args.no_resume:
        resume_mode = False
        # Limpar checkpoint
        if strategy.checkpoint_file.exists():
            strategy.checkpoint_file.unlink()
            strategy.execution_state = strategy.load_checkpoint()
    
    # Executar estratégia
    if groups_to_run:
        try:
            print(f"\nIniciando execução dos grupos: {', '.join(groups_to_run)}")
            print(f"Modo de retomada: {'Ativado' if resume_mode else 'Desativado'}")
            print("\nPressione Ctrl+C para interromper (checkpoint será salvo)")
            
            results_df = strategy.run_all_groups(groups=groups_to_run, resume=resume_mode)
            
            if not results_df.empty:
                print(f"\n✅ Execução concluída!")
                print(f"Resultados disponíveis em: {strategy.final_results_file}")
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Execução interrompida. Use --resume para continuar.")
        except Exception as e:
            print(f"\n❌ Erro durante execução: {e}")
            logger.exception("Erro detalhado:")


if __name__ == "__main__":
    main()
