"""
Exemplos de aplicações práticas do algoritmo CliSAT.
Demonstra como usar o CliSAT em cenários reais.
"""

import networkx as nx
import numpy as np
import random
from typing import List, Dict, Tuple
from clisat_algorithm import solve_maximum_clique_clisat
import json


class SocialNetworkAnalyzer:
    """
    Analisador de redes sociais usando CliSAT para encontrar grupos coesos.
    """
    
    def __init__(self):
        self.graph = nx.Graph()
        self.people = {}
    
    def add_person(self, person_id: str, name: str, attributes: Dict = None):
        """Adicionar pessoa à rede social."""
        self.graph.add_node(person_id)
        self.people[person_id] = {
            'name': name,
            'attributes': attributes or {}
        }
    
    def add_friendship(self, person1: str, person2: str, strength: float = 1.0):
        """Adicionar amizade entre duas pessoas."""
        self.graph.add_edge(person1, person2, weight=strength)
    
    def find_tight_friend_groups(self, min_size: int = 3) -> List[List[str]]:
        """
        Encontrar grupos de amigos onde todos se conhecem (cliques).
        
        Args:
            min_size: Tamanho mínimo do grupo
            
        Returns:
            Lista de grupos de amigos
        """
        # Encontrar clique máximo
        max_clique, size = solve_maximum_clique_clisat(self.graph, time_limit=300)
        
        groups = []
        if size >= min_size:
            groups.append(max_clique)
        
        # Encontrar outros cliques grandes usando algoritmo guloso
        remaining_nodes = set(self.graph.nodes()) - set(max_clique)
        
        while len(remaining_nodes) >= min_size:
            # Subgrafo com nós restantes
            subgraph = self.graph.subgraph(remaining_nodes)
            if len(subgraph.nodes()) < min_size:
                break
            
            # Encontrar clique no subgrafo
            clique, clique_size = solve_maximum_clique_clisat(subgraph, time_limit=60)
            
            if clique_size >= min_size:
                groups.append(clique)
                remaining_nodes -= set(clique)
            else:
                break
        
        return groups
    
    def analyze_groups(self, groups: List[List[str]]) -> Dict:
        """Analisar características dos grupos encontrados."""
        analysis = {
            'total_groups': len(groups),
            'group_sizes': [len(group) for group in groups],
            'groups_details': []
        }
        
        for i, group in enumerate(groups):
            group_info = {
                'group_id': i + 1,
                'size': len(group),
                'members': [self.people[person_id]['name'] for person_id in group],
                'member_ids': group
            }
            
            # Calcular densidade do grupo
            subgraph = self.graph.subgraph(group)
            group_info['density'] = nx.density(subgraph)
            
            # Calcular força média das conexões
            if 'weight' in nx.get_edge_attributes(subgraph, 'weight'):
                weights = [subgraph[u][v]['weight'] for u, v in subgraph.edges()]
                group_info['avg_connection_strength'] = np.mean(weights) if weights else 0
            
            analysis['groups_details'].append(group_info)
        
        return analysis


class ProteinInteractionAnalyzer:
    """
    Analisador de interações proteicas usando CliSAT para encontrar complexos.
    """
    
    def __init__(self):
        self.interaction_graph = nx.Graph()
        self.proteins = {}
    
    def add_protein(self, protein_id: str, name: str, function: str = None):
        """Adicionar proteína à rede."""
        self.interaction_graph.add_node(protein_id)
        self.proteins[protein_id] = {
            'name': name,
            'function': function
        }
    
    def add_interaction(self, protein1: str, protein2: str, confidence: float = 1.0):
        """Adicionar interação entre proteínas."""
        self.interaction_graph.add_edge(protein1, protein2, confidence=confidence)
    
    def find_protein_complexes(self, min_complex_size: int = 3) -> List[List[str]]:
        """
        Encontrar complexos proteicos (grupos onde todas as proteínas interagem).
        
        Args:
            min_complex_size: Tamanho mínimo do complexo
            
        Returns:
            Lista de complexos proteicos
        """
        # Filtrar interações com baixa confiança
        high_conf_graph = nx.Graph()
        for u, v, data in self.interaction_graph.edges(data=True):
            if data.get('confidence', 1.0) >= 0.5:  # Threshold de confiança
                high_conf_graph.add_edge(u, v)
        
        # Encontrar clique máximo
        max_clique, size = solve_maximum_clique_clisat(high_conf_graph, time_limit=600)
        
        complexes = []
        if size >= min_complex_size:
            complexes.append(max_clique)
        
        return complexes
    
    def analyze_complexes(self, complexes: List[List[str]]) -> Dict:
        """Analisar complexos proteicos encontrados."""
        analysis = {
            'total_complexes': len(complexes),
            'complex_sizes': [len(complex) for complex in complexes],
            'complexes_details': []
        }
        
        for i, complex_proteins in enumerate(complexes):
            complex_info = {
                'complex_id': i + 1,
                'size': len(complex_proteins),
                'proteins': [self.proteins[pid]['name'] for pid in complex_proteins],
                'protein_ids': complex_proteins
            }
            
            # Analisar funções das proteínas
            functions = [self.proteins[pid]['function'] for pid in complex_proteins 
                        if self.proteins[pid]['function']]
            complex_info['functions'] = list(set(functions))
            
            # Calcular confiança média das interações
            subgraph = self.interaction_graph.subgraph(complex_proteins)
            if subgraph.edges():
                confidences = [subgraph[u][v].get('confidence', 1.0) 
                             for u, v in subgraph.edges()]
                complex_info['avg_confidence'] = np.mean(confidences)
            
            analysis['complexes_details'].append(complex_info)
        
        return analysis


