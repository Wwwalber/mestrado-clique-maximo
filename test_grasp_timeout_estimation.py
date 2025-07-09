#!/usr/bin/env python3
"""
Teste específico para verificar a estimativa de timeout no GRASP.
"""

import sys
from pathlib import Path
import time

# Adicionar diretório raiz do projeto ao path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from algorithms.algorithm_interface import solve_maximum_clique_heuristic_with_stats
from data.dimacs_loader import DIMACSLoader


def test_timeout_estimation():
    """Testar estimativa de timeout."""
    print("🧪 TESTE ESPECÍFICO: Estimativa de Timeout no GRASP")
    print("=" * 60)
    
    loader = DIMACSLoader()
    
    # Testar com instâncias de diferentes tamanhos
    test_instances = [
        ('brock200_2', 1.0),   # Pequena, timeout baixo
        ('brock400_2', 2.0),   # Média, timeout baixo  
        ('C125.9', 0.8),       # Pequena, timeout muito baixo
    ]
    
    for instance_name, timeout in test_instances:
        print(f"\n📊 Testando {instance_name} com timeout {timeout}s")
        print("-" * 40)
        
        graph = loader.load_graph(instance_name)
        if graph is None:
            print(f"❌ Não foi possível carregar {instance_name}")
            continue
            
        print(f"   Grafo: {graph.number_of_nodes()} vértices, {graph.number_of_edges()} arestas")
        
        try:
            clique, size, exec_time, stats = solve_maximum_clique_heuristic_with_stats(
                graph, 
                alpha=0.3, 
                max_iterations=2000, 
                time_limit=timeout
            )
            
            print(f"✅ Resultado: clique {size} em {exec_time:.3f}s")
            print(f"   Iterações: {stats.get('total_iterations', 'N/A')}")
            
            if 'timeout_estimate' in stats:
                est = stats['timeout_estimate']
                print(f"🎯 ESTIMATIVA GERADA:")
                print(f"   Total estimado: {est.get('estimated_total_time', 'N/A'):.1f}s")
                print(f"   Restante: {est.get('estimated_remaining_time', 'N/A'):.1f}s")
                print(f"   Taxa: {est.get('iteration_rate', 'N/A'):.2f} iter/s")
                print(f"   Progresso: {est.get('progress_percentage', 'N/A'):.1f}%")
                print(f"   Método: {est.get('calculation_method', 'N/A')}")
            else:
                print("ℹ️ Nenhuma estimativa gerada (terminou dentro do tempo)")
                
        except Exception as e:
            print(f"❌ Erro: {e}")
    
    print("\n🏁 Teste de estimativa concluído!")


if __name__ == "__main__":
    test_timeout_estimation()
