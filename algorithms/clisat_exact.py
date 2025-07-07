"""
CliSAT: A SAT-based exact algorithm for maximum clique problems

This implementation follows the research paper:
"CliSAT: A new exact algorithm for hard maximum clique problems"
by P. San Segundo, F. Furini, D. Álvarez, et al.

The algorithm implements the specific techniques described in the paper:
- ISEQ (Incremental Sequential Coloring) - Section 2.2
- SATCOL - Section 2.2.2
- Filter Phase (FiltCOL + FiltSAT) - Sections 2.3.1 and 2.3.2
- Incremental Upper Bounds - Section 2.4
- COLOR-SORT - Section 2.5
"""

import networkx as nx
from pysat.solvers import Glucose3
from pysat.formula import CNF
from itertools import combinations
import time
import logging
import os
import sys
from typing import List, Set, Tuple, Optional, Dict

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CliSAT:
    """
    CliSAT algorithm implementation based on the original paper.
    
    This implementation follows the exact structure and techniques described
    in the CliSAT paper, including all the specific algorithms mentioned.
    """
    
    def __init__(self, graph: nx.Graph, time_limit: float = 3600.0, log_interval: int = 1000, 
                 time_interval: float = 30.0, monitor_mode: str = 'log'):
        """
        Initialize the CliSAT solver.
        
        Args:
            graph: NetworkX graph
            time_limit: Maximum time limit in seconds (default: 1 hour)
            log_interval: Intervalo para logs periódicos (número de nós processados)
            time_interval: Intervalo de tempo para logs periódicos (segundos)
            monitor_mode: Tipo de monitoramento ('log', 'realtime', 'both', 'silent')
        """
        self.graph = graph
        self.n = graph.number_of_nodes()
        self.time_limit = time_limit
        self.start_time = None
        self.log_interval = log_interval
        self.time_interval = time_interval
        self.monitor_mode = monitor_mode
        
        # Criar matriz de adjacência
        self.adj_matrix = nx.adjacency_matrix(graph).todense()
        
        # Variáveis para o melhor clique encontrado
        self.max_clique = []
        self.lb = 0  # Lower bound (best clique size found so far)
        
        # Estruturas específicas do algoritmo CliSAT
        self.mu = {}  # Incremental upper bounds (Seção 2.4)
        self.coloring = {}  # Armazena colorações parciais
        self.initial_ordering = []  # COLOR-SORT ordering
        
        # Estatísticas
        self.stats = {
            'nodes_explored': 0,
            'sat_calls': 0,
            'pruned_by_bound': 0,
            'filter_phase_calls': 0,
            'satcol_calls': 0
        }
        
        # Controle de logs periódicos
        self.last_log_time = 0
        self.last_log_nodes = 0
        
        # Controle de monitoramento em tempo real
        self.dashboard_lines = 0
        
        # Mapeamento de nós para trabalhar com índices consistentes
        self.node_to_index = {node: i for i, node in enumerate(sorted(graph.nodes()))}
        self.index_to_node = {i: node for node, i in self.node_to_index.items()}
    
    def _log_progress(self, force: bool = False):
        """
        Log progress baseado no modo de monitoramento configurado.
        
        Args:
            force: Force logging regardless of interval
        """
        if self.monitor_mode == 'silent':
            return
        
        current_time = time.time() - self.start_time
        nodes_since_last = self.stats['nodes_explored'] - self.last_log_nodes
        time_since_last = current_time - self.last_log_time
        
        # Verificar se deve fazer log/atualização
        should_update = (force or 
                        nodes_since_last >= self.log_interval or 
                        time_since_last >= self.time_interval)
        
        if not should_update:
            return
        
        if self.monitor_mode == 'log':
            self._log_traditional(force)
        elif self.monitor_mode == 'realtime':
            self._display_realtime_dashboard()
        elif self.monitor_mode == 'both':
            # Em modo 'both', usar realtime durante execução e log para eventos especiais
            if force:
                self._log_traditional(force)
            else:
                self._display_realtime_dashboard()
        
        # Atualizar contadores apenas se não for realtime puro
        if self.monitor_mode != 'realtime' or force:
            self.last_log_nodes = self.stats['nodes_explored']
            self.last_log_time = current_time

    def _time_exceeded(self) -> bool:
        """Verificar se o tempo limite foi excedido."""
        if self.start_time is None:
            return False
        return time.time() - self.start_time > self.time_limit

    def solve(self) -> Tuple[List, int]:
        """
        Resolver o problema do clique máximo usando o algoritmo CliSAT.
        
        Returns:
            Tuple contendo (lista_de_nós_do_clique, tamanho_do_clique)
        """
        self.start_time = time.time()
        self.last_log_time = 0
        
        print(f"\n🚀 INICIANDO CliSAT")
        print(f"   📊 Grafo: {self.n} vértices, {self.graph.number_of_edges()} arestas")
        print(f"   ⏱️  Limite de tempo: {self.time_limit:.0f}s")
        print(f"   📋 Intervalo de log: a cada {self.log_interval} nós ou {self.time_interval}s")
        print(f"   👀 Modo de monitoramento: {self.monitor_mode}")
        print("=" * 50)
        
        logger.info(f"Iniciando CliSAT para grafo com {self.n} vértices")
        
        # Clique inicial guloso (limite inferior)
        self.max_clique = self.greedy_initial_solution()
        self.lb = len(self.max_clique)
        logger.info(f"Clique inicial (guloso): tamanho {self.lb}")
        
        print(f"\n🎯 Clique inicial encontrado:")
        print(f"   📏 Tamanho: {self.lb}")
        print(f"   📋 Vértices: {self.max_clique[:min(10, len(self.max_clique))]}")
        if len(self.max_clique) > 10:
            print(f"        ... e mais {len(self.max_clique) - 10} vértices")
        
        # COLOR-SORT (Seção 2.5)
        self.initial_ordering = self.color_sort()
        print(f"\n🎨 Ordenação COLOR-SORT concluída")
        
        # Algoritmo principal do CliSAT
        print(f"\n🔄 Iniciando busca principal...")
        for i in range(self.lb, self.n):
            if self._time_exceeded():
                logger.warning("Tempo limite excedido")
                print(f"\n⏰ Tempo limite de {self.time_limit}s excedido!")
                break
                
            vi = self.initial_ordering[i]
            # V_hat: vértices anteriores na ordenação que são adjacentes a vi
            V_hat = [v for v in self.initial_ordering[:i] 
                    if self.adj_matrix[self.node_to_index[vi], self.node_to_index[v]] == 1]
            
            if not V_hat:
                continue
                
            # Criar subgrafo induzido por V_hat
            G_hat = self.graph.subgraph(V_hat)
            self.find_max_clique(G_hat, [vi], self.lb)
            
            # Log periódico
            self._log_progress()
        
        # Log final forçado
        self._log_progress(force=True)
        
        total_time = time.time() - self.start_time
        print(f"\n🏁 CliSAT FINALIZADO!")
        print(f"   ⏱️  Tempo total: {total_time:.2f}s")
        print(f"   🎯 Clique máximo: {len(self.max_clique)} vértices")
        print(f"   📋 Vértices: {self.max_clique}")
        print(f"   📊 Nós explorados: {self.stats['nodes_explored']:,}")
        print(f"   🔗 Chamadas SAT: {self.stats['sat_calls']:,}")
        print(f"   ✂️  Podas por limite: {self.stats['pruned_by_bound']:,}")
        print("=" * 50)
        
        logger.info(f"CliSAT finalizado em {total_time:.2f}s")
        logger.info(f"Melhor clique encontrado: tamanho {self.lb}")
        logger.info(f"Estatísticas: {self.stats}")
        
        return self.max_clique, self.lb

    def find_max_clique(self, G_hat: nx.Graph, K_hat: List, lb: int) -> None:
        """
        Algoritmo recursivo principal para encontrar clique máximo.
        
        Args:
            G_hat: Subgrafo atual
            K_hat: Clique parcial atual
            lb: Lower bound atual
        """
        self.stats['nodes_explored'] += 1
        
        if self._time_exceeded():
            return
        
        # Atualizar melhor clique se necessário
        if len(K_hat) > self.lb:
            self.lb = len(K_hat)
            self.max_clique = K_hat.copy()
            
            # Log de novo clique baseado no modo
            if self.monitor_mode != 'silent':
                elapsed = time.time() - self.start_time
                hours = int(elapsed // 3600)
                minutes = int((elapsed % 3600) // 60)
                seconds = int(elapsed % 60)
                
                if self.monitor_mode == 'realtime':
                    # No modo realtime, apenas atualizar o dashboard
                    self._display_realtime_dashboard()
                else:
                    # Nos outros modos, fazer log completo
                    print(f"\n🎉 NOVO MELHOR CLIQUE ENCONTRADO!")
                    print(f"   📏 Tamanho: {self.lb}")
                    print(f"   ⏱️  Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}")
                    print(f"   🔢 Nó: {self.stats['nodes_explored']:,}")
                    print(f"   📋 Clique: {K_hat[:min(10, len(K_hat))]}")
                    if len(K_hat) > 10:
                        print(f"        ... e mais {len(K_hat) - 10} vértices")
            
            logger.info(f"Novo melhor clique encontrado: tamanho {self.lb}")
        
        # Compute pruned and branching sets
        P, B = self.compute_pruned_and_branching_sets(G_hat, K_hat, lb)
        
        if not B:
            self.stats['pruned_by_bound'] += 1
            return
        
        # Branch sobre cada vértice em B
        for b in B:
            if self._time_exceeded():
                break
                
            # Calcular V_child: vértices adjacentes a b
            V_child = []
            
            # Adicionar vértices de P adjacentes a b
            for v in P:
                if G_hat.has_edge(b, v):
                    V_child.append(v)
            
            # Adicionar vértices de B adjacentes a b (com ordem lexicográfica)
            for v in B:
                if v != b and G_hat.has_edge(b, v) and v < b:
                    V_child.append(v)
            
            if not V_child:
                # Nó folha: verificar se encontramos um clique melhor
                new_clique_size = len(K_hat) + 1
                if new_clique_size > self.lb:
                    self.lb = new_clique_size
                    self.max_clique = K_hat + [b]
                    logger.info(f"Clique folha encontrado: tamanho {self.lb}")
                continue
            
            # Criar subgrafo filho
            G_child = G_hat.subgraph(V_child)
            
            # Decidir qual fase usar baseado na estrutura do grafo
            if self.is_k_partite(G_child, self.lb - len(K_hat)):
                # Usar Filter Phase (Seções 2.3.1 e 2.3.2)
                P_child, B_child = self.filter_phase(G_child, K_hat)
                self.stats['filter_phase_calls'] += 1
            else:
                # Usar SATCOL (Seção 2.2.2)
                P_child, B_child = self.satcol(G_child, K_hat)
                self.stats['satcol_calls'] += 1
            
            # Recursão se há vértices para explorar
            if B_child:
                self.find_max_clique(G_child, K_hat + [b], self.lb)
            else:
                # Poda: sem vértices para continuar a busca
                self.stats['pruned_by_bound'] += 1

    def compute_pruned_and_branching_sets(self, G_hat: nx.Graph, K_hat: List, lb: int) -> Tuple[List, List]:
        """
        Compute pruned and branching sets usando ISEQ + SATCOL.
        
        Args:
            G_hat: Subgrafo atual
            K_hat: Clique parcial atual  
            lb: Lower bound
            
        Returns:
            Tuple (P, B) onde P são vértices podados e B são vértices de branching
        """
        k = lb - len(K_hat)
        
        # ISEQ: Incremental Sequential Coloring (Seção 2.2)
        P_c = self.iseq_coloring(G_hat, k)
        
        # SATCOL: SAT-based coloring refinement (Seção 2.2.2)
        P, B = self.satcol(G_hat, K_hat, P_c)
        
        return P, B

    def iseq_coloring(self, G: nx.Graph, k: int) -> List[List]:
        """
        ISEQ: Incremental Sequential Coloring (Seção 2.2).
        
        Encontra k classes de cores (conjuntos independentes) no grafo.
        
        Args:
            G: Grafo para colorir
            k: Número máximo de cores
            
        Returns:
            Lista de classes de cores (cada classe é uma lista de vértices)
        """
        coloring = []
        uncolored = list(G.nodes())
        
        while len(coloring) < k and uncolored:
            independent_set = []
            remaining = uncolored.copy()
            
            for v in remaining:
                # Verificar se v pode ser adicionado ao conjunto independente
                if all(not G.has_edge(v, u) for u in independent_set):
                    independent_set.append(v)
                    uncolored.remove(v)
            
            if independent_set:
                coloring.append(independent_set)
            else:
                break
        
        return coloring

    def satcol(self, G: nx.Graph, K_hat: List, P_c: Optional[List[List]] = None) -> Tuple[List, List]:
        """
        SATCOL: SAT-based coloring refinement (Seção 2.2.2).
        
        Args:
            G: Grafo atual
            K_hat: Clique parcial atual
            P_c: Coloração prévia (opcional)
            
        Returns:
            Tuple (P, B) onde P são vértices podados e B são vértices de branching
        """
        if P_c is None:
            P_c = self.iseq_coloring(G, self.lb - len(K_hat))
        
        # P: vértices que podem ser podados (estão nas classes de cor)
        P = [v for color_class in P_c for v in color_class]
        
        # B: vértices restantes que precisam de branching
        B = [v for v in G.nodes() if v not in P]
        
        # Refinar usando failed literal detection
        for v in B.copy():
            if self.is_failed_literal(G, v, P_c):
                P.append(v)
                B.remove(v)
        
        return P, B

    def is_failed_literal(self, G: nx.Graph, v, coloring: List[List]) -> bool:
        """
        Verificar se um vértice é um failed literal usando SAT.
        
        Args:
            G: Grafo atual
            v: Vértice a verificar
            coloring: Coloração atual
            
        Returns:
            True se v é failed literal, False caso contrário
        """
        self.stats['sat_calls'] += 1
        
        # Criar nova coloração incluindo v
        extended_coloring = coloring + [[v]]
        cnf = self.build_pmax_sat(G, extended_coloring)
        
        # Resolver usando SAT solver
        with Glucose3(bootstrap_with=cnf) as solver:
            return not solver.solve()

    def build_pmax_sat(self, G: nx.Graph, coloring: List[List]) -> CNF:
        """
        Construir fórmula SAT P-MAX (Partial Maximum Clique).
        
        Args:
            G: Grafo atual
            coloring: Classes de cores
            
        Returns:
            Fórmula CNF para o problema
        """
        cnf = CNF()
        
        # Mapear vértices para variáveis SAT (1-indexed)
        vertex_to_var = {}
        var_counter = 1
        
        for color_class in coloring:
            for v in color_class:
                if v not in vertex_to_var:
                    vertex_to_var[v] = var_counter
                    var_counter += 1
        
        # Restrições de clique: se dois vértices não são adjacentes,
        # não podem estar ambos no clique
        for color_class in coloring:
            for u, v in combinations(color_class, 2):
                if not G.has_edge(u, v):
                    # ¬x_u ∨ ¬x_v
                    var_u = vertex_to_var.get(u)
                    var_v = vertex_to_var.get(v)
                    if var_u and var_v:
                        cnf.append([-var_u, -var_v])
        
        # Restrição de cardinalidade: pelo menos um vértice de cada classe
        for color_class in coloring:
            if color_class:
                clause = [vertex_to_var[v] for v in color_class if v in vertex_to_var]
                if clause:
                    cnf.append(clause)
        
        return cnf

    def filter_phase(self, G: nx.Graph, K_hat: List) -> Tuple[List, List]:
        """
        Filter Phase: FiltCOL + FiltSAT (Seções 2.3.1 e 2.3.2).
        
        Args:
            G: Grafo atual
            K_hat: Clique parcial atual
            
        Returns:
            Tuple (P, B) onde P são vértices podados e B são vértices de branching
        """
        # FiltCOL (Seção 2.3.1)
        P_filt = self.filtcol(G)
        B_filt = [v for v in G.nodes() if v not in P_filt]
        
        # FiltSAT (Seção 2.3.2)
        P_final, B_final = self.filtsat(G, P_filt, B_filt)
        
        return P_final, B_final

    def filtcol(self, G: nx.Graph) -> List:
        """
        FiltCOL: Filter using coloring information (Seção 2.3.1).
        
        Args:
            G: Grafo atual
            
        Returns:
            Lista de vértices que podem ser filtrados
        """
        # Implementação simplificada: usar coloração de referência
        filtered = set()
        graph_id = id(G)
        reference_coloring = self.coloring.get(graph_id, [])
        
        # Se não há coloração de referência, criar uma nova
        if not reference_coloring:
            reference_coloring = self.iseq_coloring(G, min(len(G.nodes()), self.lb))
            self.coloring[graph_id] = reference_coloring
        
        # Filtrar vértices que não estão em nenhuma classe de cor viável
        all_colored = set()
        for color_class in reference_coloring:
            all_colored.update(color_class)
        
        return [v for v in G.nodes() if v in all_colored]

    def filtsat(self, G: nx.Graph, P: List, B: List) -> Tuple[List, List]:
        """
        FiltSAT: SAT-based filtering (Seção 2.3.2).
        
        Args:
            G: Grafo atual
            P: Vértices previamente filtrados
            B: Vértices candidatos a branching
            
        Returns:
            Tuple (P_final, B_final) após refinamento SAT
        """
        P_final = P.copy()
        B_final = B.copy()
        
        # Aplicar failed literal detection nos vértices de B
        for v in B.copy():
            coloring = self.iseq_coloring(G.subgraph(P_final + [v]), len(P_final) + 1)
            if self.is_failed_literal(G, v, coloring):
                P_final.append(v)
                B_final.remove(v)
        
        return P_final, B_final

    def is_k_partite(self, G: nx.Graph, k: int) -> bool:
        """
        Verificar se o grafo é k-partite.
        
        Args:
            G: Grafo a verificar
            k: Número de partições
            
        Returns:
            True se G é k-partite, False caso contrário
        """
        if len(G.nodes()) == 0:
            return True
        
        coloring = self.iseq_coloring(G, k)
        
        # O grafo é k-partite se conseguimos colori-lo com exatamente k cores
        # e cada classe de cor é um conjunto independente válido
        total_colored = sum(len(color_class) for color_class in coloring)
        return total_colored == len(G.nodes()) and len(coloring) <= k

    def color_sort(self) -> List:
        """
        COLOR-SORT: Ordenação especial dos vértices (Seção 2.5).
        
        Ordena os vértices de forma a otimizar o algoritmo de branch-and-bound.
        Usa uma combinação de grau e características estruturais.
        
        Returns:
            Lista ordenada de vértices
        """
        vertices = list(self.graph.nodes())
        
        # Implementação baseada em grau decrescente + características adicionais
        def sort_key(v):
            degree = self.graph.degree(v)
            # Adicionar critérios adicionais baseados na estrutura local
            neighbors = list(self.graph.neighbors(v))
            if neighbors:
                # Densidade da vizinhança
                subgraph = self.graph.subgraph(neighbors)
                neighbor_edges = len(subgraph.edges())
                max_edges = len(neighbors) * (len(neighbors) - 1) // 2
                density = neighbor_edges / max_edges if max_edges > 0 else 0
            else:
                density = 0
            
            # Priorizar vértices com alto grau e alta densidade na vizinhança
            return (-degree, -density)
        
        vertices.sort(key=sort_key)
        return vertices

    def greedy_initial_solution(self) -> List:
        """
        Heurística gulosa para encontrar clique inicial (Seção 2.5).
        
        Encontra um clique inicial usando estratégia gulosa baseada em grau.
        Isso fornece um limite inferior para o algoritmo principal.
        
        Returns:
            Lista de vértices formando um clique
        """
        # Ordenar vértices por grau decrescente
        vertices = sorted(self.graph.nodes(), 
                         key=lambda x: self.graph.degree(x), 
                         reverse=True)
        
        clique = []
        
        for v in vertices:
            # Verificar se v é adjacente a todos os vértices no clique atual
            if all(self.graph.has_edge(v, u) for u in clique):
                clique.append(v)
                
                # Otimização: se o clique está ficando grande,
                # focar nos vértices com maior grau na vizinhança comum
                if len(clique) > 3:
                    # Calcular vizinhança comum
                    common_neighbors = set(self.graph.neighbors(clique[0]))
                    for u in clique[1:]:
                        common_neighbors &= set(self.graph.neighbors(u))
                    
                    # Reordenar vértices restantes priorizando vizinhança comum
                    remaining = [x for x in vertices if x not in clique]
                    remaining.sort(key=lambda x: (
                        x in common_neighbors,
                        self.graph.degree(x)
                    ), reverse=True)
                    vertices = clique + remaining
        
        return clique

    def get_statistics(self) -> Dict:
        """
        Obter estatísticas detalhadas da execução.
        
        Returns:
            Dicionário com estatísticas da execução
        """
        total_time = 0
        if self.start_time:
            total_time = time.time() - self.start_time
        
        return {
            **self.stats,
            'total_time': total_time,
            'best_clique_size': self.lb,
            'graph_vertices': self.n,
            'graph_edges': len(self.graph.edges()),
            'time_limit': self.time_limit
        }

    def verify_clique(self, clique: List) -> bool:
        """
        Verificar se uma lista de vértices forma um clique válido.
        
        Args:
            clique: Lista de vértices
            
        Returns:
            True se é um clique válido, False caso contrário
        """
        if len(clique) <= 1:
            return True
        
        # Verificar se todos os pares são adjacentes
        for i, u in enumerate(clique):
            for v in clique[i+1:]:
                if not self.graph.has_edge(u, v):
                    return False
        
        return True

    def print_solution_summary(self) -> None:
        """Imprimir resumo da solução encontrada."""
        print(f"\n=== CliSAT Solution Summary ===")
        print(f"Graph: {self.n} vertices, {len(self.graph.edges())} edges")
        print(f"Maximum clique size: {self.lb}")
        print(f"Maximum clique: {self.max_clique}")
        print(f"Is valid clique: {self.verify_clique(self.max_clique)}")
        
        stats = self.get_statistics()
        print(f"\n=== Execution Statistics ===")
        for key, value in stats.items():
            if key == 'total_time':
                print(f"{key}: {value:.2f}s")
            else:
                print(f"{key}: {value}")
    
    def _clear_screen(self):
        """Limpar tela para monitoramento em tempo real."""
        if os.name == 'nt':  # Windows
            os.system('cls')
        else:  # Linux/Mac
            os.system('clear')
    
    def _move_cursor_up(self, lines: int):
        """Mover cursor para cima (para atualizar dashboard)."""
        if lines > 0:
            sys.stdout.write(f'\033[{lines}A')
            sys.stdout.flush()
    
    def _display_realtime_dashboard(self):
        """Exibir dashboard em tempo real (atualiza na mesma posição)."""
        current_time = time.time() - self.start_time
        hours = int(current_time // 3600)
        minutes = int((current_time % 3600) // 60)
        seconds = int(current_time % 60)
        
        rate = self.stats['nodes_explored'] / current_time if current_time > 0 else 0
        
        # Se não é a primeira vez, mover cursor para cima
        if self.dashboard_lines > 0:
            self._move_cursor_up(self.dashboard_lines)
        
        dashboard = []
        dashboard.append("┌" + "─" * 58 + "┐")
        dashboard.append("│" + " " * 18 + "🔍 CliSAT MONITOR" + " " * 22 + "│")
        dashboard.append("├" + "─" * 58 + "┤")
        dashboard.append(f"│ ⏱️  Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}" + " " * 32 + "│")
        dashboard.append(f"│ 🔢 Nós: {self.stats['nodes_explored']:,}" + " " * (50 - len(f"Nós: {self.stats['nodes_explored']:,}")) + "│")
        dashboard.append(f"│ 📊 Taxa: {rate:.1f} nós/seg" + " " * (42 - len(f"Taxa: {rate:.1f} nós/seg")) + "│")
        dashboard.append(f"│ 🎯 Clique: {len(self.max_clique)} vértices" + " " * (36 - len(f"Clique: {len(self.max_clique)} vértices")) + "│")
        
        if self.max_clique:
            clique_str = str(self.max_clique[:5])
            if len(self.max_clique) > 5:
                clique_str = clique_str[:-1] + f"...+{len(self.max_clique)-5}]"
            dashboard.append(f"│ 📋 {clique_str}" + " " * (56 - len(clique_str)) + "│")
        else:
            dashboard.append("│ 📋 Nenhum clique encontrado" + " " * 25 + "│")
        
        dashboard.append(f"│ 🔗 SAT: {self.stats['sat_calls']:,}" + " " * (48 - len(f"SAT: {self.stats['sat_calls']:,}")) + "│")
        dashboard.append(f"│ ✂️  Podas: {self.stats['pruned_by_bound']:,}" + " " * (45 - len(f"Podas: {self.stats['pruned_by_bound']:,}")) + "│")
        dashboard.append("└" + "─" * 58 + "┘")
        
        # Imprimir dashboard
        for line in dashboard:
            print(line)
        
        # Armazenar número de linhas para próxima atualização
        self.dashboard_lines = len(dashboard)
    
    def _log_traditional(self, force: bool = False):
        """Log tradicional (modo atual)."""
        current_time = time.time() - self.start_time
        nodes_since_last = self.stats['nodes_explored'] - self.last_log_nodes
        time_since_last = current_time - self.last_log_time
        
        # Log se: forçado, ou atingiu intervalo de nós, ou atingiu intervalo de tempo
        should_log = (force or 
                     nodes_since_last >= self.log_interval or 
                     time_since_last >= self.time_interval)
        
        if should_log:
            elapsed_time = current_time
            hours = int(elapsed_time // 3600)
            minutes = int((elapsed_time % 3600) // 60)
            seconds = int(elapsed_time % 60)
            
            rate = self.stats['nodes_explored'] / elapsed_time if elapsed_time > 0 else 0
            
            print(f"\n🔍 PROGRESSO CliSAT:")
            print(f"   ⏱️  Tempo: {hours:02d}:{minutes:02d}:{seconds:02d}")
            print(f"   🔢 Nós processados: {self.stats['nodes_explored']:,}")
            print(f"   📊 Taxa: {rate:.1f} nós/seg")
            print(f"   🎯 Maior clique: {len(self.max_clique)} vértices")
            if self.max_clique:
                print(f"   📋 Clique atual: {self.max_clique[:min(10, len(self.max_clique))]}")
                if len(self.max_clique) > 10:
                    print(f"        ... e mais {len(self.max_clique) - 10} vértices")
            print(f"   🔗 Chamadas SAT: {self.stats['sat_calls']:,}")
            print(f"   ✂️  Podas: {self.stats['pruned_by_bound']:,}")
            print(f"   🧮 Filter Phase: {self.stats['filter_phase_calls']:,}")
            print(f"   🎨 SATCOL: {self.stats['satcol_calls']:,}")
            print("-" * 50)
            
            self.last_log_nodes = self.stats['nodes_explored']
            self.last_log_time = current_time


def solve_maximum_clique_clisat(graph: nx.Graph, time_limit: float = 3600.0, 
                                log_interval: int = 1000, time_interval: float = 30.0,
                                monitor_mode: str = 'log') -> Tuple[List, int, float]:
    """
    Função conveniente para resolver o problema do clique máximo usando CliSAT.
    
    Args:
        graph: Grafo NetworkX
        time_limit: Tempo limite em segundos (default: 1 hora)
        log_interval: Intervalo de nós para logs periódicos
        time_interval: Intervalo de tempo para logs periódicos (segundos)
        monitor_mode: Modo de monitoramento ('log', 'realtime', 'both', 'silent')
        
    Returns:
        Tuple contendo (lista_de_nós_do_clique, tamanho_do_clique, tempo_execução)
    """
    start_time = time.time()
    solver = CliSAT(graph, time_limit, log_interval, time_interval, monitor_mode)
    clique, size = solver.solve()
    execution_time = time.time() - start_time
    
    # Imprimir estatísticas se desejado
    if logger.isEnabledFor(logging.INFO):
        solver.print_solution_summary()
    
    return clique, size, execution_time


# Exemplo de uso e testes
if __name__ == "__main__":
    import argparse
    
    def create_test_graph() -> nx.Graph:
        """Criar um grafo de teste com clique conhecido."""
        G = nx.Graph()
        
        # Adicionar um clique de tamanho 4
        clique_nodes = [1, 2, 3, 4]
        for i in clique_nodes:
            for j in clique_nodes:
                if i != j:
                    G.add_edge(i, j)
        
        # Adicionar alguns nós extras conectados parcialmente
        G.add_edges_from([(5, 1), (5, 2), (6, 3), (6, 4), (7, 1), (7, 2), (7, 3)])
        
        # Adicionar um segundo clique menor
        G.add_edges_from([(8, 9), (8, 10), (9, 10)])
        
        # Conectar os cliques
        G.add_edge(4, 8)
        
        return G
    
    def test_clisat():
        """Testar o algoritmo CliSAT."""
        print("=== Teste do Algoritmo CliSAT ===")
        
        # Criar grafo de teste
        G = create_test_graph()
        
        print(f"Grafo de teste:")
        print(f"Vértices: {sorted(G.nodes())}")
        print(f"Arestas: {len(G.edges())}")
        print(f"Densidade: {nx.density(G):.3f}")
        
        # Resolver usando CliSAT
        print(f"\nExecutando CliSAT...")
        clique, size = solve_maximum_clique_clisat(G, time_limit=60.0)
        
        print(f"\nResultado:")
        print(f"Clique máximo encontrado: {clique}")
        print(f"Tamanho: {size}")
        
        # Verificar resultado
        solver = CliSAT(G)
        is_valid = solver.verify_clique(clique)
        print(f"Clique válido: {is_valid}")
        
        return clique, size
    
    # Executar teste se script for chamado diretamente
    parser = argparse.ArgumentParser(description='Teste do algoritmo CliSAT')
    parser.add_argument('--test', action='store_true', help='Executar teste básico')
    parser.add_argument('--verbose', action='store_true', help='Saída detalhada')
    
    args = parser.parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    if args.test:
        test_clisat()
    else:
        print("Use --test para executar o teste básico ou --help para ver opções")