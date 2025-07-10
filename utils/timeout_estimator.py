"""
Estimador de Tempo para Casos de Timeout

Este módulo fornece métodos simples para estimar o tempo necessário
quando os algoritmos excedem o tempo limite, baseado nos dados
já coletados durante a execução.

Autor: Walber
Data: Julho 2025
"""

import time
import math
from typing import Dict, Any, Optional, Tuple


class TimeoutEstimator:
    """
    Estimador de tempo baseado em dados de execução parcial.
    
    Este estimador usa informações que já são coletadas pelos algoritmos
    existentes para calcular estimativas de tempo necessário em casos de timeout.
    """
    
    @staticmethod
    def estimate_clisat_time(stats: Dict[str, Any], 
                           current_time: float, 
                           graph_size: int,
                           current_bound: int) -> Dict[str, Any]:
        """
        Estimar tempo necessário para CliSAT baseado no progresso atual.
        
        DADOS NECESSÁRIOS (já coletados pelo CliSAT):
        - stats['nodes_explored']: número de nós explorados na árvore de busca
        - current_time: tempo já decorrido
        - graph_size: número de vértices do grafo
        - current_bound: melhor clique encontrado até agora
        
        COMO PEGAR OS DADOS:
        1. stats['nodes_explored'] - já existe no algoritmo
        2. current_time - calculado como: time.time() - start_time
        3. graph_size - self.n (número de vértices)
        4. current_bound - self.lb (tamanho do melhor clique)
        
        CÁLCULO DA ESTIMATIVA:
        - Espaço de busca restante ≈ 2^(graph_size - current_bound)
        - Taxa de exploração = nodes_explored / current_time
        - Estimativa = espaço_restante / taxa_exploração
        
        Returns:
            Dict com estimativa e dados do cálculo
        """
        nodes_explored = stats.get('nodes_explored', 0)
        
        if nodes_explored == 0 or current_time == 0:
            return {
                'estimated_total_time': float('inf'),
                'estimated_remaining_time': float('inf'),
                'current_time': current_time,
                'exploration_rate': 0,
                'nodes_explored': nodes_explored,
                'calculation_method': 'Dados insuficientes para estimativa',
                'explanation': 'Dados insuficientes para estimativa'
            }
        
        # Taxa de exploração (nós por segundo)
        exploration_rate = nodes_explored / current_time
        
        # Estimativa do espaço de busca restante
        # Heurística: considera que ainda precisamos explorar aproximadamente
        # uma fração do espaço baseada no tamanho do grafo e bound atual
        remaining_space_factor = max(1, graph_size - current_bound)
        estimated_remaining_nodes = nodes_explored * remaining_space_factor
        
        # Estimativa de tempo restante
        estimated_remaining_time = estimated_remaining_nodes / exploration_rate
        
        # Tempo total estimado
        estimated_total_time = current_time + estimated_remaining_time
        
        return {
            'estimated_total_time': estimated_total_time,
            'estimated_remaining_time': estimated_remaining_time,
            'current_time': current_time,
            'exploration_rate': exploration_rate,
            'nodes_explored': nodes_explored,
            'calculation_method': 'Baseado na taxa de exploração de nós da árvore de busca',
            'explanation': f'Taxa atual: {exploration_rate:.2f} nós/s. Espaço restante estimado: {estimated_remaining_nodes:,} nós'
        }
    
    @staticmethod
    def estimate_grasp_time(iteration: int,
                          current_time: float,
                          max_iterations: int,
                          best_clique_size: int,
                          improvement_history: list) -> Dict[str, Any]:
        """
        Estimar tempo necessário para GRASP baseado na convergência.
        
        DADOS NECESSÁRIOS (já coletados pelo GRASP):
        - iteration: iteração atual
        - current_time: tempo já decorrido
        - max_iterations: número máximo de iterações configurado
        - best_clique_size: melhor clique encontrado
        - improvement_history: histórico de melhorias
        
        COMO PEGAR OS DADOS:
        1. iteration - contador de iterações do loop principal
        2. current_time - calculado como: time.time() - start_time
        3. max_iterations - self.params.max_iterations
        4. best_clique_size - self.best_clique_size
        5. improvement_history - lista com tamanhos encontrados por iteração
        
        CÁLCULO DA ESTIMATIVA:
        - Taxa de progresso = iteration / current_time
        - Iterações restantes = max_iterations - iteration
        - Estimativa = iterações_restantes / taxa_progresso
        
        Returns:
            Dict com estimativa e dados do cálculo
        """
        if iteration == 0 or current_time == 0:
            return {
                'estimated_total_time': float('inf'),
                'estimated_remaining_time': float('inf'),
                'current_time': current_time,
                'iteration_rate': 0,
                'remaining_iterations': max_iterations,
                'progress_percentage': 0,
                'calculation_method': 'Dados insuficientes para estimativa',
                'explanation': 'Dados insuficientes para estimativa'
            }
        
        # Taxa de progresso (iterações por segundo)
        iteration_rate = iteration / current_time
        
        # Iterações restantes
        remaining_iterations = max_iterations - iteration
        
        # Estimativa de tempo restante
        estimated_remaining_time = remaining_iterations / iteration_rate
        
        # Tempo total estimado
        estimated_total_time = current_time + estimated_remaining_time
        
        # Análise de convergência
        convergence_analysis = ""
        if len(improvement_history) > 10:
            recent_improvements = sum(1 for i in range(len(improvement_history)-10, len(improvement_history))
                                   if improvement_history[i] > improvement_history[i-1])
            convergence_analysis = f"Melhorias recentes: {recent_improvements}/10 iterações"
        
        return {
            'estimated_total_time': estimated_total_time,
            'estimated_remaining_time': estimated_remaining_time,
            'current_time': current_time,
            'iteration_rate': iteration_rate,
            'remaining_iterations': remaining_iterations,
            'progress_percentage': (iteration / max_iterations) * 100,
            'calculation_method': 'Baseado na taxa de progresso das iterações',
            'explanation': f'Taxa atual: {iteration_rate:.2f} iter/s. Restam {remaining_iterations:,} iterações. {convergence_analysis}'
        }
    
    @staticmethod
    def format_time_estimate(estimate_data: Dict[str, Any]) -> str:
        """
        Formatar estimativa de tempo de forma legível.
        
        Args:
            estimate_data: Dados da estimativa retornados pelos métodos acima
            
        Returns:
            String formatada com a estimativa
        """
        if estimate_data.get('estimated_total_time') == float('inf'):
            return "⚠️ Não foi possível estimar o tempo (dados insuficientes)"
        
        total_time = estimate_data['estimated_total_time']
        remaining_time = estimate_data['estimated_remaining_time']
        
        # Converter para formato legível
        def format_duration(seconds):
            if seconds < 60:
                return f"{seconds:.1f}s"
            elif seconds < 3600:
                minutes = seconds / 60
                return f"{minutes:.1f}min"
            elif seconds < 86400:
                hours = seconds / 3600
                return f"{hours:.1f}h"
            else:
                days = seconds / 86400
                return f"{days:.1f}d"
        
        result = f"📊 ESTIMATIVA DE TEMPO:\n"
        result += f"   ⏱️  Tempo restante estimado: {format_duration(remaining_time)}\n"
        result += f"   🎯 Tempo total estimado: {format_duration(total_time)}\n"
        result += f"   📈 Método: {estimate_data['calculation_method']}\n"
        result += f"   💡 Detalhes: {estimate_data['explanation']}\n"
        
        return result