def create_example_social_network() -> SocialNetworkAnalyzer:
    """Criar exemplo de rede social para demonstração."""
    analyzer = SocialNetworkAnalyzer()
    
    # Adicionar pessoas
    people = [
        ('alice', 'Alice Silva', {'age': 25, 'city': 'São Paulo'}),
        ('bob', 'Bob Santos', {'age': 28, 'city': 'São Paulo'}),
        ('carol', 'Carol Oliveira', {'age': 26, 'city': 'São Paulo'}),
        ('david', 'David Lima', {'age': 27, 'city': 'Rio de Janeiro'}),
        ('eva', 'Eva Costa', {'age': 24, 'city': 'Rio de Janeiro'}),
        ('frank', 'Frank Pereira', {'age': 29, 'city': 'Rio de Janeiro'}),
        ('grace', 'Grace Martins', {'age': 25, 'city': 'Belo Horizonte'}),
        ('henry', 'Henry Rodrigues', {'age': 30, 'city': 'Belo Horizonte'}),
        ('iris', 'Iris Fernandes', {'age': 23, 'city': 'Belo Horizonte'})
    ]
    
    for person_id, name, attrs in people:
        analyzer.add_person(person_id, name, attrs)
    
    # Criar grupos de amigos (cliques)
    # Grupo 1: Alice, Bob, Carol, David (amigos da faculdade)
    group1 = ['alice', 'bob', 'carol', 'david']
    for i, person1 in enumerate(group1):
        for person2 in group1[i+1:]:
            analyzer.add_friendship(person1, person2, random.uniform(0.7, 1.0))
    
    # Grupo 2: Eva, Frank, Grace (colegas de trabalho)
    group2 = ['eva', 'frank', 'grace']
    for i, person1 in enumerate(group2):
        for person2 in group2[i+1:]:
            analyzer.add_friendship(person1, person2, random.uniform(0.6, 0.9))
    
    # Algumas conexões entre grupos
    analyzer.add_friendship('david', 'eva', 0.8)  # Primos
    analyzer.add_friendship('carol', 'grace', 0.5)  # Conhecidos
    analyzer.add_friendship('henry', 'iris', 0.9)  # Namorados
    
    return analyzer


