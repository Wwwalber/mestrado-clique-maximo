"""
Implementação da Heurística GRASP para o Problema do Clique Máximo

Este módulo implementa o algoritmo GRASP (Greedy Randomized Adaptive Search Procedure)
seguindo a estrutura clássica da metaheurística para o problema do clique máximo.

ESTRUTURA DO GRASP:
1. Fase de Construção: Constrói uma solução usando critério guloso randomizado
2. Fase de Busca Local: Melhora a solução através de operadores de vizinhança
3. Critério de Parada: Número de iterações, tempo limite ou estagnação

REFERÊNCIAS:
- Feo, T.A., Resende, M.G.C. (1995). Greedy Randomized Adaptive Search Procedures
- Pardalos, P.M., Xue, J. (1994). The maximum clique problem
- Ribeiro, C.C., Hansen, P. (2002). Essays and Surveys in Metaheuristics

Autor: Walber
Data: Julho 2025
"""

import networkx as nx
import random
import time
import logging
from typing import List, Set, Tuple, Optional, Dict
import numpy as np
from dataclasses import dataclass

logger = logging.getLogger(__name__)


@dataclass
class GRASPParameters:
    """Parâmetros de configuração do GRASP."""
    alpha: float = 0.3              # Parâmetro de aleatoriedade (0=guloso, 1=aleatório)
    max_iterations: int = 1000       # Número máximo de iterações
    time_limit: float = 300.0        # Limite de tempo em segundos
    max_no_improvement: int = 100    # Máximo de iterações sem melhoria
    local_search_intensity: int = 3  # Intensidade da busca local
    seed: Optional[int] = None       # Semente para reprodutibilidade
    verbose: bool = True             # Imprimir progresso


@dataclass
class GRASPStatistics:
    """Estatísticas de execução do GRASP."""
    total_iterations: int = 0
    construction_time: float = 0.0
    local_search_time: float = 0.0
    total_time: float = 0.0
    best_iteration: int = 0
    improvements_found: int = 0
    clique_sizes_history: List[int] = None
    
    def __post_init__(self):
        if self.clique_sizes_history is None:
            self.clique_sizes_history = []