# Exemplo de uso simples para adicionar ao código existente
def add_timeout_estimation_to_clisat():
    """
    EXEMPLO: Como adicionar estimativa de tempo ao CliSAT existente.
    
    Adicionar essas linhas quando detectar timeout no método solve():
    """
    exemplo_codigo = '''
    # No método solve() do CliSAT, quando detectar timeout:
    if self._time_exceeded():
        # Calcular estimativa
        current_time = time.time() - self.start_time
        estimate = TimeoutEstimator.estimate_clisat_time(
            stats=self.stats,
            current_time=current_time,
            graph_size=self.n,
            current_bound=self.lb
        )
        
        # Mostrar estimativa
        print(TimeoutEstimator.format_time_estimate(estimate))
        
        # Salvar dados para relatório
        self.timeout_estimate = estimate
        
        break
    '''
    return exemplo_codigo


def add_timeout_estimation_to_grasp():
    """
    EXEMPLO: Como adicionar estimativa de tempo ao GRASP existente.
    
    Adicionar essas linhas quando detectar timeout no método solve():
    """
    exemplo_codigo = '''
    # No método solve() do GRASP, quando detectar timeout:
    if time.time() - start_time >= self.params.time_limit:
        # Calcular estimativa
        current_time = time.time() - start_time
        estimate = TimeoutEstimator.estimate_grasp_time(
            iteration=iteration,
            current_time=current_time,
            max_iterations=self.params.max_iterations,
            best_clique_size=self.best_clique_size,
            improvement_history=self.stats.clique_sizes_history
        )
        
        # Mostrar estimativa
        print(TimeoutEstimator.format_time_estimate(estimate))
        
        # Salvar dados para relatório
        self.timeout_estimate = estimate
        
        break
    '''
    return exemplo_codigo