def create_example_protein_network() -> ProteinInteractionAnalyzer:
    """Criar exemplo de rede de interação proteica."""
    analyzer = ProteinInteractionAnalyzer()
    
    # Adicionar proteínas
    proteins = [
        ('p53', 'Tumor Protein p53', 'Tumor Suppressor'),
        ('mdm2', 'Mouse Double Minute 2', 'Oncogene'),
        ('atm', 'ATM Kinase', 'DNA Damage Response'),
        ('chk2', 'Checkpoint Kinase 2', 'Cell Cycle Control'),
        ('brca1', 'BRCA1 DNA Repair', 'DNA Repair'),
        ('brca2', 'BRCA2 DNA Repair', 'DNA Repair'),
        ('rad51', 'RAD51 Recombinase', 'Homologous Recombination'),
        ('pcna', 'PCNA', 'DNA Replication')
    ]
    
    for protein_id, name, function in proteins:
        analyzer.add_protein(protein_id, name, function)
    
    # Adicionar interações conhecidas
    interactions = [
        ('p53', 'mdm2', 0.95),    # Interação bem conhecida
        ('p53', 'atm', 0.85),     # ATM fosforila p53
        ('p53', 'chk2', 0.75),    # Via de resposta a dano
        ('atm', 'chk2', 0.90),    # Via ATM-Chk2
        ('brca1', 'brca2', 0.80), # Complexo BRCA
        ('brca1', 'rad51', 0.85), # Reparo de DNA
        ('brca2', 'rad51', 0.88), # Reparo de DNA
        ('pcna', 'brca1', 0.70),  # Replicação e reparo
        ('atm', 'brca1', 0.75),   # Sinalização de dano
    ]
    
    for p1, p2, conf in interactions:
        analyzer.add_interaction(p1, p2, conf)
    
    return analyzer


def run_social_network_example():
    """Executar exemplo de análise de rede social."""
    print("=== Análise de Rede Social ===\n")
    
    analyzer = create_example_social_network()
    
    print(f"Rede criada com {len(analyzer.graph.nodes())} pessoas")
    print(f"Total de amizades: {len(analyzer.graph.edges())}")
    print(f"Densidade da rede: {nx.density(analyzer.graph):.3f}")
    
    # Encontrar grupos coesos
    print("\nEncontrando grupos de amigos...")
    groups = analyzer.find_tight_friend_groups(min_size=3)
    
    # Analisar grupos
    analysis = analyzer.analyze_groups(groups)
    
    print(f"\n=== Resultados ===")
    print(f"Grupos encontrados: {analysis['total_groups']}")
    print(f"Tamanhos dos grupos: {analysis['group_sizes']}")
    
    for group_detail in analysis['groups_details']:
        print(f"\nGrupo {group_detail['group_id']}:")
        print(f"  Tamanho: {group_detail['size']}")
        print(f"  Membros: {', '.join(group_detail['members'])}")
        print(f"  Densidade: {group_detail['density']:.3f}")
    
    return analysis


def run_protein_interaction_example():
    """Executar exemplo de análise de interação proteica."""
    print("\n=== Análise de Interação Proteica ===\n")
    
    analyzer = create_example_protein_network()
    
    print(f"Rede criada com {len(analyzer.interaction_graph.nodes())} proteínas")
    print(f"Total de interações: {len(analyzer.interaction_graph.edges())}")
    
    # Encontrar complexos proteicos
    print("\nEncontrando complexos proteicos...")
    complexes = analyzer.find_protein_complexes(min_complex_size=3)
    
    # Analisar complexos
    analysis = analyzer.analyze_complexes(complexes)
    
    print(f"\n=== Resultados ===")
    print(f"Complexos encontrados: {analysis['total_complexes']}")
    print(f"Tamanhos dos complexos: {analysis['complex_sizes']}")
    
    for complex_detail in analysis['complexes_details']:
        print(f"\nComplexo {complex_detail['complex_id']}:")
        print(f"  Tamanho: {complex_detail['size']}")
        print(f"  Proteínas: {', '.join(complex_detail['proteins'])}")
        print(f"  Funções: {', '.join(complex_detail['functions'])}")
        if 'avg_confidence' in complex_detail:
            print(f"  Confiança média: {complex_detail['avg_confidence']:.3f}")
    
    return analysis


def save_results_to_file(social_results: Dict, protein_results: Dict, filename: str = "clisat_results.json"):
    """Salvar resultados em arquivo JSON."""
    results = {
        'timestamp': time.time(),
        'social_network_analysis': social_results,
        'protein_interaction_analysis': protein_results
    }
    
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    print(f"\nResultados salvos em {filename}")


if __name__ == "__main__":
    import time
    
    print("=== Exemplos Práticos do CliSAT ===\n")
    
    # Executar exemplos
    social_results = run_social_network_example()
    protein_results = run_protein_interaction_example()
    
    # Salvar resultados
    save_results_to_file(social_results, protein_results)
    
    print("\n=== Exemplos Concluídos ===")
    print("Os exemplos demonstram como o CliSAT pode ser aplicado em:")
    print("1. Análise de redes sociais - encontrar grupos coesos de amigos")
    print("2. Bioinformática - identificar complexos proteicos")
    print("3. Qualquer domínio onde é necessário encontrar grupos totalmente conectados")