class GRASPMaximumClique:
    """
    Implementação do algoritmo GRASP para o problema do clique máximo.
    
    O GRASP é uma metaheurística que combina:
    1. Construção gulosa randomizada
    2. Busca local intensiva
    3. Reinicialização com diversificação
    """
    
    def __init__(self, graph: nx.Graph, params: GRASPParameters = None):
        """
        Inicializar o algoritmo GRASP.
        
        Args:
            graph: Grafo NetworkX
            params: Parâmetros de configuração do GRASP
        """
        self.graph = graph
        self.params = params or GRASPParameters()
        self.stats = GRASPStatistics()
        
        # Configurar semente aleatória
        if self.params.seed is not None:
            random.seed(self.params.seed)
            np.random.seed(self.params.seed)
        
        # Melhor solução encontrada
        self.best_clique = []
        self.best_clique_size = 0
        
        # Pré-computar informações do grafo
        self.nodes = list(self.graph.nodes())
        self.n_nodes = len(self.nodes)
        self.adjacency_dict = {node: set(self.graph.neighbors(node)) for node in self.nodes}
        
        logger.info(f"GRASP inicializado: {self.n_nodes} nós, α={self.params.alpha}")

    def solve(self) -> Tuple[List[int], int, float]:
        """
        Executar o algoritmo GRASP principal.
        
        Returns:
            Tupla (clique, tamanho, tempo_execução)
        """
        start_time = time.time()
        
        if self.params.verbose:
            print("\n🚀 INICIANDO GRASP PARA CLIQUE MÁXIMO")
            print("="*50)
            print(f"📊 Grafo: {self.n_nodes} vértices, {len(self.graph.edges())} arestas")
            print(f"⚙️  Parâmetros: α={self.params.alpha}, max_iter={self.params.max_iterations}")
            print(f"⏱️  Limite de tempo: {self.params.time_limit}s")
            print("="*50)
        
        # Variáveis de controle
        iteration = 0
        last_improvement = 0
        
        try:
            while self._should_continue(iteration, start_time, last_improvement):
                iteration += 1
                
                # Fase 1: Construção Gulosa Randomizada
                construction_start = time.time()
                current_clique = self._greedy_randomized_construction()
                construction_time = time.time() - construction_start
                self.stats.construction_time += construction_time
                
                # Fase 2: Busca Local
                local_search_start = time.time()
                improved_clique = self._local_search(current_clique)
                local_search_time = time.time() - local_search_start
                self.stats.local_search_time += local_search_time
                
                # Atualizar melhor solução
                if len(improved_clique) > self.best_clique_size:
                    self.best_clique = improved_clique.copy()
                    self.best_clique_size = len(improved_clique)
                    self.stats.best_iteration = iteration
                    self.stats.improvements_found += 1
                    last_improvement = iteration
                    
                    if self.params.verbose and iteration % 10 == 0:
                        elapsed = time.time() - start_time
                        print(f"🎯 Iteração {iteration}: Novo melhor clique = {self.best_clique_size} "
                              f"(tempo: {elapsed:.1f}s)")
                
                # Registrar estatísticas
                self.stats.clique_sizes_history.append(len(improved_clique))
                
                # Log periódico
                if self.params.verbose and iteration % 100 == 0:
                    elapsed = time.time() - start_time
                    print(f"📈 Progresso: Iteração {iteration}/{self.params.max_iterations}, "
                          f"Melhor: {self.best_clique_size}, Tempo: {elapsed:.1f}s")
        
        except KeyboardInterrupt:
            print("\n⏹️  GRASP interrompido pelo usuário")
        
        # Finalizar estatísticas
        self.stats.total_iterations = iteration
        self.stats.total_time = time.time() - start_time
        
        if self.params.verbose:
            self._print_final_results()
        
        return self.best_clique, self.best_clique_size, self.stats.total_time

    def _should_continue(self, iteration: int, start_time: float, last_improvement: int) -> bool:
        """
        Verificar critérios de parada do GRASP.
        
        Args:
            iteration: Iteração atual
            start_time: Tempo de início
            last_improvement: Última iteração com melhoria
            
        Returns:
            True se deve continuar, False caso contrário
        """
        # Limite de iterações
        if iteration >= self.params.max_iterations:
            return False
        
        # Limite de tempo
        if time.time() - start_time >= self.params.time_limit:
            return False
        
        # Estagnação (sem melhoria por muito tempo)
        if iteration - last_improvement >= self.params.max_no_improvement:
            return False
        
        return True

    def _greedy_randomized_construction(self) -> List[int]:
        """
        Fase de Construção Gulosa Randomizada do GRASP.
        
        Constrói um clique usando uma Lista de Candidatos Restrita (RCL)
        baseada no grau dos vértices candidatos.
        
        Returns:
            Lista de vértices do clique construído
        """
        clique = []
        candidates = set(self.nodes)
        
        while candidates:
            # Calcular candidatos válidos (que mantêm a propriedade de clique)
            valid_candidates = []
            if not clique:
                # Primeiro vértice: todos são válidos
                valid_candidates = list(candidates)
            else:
                # Vértices que são adjacentes a todos no clique atual
                for candidate in candidates:
                    if all(candidate in self.adjacency_dict[v] for v in clique):
                        valid_candidates.append(candidate)
            
            if not valid_candidates:
                break
            
            # Construir RCL baseada no grau dos candidatos
            rcl = self._build_restricted_candidate_list(valid_candidates, clique)
            
            if not rcl:
                break
            
            # Selecionar aleatoriamente da RCL
            selected = random.choice(rcl)
            
            # Adicionar ao clique e atualizar candidatos
            clique.append(selected)
            candidates.remove(selected)
            
            # Atualizar candidatos: manter apenas os adjacentes ao vértice selecionado
            candidates &= self.adjacency_dict[selected]
        
        return clique

    def _build_restricted_candidate_list(self, candidates: List[int], current_clique: List[int]) -> List[int]:
        """
        Construir Lista de Candidatos Restrita (RCL) para o GRASP.
        
        A RCL contém os candidatos com melhor valor da função gulosa,
        controlado pelo parâmetro α.
        
        Args:
            candidates: Lista de candidatos válidos
            current_clique: Clique atual em construção
            
        Returns:
            Lista de candidatos na RCL
        """
        if not candidates:
            return []
        
        # Função gulosa: grau do vértice entre os candidatos
        candidate_degrees = []
        for candidate in candidates:
            # Grau entre os candidatos válidos
            degree = sum(1 for other in candidates 
                        if other != candidate and candidate in self.adjacency_dict[other])
            candidate_degrees.append((candidate, degree))
        
        # Ordenar por grau (decrescente)
        candidate_degrees.sort(key=lambda x: x[1], reverse=True)
        
        if not candidate_degrees:
            return candidates
        
        # Calcular limites da RCL
        best_value = candidate_degrees[0][1]
        worst_value = candidate_degrees[-1][1]
        
        # Evitar divisão por zero
        if best_value == worst_value:
            threshold = best_value
        else:
            threshold = worst_value + self.params.alpha * (best_value - worst_value)
        
        # Construir RCL
        rcl = [candidate for candidate, degree in candidate_degrees if degree >= threshold]
        
        return rcl

    def _local_search(self, initial_clique: List[int]) -> List[int]:
        """
        Fase de Busca Local do GRASP.
        
        Aplica operadores de vizinhança para melhorar a solução:
        1. ADD: Tentar adicionar vértices ao clique
        2. REMOVE: Remover vértice e tentar adicionar outros
        3. SWAP: Trocar vértice do clique por outro
        
        Args:
            initial_clique: Clique inicial
            
        Returns:
            Clique melhorado
        """
        current_clique = initial_clique.copy()
        improvement_found = True
        
        intensity = 0
        while improvement_found and intensity < self.params.local_search_intensity:
            improvement_found = False
            intensity += 1
            
            # Operador ADD: tentar adicionar vértices
            improved_clique = self._local_search_add(current_clique)
            if len(improved_clique) > len(current_clique):
                current_clique = improved_clique
                improvement_found = True
                continue
            
            # Operador SWAP: trocar vértices
            improved_clique = self._local_search_swap(current_clique)
            if len(improved_clique) > len(current_clique):
                current_clique = improved_clique
                improvement_found = True
                continue
            
            # Operador REMOVE-ADD: remover um e tentar adicionar outros
            improved_clique = self._local_search_remove_add(current_clique)
            if len(improved_clique) > len(current_clique):
                current_clique = improved_clique
                improvement_found = True
        
        return current_clique

    def _local_search_add(self, clique: List[int]) -> List[int]:
        """
        Operador ADD: tentar adicionar vértices ao clique.
        
        Args:
            clique: Clique atual
            
        Returns:
            Clique possivelmente expandido
        """
        clique_set = set(clique)
        candidates = set(self.nodes) - clique_set
        
        for candidate in candidates:
            # Verificar se candidate é adjacente a todos no clique
            if all(candidate in self.adjacency_dict[v] for v in clique):
                return clique + [candidate]
        
        return clique

    def _local_search_swap(self, clique: List[int]) -> List[int]:
        """
        Operador SWAP: trocar um vértice do clique por outro.
        
        Args:
            clique: Clique atual
            
        Returns:
            Clique possivelmente melhorado
        """
        if len(clique) <= 1:
            return clique
        
        clique_set = set(clique)
        non_clique = set(self.nodes) - clique_set
        
        for v_out in clique:
            for v_in in non_clique:
                # Tentar trocar v_out por v_in
                new_clique = [v if v != v_out else v_in for v in clique]
                if self._is_valid_clique(new_clique):
                    return new_clique
        
        return clique

    def _local_search_remove_add(self, clique: List[int]) -> List[int]:
        """
        Operador REMOVE-ADD: remover um vértice e tentar adicionar múltiplos.
        
        Args:
            clique: Clique atual
            
        Returns:
            Clique possivelmente melhorado
        """
        if len(clique) <= 1:
            return clique
        
        best_clique = clique
        
        for v_remove in clique:
            # Remover vértice
            reduced_clique = [v for v in clique if v != v_remove]
            
            # Tentar adicionar vértices ao clique reduzido
            expanded_clique = self._greedy_expansion(reduced_clique)
            
            if len(expanded_clique) > len(best_clique):
                best_clique = expanded_clique
        
        return best_clique

    def _greedy_expansion(self, clique: List[int]) -> List[int]:
        """
        Expansão gulosa: adicionar vértices greedily.
        
        Args:
            clique: Clique inicial
            
        Returns:
            Clique expandido
        """
        current_clique = clique.copy()
        clique_set = set(current_clique)
        
        improvement = True
        while improvement:
            improvement = False
            candidates = set(self.nodes) - clique_set
            
            # Encontrar candidato com maior grau entre os candidatos
            best_candidate = None
            best_degree = -1
            
            for candidate in candidates:
                if all(candidate in self.adjacency_dict[v] for v in current_clique):
                    degree = sum(1 for other in candidates 
                               if other != candidate and candidate in self.adjacency_dict[other])
                    if degree > best_degree:
                        best_degree = degree
                        best_candidate = candidate
            
            if best_candidate is not None:
                current_clique.append(best_candidate)
                clique_set.add(best_candidate)
                improvement = True
        
        return current_clique

    def _is_valid_clique(self, vertices: List[int]) -> bool:
        """
        Verificar se um conjunto de vértices forma um clique válido.
        
        Args:
            vertices: Lista de vértices
            
        Returns:
            True se é um clique válido, False caso contrário
        """
        if len(vertices) <= 1:
            return True
        
        for i in range(len(vertices)):
            for j in range(i + 1, len(vertices)):
                if vertices[j] not in self.adjacency_dict[vertices[i]]:
                    return False
        
        return True

    def _print_final_results(self):
        """Imprimir resultados finais do GRASP."""
        print("\n🏁 GRASP FINALIZADO!")
        print("="*50)
        print(f"🎯 Melhor clique encontrado: {self.best_clique_size} vértices")
        print(f"⏱️  Tempo total: {self.stats.total_time:.2f}s")
        print(f"🔄 Iterações executadas: {self.stats.total_iterations}")
        print(f"📈 Melhorias encontradas: {self.stats.improvements_found}")
        print(f"🏆 Melhor solução na iteração: {self.stats.best_iteration}")
        print(f"⚙️  Tempo de construção: {self.stats.construction_time:.2f}s")
        print(f"🔍 Tempo de busca local: {self.stats.local_search_time:.2f}s")
        
        if len(self.best_clique) <= 20:
            print(f"📋 Clique: {sorted(self.best_clique)}")
        else:
            print(f"📋 Clique: {sorted(self.best_clique[:10])} ... (+{len(self.best_clique)-10} vértices)")
        
        print("="*50)

    def get_statistics(self) -> Dict:
        """
        Obter estatísticas detalhadas da execução.
        
        Returns:
            Dicionário com estatísticas
        """
        return {
            'total_iterations': self.stats.total_iterations,
            'total_time': self.stats.total_time,
            'construction_time': self.stats.construction_time,
            'local_search_time': self.stats.local_search_time,
            'best_iteration': self.stats.best_iteration,
            'improvements_found': self.stats.improvements_found,
            'best_clique_size': self.best_clique_size,
            'alpha': self.params.alpha,
            'max_iterations': self.params.max_iterations,
            'convergence_history': self.stats.clique_sizes_history.copy()
        }


