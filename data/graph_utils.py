"""
Utilitários para manipulação e análise de grafos

Este módulo fornece funções utilitárias para trabalhar com grafos
no contexto do problema do clique máximo.
"""

import networkx as nx
import numpy as np
from typing import List, Set, Tuple, Dict, Any, Optional
import logging

logger = logging.getLogger(__name__)


class GraphUtils:
    """
    Classe com utilitários estáticos para análise de grafos.
    """
    
    @staticmethod
    def analyze_graph(graph: nx.Graph) -> Dict[str, Any]:
        """
        Analisar propriedades básicas de um grafo.
        
        Args:
            graph: Grafo NetworkX
            
        Returns:
            Dicionário com propriedades do grafo
        """
        n_nodes = len(graph.nodes())
        n_edges = len(graph.edges())
        
        analysis = {
            'nodes': n_nodes,
            'edges': n_edges,
            'density': nx.density(graph),
            'is_connected': nx.is_connected(graph),
            'number_of_components': nx.number_connected_components(graph),
            'average_clustering': nx.average_clustering(graph),
            'average_degree': 2 * n_edges / n_nodes if n_nodes > 0 else 0,
            'max_degree': max(dict(graph.degree()).values()) if n_nodes > 0 else 0,
            'min_degree': min(dict(graph.degree()).values()) if n_nodes > 0 else 0
        }
        
        # Propriedades que requerem conectividade
        if analysis['is_connected']:
            try:
                analysis['diameter'] = nx.diameter(graph)
                analysis['radius'] = nx.radius(graph)
                analysis['center'] = list(nx.center(graph))
            except:
                analysis['diameter'] = None
                analysis['radius'] = None
                analysis['center'] = []
        else:
            analysis['diameter'] = None
            analysis['radius'] = None
            analysis['center'] = []
        
        return analysis
    
    @staticmethod
    def validate_clique(graph: nx.Graph, clique: List[int]) -> bool:
        """
        Validar se um conjunto de vértices forma um clique.
        
        Args:
            graph: Grafo NetworkX
            clique: Lista de vértices
            
        Returns:
            True se é um clique válido, False caso contrário
        """
        if len(clique) <= 1:
            return True
        
        # Verificar se todos os vértices existem
        for vertex in clique:
            if vertex not in graph:
                logger.warning(f"Vértice {vertex} não existe no grafo")
                return False
        
        # Verificar se todos os pares são adjacentes
        for i in range(len(clique)):
            for j in range(i + 1, len(clique)):
                if not graph.has_edge(clique[i], clique[j]):
                    logger.warning(f"Vértices {clique[i]} e {clique[j]} não são adjacentes")
                    return False
        
        return True
    
    @staticmethod
    def get_clique_induced_subgraph(graph: nx.Graph, clique: List[int]) -> nx.Graph:
        """
        Obter o subgrafo induzido por um clique.
        
        Args:
            graph: Grafo original
            clique: Lista de vértices do clique
            
        Returns:
            Subgrafo induzido
        """
        return graph.subgraph(clique).copy()
    
    @staticmethod
    def find_greedy_clique(graph: nx.Graph, start_vertex: Optional[int] = None) -> List[int]:
        """
        Encontrar um clique usando algoritmo guloso simples.
        
        Args:
            graph: Grafo NetworkX
            start_vertex: Vértice inicial (None para escolher automaticamente)
            
        Returns:
            Lista de vértices do clique encontrado
        """
        if len(graph.nodes()) == 0:
            return []
        
        # Escolher vértice inicial
        if start_vertex is None:
            # Escolher vértice com maior grau
            degrees = dict(graph.degree())
            start_vertex = max(degrees.keys(), key=lambda v: degrees[v])
        
        clique = [start_vertex]
        candidates = set(graph.neighbors(start_vertex))
        
        while candidates:
            # Escolher candidato com maior grau entre os candidatos
            candidate_degrees = {v: len(set(graph.neighbors(v)) & candidates) 
                               for v in candidates}
            best_candidate = max(candidate_degrees.keys(), 
                               key=lambda v: candidate_degrees[v])
            
            # Adicionar ao clique
            clique.append(best_candidate)
            
            # Atualizar candidatos: manter apenas vizinhos do novo vértice
            candidates &= set(graph.neighbors(best_candidate))
        
        return clique
    
    @staticmethod
    def get_complement_graph(graph: nx.Graph) -> nx.Graph:
        """
        Obter o complemento de um grafo.
        
        Args:
            graph: Grafo original
            
        Returns:
            Grafo complemento
        """
        return nx.complement(graph)
    
    @staticmethod
    def calculate_graph_metrics(graph: nx.Graph) -> Dict[str, float]:
        """
        Calcular métricas avançadas do grafo.
        
        Args:
            graph: Grafo NetworkX
            
        Returns:
            Dicionário com métricas
        """
        metrics = {}
        
        try:
            # Métricas básicas
            metrics['nodes'] = len(graph.nodes())
            metrics['edges'] = len(graph.edges())
            metrics['density'] = nx.density(graph)
            
            # Métricas de conectividade
            metrics['is_connected'] = nx.is_connected(graph)
            metrics['components'] = nx.number_connected_components(graph)
            
            # Métricas de grau
            degrees = list(dict(graph.degree()).values())
            metrics['avg_degree'] = np.mean(degrees) if degrees else 0
            metrics['max_degree'] = np.max(degrees) if degrees else 0
            metrics['min_degree'] = np.min(degrees) if degrees else 0
            metrics['degree_std'] = np.std(degrees) if degrees else 0
            
            # Métricas de clustering
            metrics['avg_clustering'] = nx.average_clustering(graph)
            metrics['transitivity'] = nx.transitivity(graph)
            
            # Métricas de centralidade (para grafos pequenos)
            if len(graph.nodes()) <= 1000:
                try:
                    centralities = nx.degree_centrality(graph)
                    metrics['max_centrality'] = max(centralities.values()) if centralities else 0
                    metrics['avg_centrality'] = np.mean(list(centralities.values())) if centralities else 0
                except:
                    metrics['max_centrality'] = 0
                    metrics['avg_centrality'] = 0
            
        except Exception as e:
            logger.warning(f"Erro ao calcular métricas: {e}")
        
        return metrics
    
    @staticmethod
    def export_graph_summary(graph: nx.Graph, filename: str = None) -> str:
        """
        Exportar resumo das propriedades do grafo.
        
        Args:
            graph: Grafo NetworkX
            filename: Arquivo para salvar (None para retornar string)
            
        Returns:
            String com o resumo
        """
        analysis = GraphUtils.analyze_graph(graph)
        metrics = GraphUtils.calculate_graph_metrics(graph)
        
        summary = f"""
RESUMO DO GRAFO
===============

Propriedades Básicas:
- Vértices: {analysis['nodes']}
- Arestas: {analysis['edges']}
- Densidade: {analysis['density']:.4f}
- Conectado: {analysis['is_connected']}
- Componentes: {analysis['number_of_components']}

Propriedades de Grau:
- Grau Médio: {analysis['average_degree']:.2f}
- Grau Máximo: {analysis['max_degree']}
- Grau Mínimo: {analysis['min_degree']}

Propriedades de Clustering:
- Clustering Médio: {analysis['average_clustering']:.4f}
- Transitividade: {metrics.get('transitivity', 'N/A'):.4f}

Propriedades de Distância:
- Diâmetro: {analysis['diameter'] or 'N/A'}
- Raio: {analysis['radius'] or 'N/A'}
- Centro: {analysis['center'] or 'N/A'}
"""
        
        if filename:
            with open(filename, 'w') as f:
                f.write(summary)
        
        return summary
