"""
Módulo para carregar e gerenciar instâncias DIMACS específicas da atividade APA.

Este módulo é especializado para trabalhar com as instâncias selecionadas
para a disciplina de Análise e Projeto de Algoritmos do mestrado.
"""

import os
import requests
import pandas as pd
from pathlib import Path
import networkx as nx
from typing import List, Dict, Optional, Tuple
import logging

logger = logging.getLogger(__name__)


class APAInstanceManager:
    """Gerenciador para as instâncias específicas da atividade APA."""
    
    BASE_URL = "https://iridia.ulb.ac.be/~fmascia/maximum_clique/DIMACS-benchmark"
    
    def __init__(self, data_dir: str = "dimacs_data"):
        """
        Inicializar gerenciador de instâncias APA.
        
        Args:
            data_dir: Diretório para armazenar os arquivos DIMACS
        """
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(exist_ok=True)
        
        # Carregar lista de instâncias
        csv_path = Path(__file__).parent / "instances_apa.csv"
        self.instances_df = pd.read_csv(csv_path)
        
        # Criar dicionário para acesso rápido
        self.instances_info = {}
        for _, row in self.instances_df.iterrows():
            self.instances_info[row['Instance']] = {
                'nodes': row['Nodes'],
                'edges': row['Edges'],
                'density': (2 * row['Edges']) / (row['Nodes'] * (row['Nodes'] - 1))
            }
    
    def list_instances(self, max_nodes: Optional[int] = None, 
                      min_nodes: Optional[int] = None) -> List[str]:
        """
        Listar instâncias disponíveis com filtros opcionais.
        
        Args:
            max_nodes: Número máximo de nós
            min_nodes: Número mínimo de nós
            
        Returns:
            Lista de nomes de instâncias
        """
        filtered_df = self.instances_df.copy()
        
        if max_nodes is not None:
            filtered_df = filtered_df[filtered_df['Nodes'] <= max_nodes]
        if min_nodes is not None:
            filtered_df = filtered_df[filtered_df['Nodes'] >= min_nodes]
        
        return filtered_df['Instance'].tolist()
    
    def get_instance_info(self, instance_name: str) -> Dict:
        """
        Obter informações sobre uma instância específica.
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            Dicionário com informações da instância
        """
        if instance_name not in self.instances_info:
            raise ValueError(f"Instância '{instance_name}' não encontrada na lista APA")
        
        return self.instances_info[instance_name].copy()
    
    def download_instance(self, instance_name: str) -> bool:
        """
        Baixar uma instância específica do repositório DIMACS.
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            True se sucesso, False caso contrário
        """
        if instance_name not in self.instances_info:
            logger.error(f"Instância {instance_name} não encontrada na lista APA")
            return False
        
        # Buscar URL correto no CSV
        instance_row = self.instances_df[self.instances_df['Instance'] == instance_name]
        if instance_row.empty:
            logger.error(f"URL não encontrado para {instance_name}")
            return False
        
        url = instance_row.iloc[0]['link']
        file_path = self.data_dir / f"{instance_name}.clq"
        
        # Verificar se já existe
        if file_path.exists():
            logger.info(f"Arquivo {instance_name}.clq já existe")
            return True
        
        try:
            logger.info(f"Baixando {instance_name} de {url}")
            response = requests.get(url, timeout=30)
            response.raise_for_status()
            
            with open(file_path, 'w') as f:
                f.write(response.text)
            
            logger.info(f"Instância {instance_name} baixada com sucesso")
            return True
            
        except Exception as e:
            logger.error(f"Erro ao baixar {instance_name}: {e}")
            return False
    
    def load_graph(self, instance_name: str, auto_download: bool = True) -> nx.Graph:
        """
        Carregar grafo de uma instância DIMACS.
        
        Args:
            instance_name: Nome da instância
            auto_download: Baixar automaticamente se não existir
            
        Returns:
            Grafo NetworkX
        """
        file_path = self.data_dir / f"{instance_name}.clq"
        
        if not file_path.exists():
            if auto_download:
                self.download_instance(instance_name)
            else:
                raise FileNotFoundError(f"Arquivo {instance_name}.clq não encontrado")
        
        return self._parse_dimacs_file(file_path)
    
    def load_instance(self, instance_name: str) -> Optional[nx.Graph]:
        """
        Carregar uma instância específica como grafo NetworkX.
        
        Args:
            instance_name: Nome da instância (ex: 'C125.9')
            
        Returns:
            Grafo NetworkX ou None se erro
        """
        if instance_name not in self.instances_info:
            logger.error(f"Instância {instance_name} não está na lista da atividade APA")
            return None
        
        file_path = self.data_dir / f"{instance_name}.clq"
        
        # Baixar se não existir
        if not file_path.exists():
            logger.info(f"Baixando instância {instance_name}...")
            if not self.download_instance(instance_name):
                logger.error(f"Falha ao baixar {instance_name}")
                return None
        
        # Carregar grafo
        try:
            return self._parse_dimacs_file(file_path)
        except Exception as e:
            logger.error(f"Erro ao carregar {instance_name}: {e}")
            return None
    
    def _parse_dimacs_file(self, file_path: Path) -> nx.Graph:
        """
        Parsear arquivo DIMACS e criar grafo NetworkX.
        
        Args:
            file_path: Caminho para o arquivo .clq
            
        Returns:
            Grafo NetworkX
        """
        G = nx.Graph()
        
        with open(file_path, 'r') as f:
            for line in f:
                line = line.strip()
                
                if line.startswith('p edge'):
                    # Linha de problema: p edge n m
                    parts = line.split()
                    n_vertices = int(parts[2])
                    G.add_nodes_from(range(1, n_vertices + 1))
                    
                elif line.startswith('e'):
                    # Linha de aresta: e u v
                    parts = line.split()
                    u, v = int(parts[1]), int(parts[2])
                    G.add_edge(u, v)
        
        return G
    
    def get_statistics(self) -> pd.DataFrame:
        """
        Obter estatísticas das instâncias APA.
        
        Returns:
            DataFrame com estatísticas
        """
        stats_df = self.instances_df.copy()
        
        # Adicionar densidade
        stats_df['Density'] = (2 * stats_df['Edges']) / (stats_df['Nodes'] * (stats_df['Nodes'] - 1))
        
        # Adicionar categoria de tamanho
        def categorize_size(nodes):
            if nodes <= 200:
                return 'Pequeno'
            elif nodes <= 500:
                return 'Médio'
            elif nodes <= 1000:
                return 'Grande'
            else:
                return 'Muito Grande'
        
        stats_df['Size_Category'] = stats_df['Nodes'].apply(categorize_size)
        
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
        
        stats_df['Family'] = stats_df['Instance'].apply(get_family)
        
        return stats_df
    
    def download_all_instances(self, max_nodes: Optional[int] = None, 
                              force: bool = False) -> List[str]:
        """
        Baixar todas as instâncias (ou filtradas por tamanho).
        
        Args:
            max_nodes: Número máximo de nós para filtrar
            force: Forçar download mesmo se arquivos já existirem
            
        Returns:
            Lista de instâncias baixadas com sucesso
        """
        instances = self.list_instances(max_nodes=max_nodes)
        downloaded = []
        failed = []
        
        for instance in instances:
            try:
                self.download_instance(instance, force=force)
                downloaded.append(instance)
                logger.info(f"✓ {instance} baixado com sucesso")
            except Exception as e:
                failed.append(instance)
                logger.error(f"✗ Falha ao baixar {instance}: {e}")
        
        logger.info(f"Download concluído: {len(downloaded)} sucessos, {len(failed)} falhas")
        
        if failed:
            logger.warning(f"Instâncias que falharam: {failed}")
        
        return downloaded
    

    
    def print_summary(self):
        """Imprimir resumo das instâncias APA."""
        stats_df = self.get_statistics()
        
        print("=== RESUMO DAS INSTÂNCIAS APA ===")
        print(f"Total de instâncias: {len(stats_df)}")
        print()
        
        print("Distribuição por tamanho:")
        size_dist = stats_df['Size_Category'].value_counts().sort_index()
        for category, count in size_dist.items():
            print(f"  {category}: {count}")
        print()
        
        print("Distribuição por família:")
        family_dist = stats_df['Family'].value_counts()
        for family, count in family_dist.items():
            print(f"  {family}: {count}")
        print()
        
        print("Estatísticas gerais:")
        print(f"  Nós: {stats_df['Nodes'].min()} - {stats_df['Nodes'].max()}")
        print(f"  Arestas: {stats_df['Edges'].min():,} - {stats_df['Edges'].max():,}")
        print(f"  Densidade: {stats_df['Density'].min():.3f} - {stats_df['Density'].max():.3f}")
        print()
        
        print("Top 5 maiores instâncias:")
        top5 = stats_df.nlargest(5, 'Nodes')[['Instance', 'Nodes', 'Edges', 'Density']]
        for _, row in top5.iterrows():
            print(f"  {row['Instance']}: {row['Nodes']} nós, {row['Edges']:,} arestas, "
                  f"densidade {row['Density']:.3f}")
    
    def get_apa_instance_list(self) -> List[str]:
        """
        Obter lista completa de instâncias da atividade APA.
        
        Returns:
            Lista com nomes de todas as 38 instâncias
        """
        return self.instances_df['Instance'].tolist()
    
    def get_known_clique_size(self, instance_name: str) -> Optional[int]:
        """
        Obter tamanho do clique ótimo conhecido para uma instância.
        
        Args:
            instance_name: Nome da instância
            
        Returns:
            Tamanho do clique ótimo conhecido ou None se não conhecido
        """
        # Valores ótimos conhecidos das instâncias DIMACS
        known_optima = {
            'C125.9': 34,
            'C250.9': 44, 
            'C500.9': 57,
            'C1000.9': 68,
            'C2000.9': 80,
            'C2000.5': 16,
            'C4000.5': 18,
            'DSJC500_5': 13,
            'DSJC1000_5': 15,
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
            'hamming8-4': 16,
            'hamming10-4': 40,
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
        
        return known_optima.get(instance_name)

def main():
    """Função principal para demonstração."""
    manager = APAInstanceManager()
    
    # Imprimir resumo
    manager.print_summary()
    
    # Listar instâncias pequenas
    print("\n=== INSTÂNCIAS PEQUENAS (≤ 300 nós) ===")
    small_instances = manager.list_instances(max_nodes=300)
    for instance in small_instances:
        info = manager.get_instance_info(instance)
        print(f"{instance}: {info['nodes']} nós, densidade {info['density']:.3f}")
    
    # Exemplo de carregamento
    print("\n=== EXEMPLO DE CARREGAMENTO ===")
    try:
        # Carregar uma instância pequena
        print("Carregando C125.9...")
        graph = manager.load_graph("C125.9")
        print(f"Grafo carregado: {len(graph.nodes())} nós, {len(graph.edges())} arestas")
        print(f"Densidade: {nx.density(graph):.3f}")
    except Exception as e:
        print(f"Erro ao carregar grafo: {e}")


if __name__ == "__main__":
    main()
