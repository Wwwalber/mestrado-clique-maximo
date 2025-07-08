"""
DIMACS Dataset Loader for Maximum Clique Problems

Este módulo baixa e carrega grafos da base de dados DIMACS para testes
do algoritmo CliSAT. Os grafos estão disponíveis em:
https://iridia.ulb.ac.be/~fmascia/maximum_clique/
"""

import os
import requests
import networkx as nx
import gzip
import shutil
from typing import Dict, List, Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class DIMACSLoader:
    """Classe para baixar e carregar grafos DIMACS."""
    
    def __init__(self, data_dir: str = "dimacs_data"):
        """
        Inicializar o loader DIMACS.
        
        Args:
            data_dir: Diretório para armazenar os arquivos DIMACS
        """
        self.data_dir = data_dir
        self.base_url = "https://iridia.ulb.ac.be/~fmascia/files/graphs"
        
        # Criar diretório se não existir
        os.makedirs(data_dir, exist_ok=True)
        
        # Lista de grafos DIMACS disponíveis com suas características
        self.available_graphs = {
            # Grafos pequenos para teste
            "brock200_1": {"url": "brock200_1.clq.gz", "size": 200, "known_clique": 21},
            "brock200_2": {"url": "brock200_2.clq.gz", "size": 200, "known_clique": 12},
            "brock200_3": {"url": "brock200_3.clq.gz", "size": 200, "known_clique": 15},
            "brock200_4": {"url": "brock200_4.clq.gz", "size": 200, "known_clique": 17},
            
            # Grafos médios
            "brock400_1": {"url": "brock400_1.clq.gz", "size": 400, "known_clique": 27},
            "brock400_2": {"url": "brock400_2.clq.gz", "size": 400, "known_clique": 29},
            "brock400_3": {"url": "brock400_3.clq.gz", "size": 400, "known_clique": 31},
            "brock400_4": {"url": "brock400_4.clq.gz", "size": 400, "known_clique": 33},
            
            # Grafos C-family
            "C125.9": {"url": "C125.9.clq.gz", "size": 125, "known_clique": 34},
            "C250.9": {"url": "C250.9.clq.gz", "size": 250, "known_clique": 44},
            "C500.9": {"url": "C500.9.clq.gz", "size": 500, "known_clique": 57},
            
            # Grafos DSJC
            "DSJC125.1": {"url": "DSJC125.1.clq.gz", "size": 125, "known_clique": 34},
            "DSJC125.5": {"url": "DSJC125.5.clq.gz", "size": 125, "known_clique": 17},
            "DSJC125.9": {"url": "DSJC125.9.clq.gz", "size": 125, "known_clique": 44},
            
            # Grafos gen
            "gen200_p0.9_44": {"url": "gen200_p0.9_44.clq.gz", "size": 200, "known_clique": 44},
            "gen200_p0.9_55": {"url": "gen200_p0.9_55.clq.gz", "size": 200, "known_clique": 55},
            "gen400_p0.9_55": {"url": "gen400_p0.9_55.clq.gz", "size": 400, "known_clique": 55},
            "gen400_p0.9_65": {"url": "gen400_p0.9_65.clq.gz", "size": 400, "known_clique": 65},
            "gen400_p0.9_75": {"url": "gen400_p0.9_75.clq.gz", "size": 400, "known_clique": 75},
            
            # Grafos hamming
            "hamming8-4": {"url": "hamming8-4.clq.gz", "size": 256, "known_clique": 16},
            "hamming10-4": {"url": "hamming10-4.clq.gz", "size": 1024, "known_clique": 40},
            
            # Grafos johnson
            "johnson16-2-4": {"url": "johnson16-2-4.clq.gz", "size": 120, "known_clique": 8},
            "johnson32-2-4": {"url": "johnson32-2-4.clq.gz", "size": 496, "known_clique": 16},
            
            # Grafos keller
            "keller4": {"url": "keller4.clq.gz", "size": 171, "known_clique": 11},
            "keller5": {"url": "keller5.clq.gz", "size": 776, "known_clique": 27},
            
            # Grafos MANN
            "MANN_a27": {"url": "MANN_a27.clq.gz", "size": 378, "known_clique": 126},
            "MANN_a45": {"url": "MANN_a45.clq.gz", "size": 1035, "known_clique": 345},
            
            # Grafos p_hat
            "p_hat300-1": {"url": "p_hat300-1.clq.gz", "size": 300, "known_clique": 8},
            "p_hat300-2": {"url": "p_hat300-2.clq.gz", "size": 300, "known_clique": 25},
            "p_hat300-3": {"url": "p_hat300-3.clq.gz", "size": 300, "known_clique": 36},
            
            # Grafos san
            "san200_0.7_1": {"url": "san200_0.7_1.clq.gz", "size": 200, "known_clique": 30},
            "san200_0.7_2": {"url": "san200_0.7_2.clq.gz", "size": 200, "known_clique": 18},
            "san200_0.9_1": {"url": "san200_0.9_1.clq.gz", "size": 200, "known_clique": 70},
            "san200_0.9_2": {"url": "san200_0.9_2.clq.gz", "size": 200, "known_clique": 60},
            "san200_0.9_3": {"url": "san200_0.9_3.clq.gz", "size": 200, "known_clique": 44},
            
            "san400_0.5_1": {"url": "san400_0.5_1.clq.gz", "size": 400, "known_clique": 13},
            "san400_0.7_1": {"url": "san400_0.7_1.clq.gz", "size": 400, "known_clique": 40},
            "san400_0.7_2": {"url": "san400_0.7_2.clq.gz", "size": 400, "known_clique": 30},
            "san400_0.7_3": {"url": "san400_0.7_3.clq.gz", "size": 400, "known_clique": 22},
            "san400_0.9_1": {"url": "san400_0.9_1.clq.gz", "size": 400, "known_clique": 100},
        }
    
    def download_graph(self, graph_name: str) -> bool:
        """
        Baixar um grafo específico da base DIMACS.
        
        Args:
            graph_name: Nome do grafo a ser baixado
            
        Returns:
            True se o download foi bem-sucedido, False caso contrário
        """
        if graph_name not in self.available_graphs:
            logger.error(f"Grafo {graph_name} não está disponível.")
            return False
        
        graph_info = self.available_graphs[graph_name]
        url = f"{self.base_url}/{graph_info['url']}"
        
        # Nome do arquivo local
        local_file = os.path.join(self.data_dir, f"{graph_name}.clq")
        local_file_gz = os.path.join(self.data_dir, f"{graph_name}.clq.gz")
        
        # Verificar se já existe
        if os.path.exists(local_file):
            logger.info(f"Grafo {graph_name} já existe localmente.")
            return True
        
        try:
            logger.info(f"Baixando {graph_name} de {url}...")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            # Salvar arquivo comprimido
            with open(local_file_gz, 'wb') as f:
                f.write(response.content)
            
            # Descomprimir
            with gzip.open(local_file_gz, 'rb') as f_in:
                with open(local_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            
            # Remover arquivo comprimido
            os.remove(local_file_gz)
            
            logger.info(f"Grafo {graph_name} baixado com sucesso.")
            return True
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Erro ao baixar {graph_name}: {e}")
            return False
        except Exception as e:
            logger.error(f"Erro ao processar {graph_name}: {e}")
            return False
    
    def load_graph(self, graph_name: str) -> Optional[nx.Graph]:
        """
        Carregar um grafo DIMACS em formato NetworkX.
        
        Args:
            graph_name: Nome do grafo a ser carregado
            
        Returns:
            Grafo NetworkX ou None se erro
        """
        if graph_name not in self.available_graphs:
            logger.error(f"Grafo {graph_name} não está disponível.")
            return None
        
        local_file = os.path.join(self.data_dir, f"{graph_name}.clq")
        
        # Baixar se não existir
        if not os.path.exists(local_file):
            if not self.download_graph(graph_name):
                return None
        
        try:
            return self._parse_dimacs_file(local_file)
        except Exception as e:
            logger.error(f"Erro ao carregar {graph_name}: {e}")
            return None
    
    def _parse_dimacs_file(self, filepath: str) -> nx.Graph:
        """
        Fazer parsing de um arquivo DIMACS (.clq format).
        
        Args:
            filepath: Caminho para o arquivo DIMACS
            
        Returns:
            Grafo NetworkX
        """
        graph = nx.Graph()
        
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('c'):
                    # Ignorar comentários e linhas vazias
                    continue
                elif line.startswith('p'):
                    # Linha de problema: p edge <num_vertices> <num_edges>
                    parts = line.split()
                    if len(parts) >= 3:
                        num_vertices = int(parts[2])
                        # Adicionar vértices
                        graph.add_nodes_from(range(1, num_vertices + 1))
                elif line.startswith('e'):
                    # Linha de aresta: e <vertex1> <vertex2>
                    parts = line.split()
                    if len(parts) >= 3:
                        v1, v2 = int(parts[1]), int(parts[2])
                        graph.add_edge(v1, v2)
        
        return graph
    
    def get_graph_info(self, graph_name: str) -> Optional[Dict]:
        """
        Obter informações sobre um grafo.
        
        Args:
            graph_name: Nome do grafo
            
        Returns:
            Dicionário com informações do grafo ou None
        """
        return self.available_graphs.get(graph_name)
    
    def list_available_graphs(self) -> List[str]:
        """
        Listar todos os grafos disponíveis.
        
        Returns:
            Lista com nomes dos grafos disponíveis
        """
        return list(self.available_graphs.keys())
    
    def get_test_suite(self, max_size: Optional[int] = None) -> List[str]:
        """
        Obter uma suíte de testes adequada para benchmarking.
        
        Args:
            max_size: Tamanho máximo dos grafos (None para todos)
            
        Returns:
            Lista de nomes de grafos para teste
        """
        test_graphs = []
        
        for name, info in self.available_graphs.items():
            if max_size is None or info['size'] <= max_size:
                test_graphs.append(name)
        
        # Ordenar por tamanho
        test_graphs.sort(key=lambda x: self.available_graphs[x]['size'])
        
        return test_graphs
    
    def download_test_suite(self, max_size: Optional[int] = None) -> List[str]:
        """
        Baixar uma suíte completa de testes.
        
        Args:
            max_size: Tamanho máximo dos grafos
            
        Returns:
            Lista de grafos baixados com sucesso
        """
        test_graphs = self.get_test_suite(max_size)
        successful_downloads = []
        
        logger.info(f"Baixando {len(test_graphs)} grafos de teste...")
        
        for graph_name in test_graphs:
            if self.download_graph(graph_name):
                successful_downloads.append(graph_name)
        
        logger.info(f"Baixados {len(successful_downloads)} grafos com sucesso.")
        return successful_downloads


def main():
    """Função de teste do loader DIMACS."""
    loader = DIMACSLoader()
    
    # Listar grafos disponíveis
    print("Grafos DIMACS disponíveis:")
    for name in loader.list_available_graphs()[:10]:  # Primeiros 10
        info = loader.get_graph_info(name)
        print(f"  {name}: {info['size']} vértices, clique máximo conhecido: {info['known_clique']}")
    
    # Teste com um grafo pequeno
    test_graph = "brock200_1"
    print(f"\nTestando com {test_graph}...")
    
    graph = loader.load_graph(test_graph)
    if graph:
        print(f"Grafo carregado: {len(graph.nodes())} vértices, {len(graph.edges())} arestas")
        print(f"Densidade: {nx.density(graph):.3f}")
    else:
        print("Erro ao carregar grafo.")


if __name__ == "__main__":
    main()