def solve_maximum_clique_grasp(graph: nx.Graph, 
                              alpha: float = 0.3,
                              max_iterations: int = 1000,
                              time_limit: float = 300.0,
                              max_no_improvement: int = 100,
                              seed: Optional[int] = None,
                              verbose: bool = True) -> Tuple[List[int], int, float]:
    """
    Interface principal para resolver o problema do clique máximo com GRASP.
    
    Args:
        graph: Grafo NetworkX
        alpha: Parâmetro de aleatoriedade do GRASP (0=guloso, 1=aleatório)
        max_iterations: Número máximo de iterações
        time_limit: Limite de tempo em segundos
        max_no_improvement: Máximo de iterações sem melhoria
        seed: Semente aleatória para reprodutibilidade
        verbose: Imprimir progresso da execução
        
    Returns:
        Tupla (clique, tamanho, tempo_execução)
    """
    params = GRASPParameters(
        alpha=alpha,
        max_iterations=max_iterations,
        time_limit=time_limit,
        max_no_improvement=max_no_improvement,
        seed=seed,
        verbose=verbose
    )
    
    grasp = GRASPMaximumClique(graph, params)
    return grasp.solve()


def compare_grasp_parameters(graph: nx.Graph, 
                           alpha_values: List[float] = [0.1, 0.3, 0.5, 0.7, 0.9],
                           iterations_per_test: int = 100,
                           time_limit: float = 60.0) -> Dict:
    """
    Comparar diferentes valores de α para calibrar o GRASP.
    
    Args:
        graph: Grafo a testar
        alpha_values: Lista de valores de α para testar
        iterations_per_test: Iterações por teste
        time_limit: Limite de tempo por teste
        
    Returns:
        Dicionário com resultados da comparação
    """
    results = {}
    
    print(f"\n🧪 CALIBRAÇÃO DE PARÂMETROS GRASP")
    print(f"Testando {len(alpha_values)} valores de α...")
    
    for alpha in alpha_values:
        print(f"\n🔧 Testando α = {alpha}")
        
        clique, size, exec_time = solve_maximum_clique_grasp(
            graph=graph,
            alpha=alpha,
            max_iterations=iterations_per_test,
            time_limit=time_limit,
            verbose=False
        )
        
        results[alpha] = {
            'clique_size': size,
            'execution_time': exec_time,
            'clique': clique
        }
        
        print(f"   Resultado: clique {size}, tempo {exec_time:.2f}s")
    
    # Encontrar melhor α
    best_alpha = max(results.keys(), key=lambda a: results[a]['clique_size'])
    
    print(f"\n🏆 MELHOR PARÂMETRO: α = {best_alpha}")
    print(f"   Clique: {results[best_alpha]['clique_size']}")
    print(f"   Tempo: {results[best_alpha]['execution_time']:.2f}s")
    
    return results


if __name__ == "__main__":
    # Exemplo de uso
    print("🧪 TESTE DO ALGORITMO GRASP")
    
    # Criar grafo de teste
    G = nx.Graph()
    G.add_edges_from([(1,2), (1,3), (1,4), (2,3), (2,4), (3,4), (5,6), (5,7), (6,7)])
    
    print(f"📊 Grafo de teste: {len(G.nodes())} nós, {len(G.edges())} arestas")
    
    # Executar GRASP
    clique, size, time_exec = solve_maximum_clique_grasp(
        graph=G,
        alpha=0.3,
        max_iterations=50,
        time_limit=10.0,
        verbose=True
    )
    
    print(f"\n✅ Resultado: clique de tamanho {size} em {time_exec:.3f}s")
    print(f"📋 Vértices: {sorted(clique)}")
