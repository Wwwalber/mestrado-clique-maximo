#!/usr/bin/env python3
"""
Teste forçado da estimativa de tempo para timeout

Este script força um timeout para demonstrar a funcionalidade
da estimativa de tempo em funcionamento.
"""

import sys
import os
import time
import networkx as nx

# Adicionar o diretório raiz ao path
sys.path.append('/home/cliSAT_project/mestrado-clique-maximo')

from algorithms.clisat_exact import CliSAT
from algorithms.grasp_heuristic import GRASPMaximumClique, GRASPParameters
from utils.timeout_estimator import TimeoutEstimator

def test_forced_timeout():
    """
    Força um timeout para demonstrar a estimativa funcionando.
    """
    print("🧪 TESTE FORÇADO: Demonstrando estimativa de tempo em timeout")
    print("="*70)
    
    # Criar um grafo mais complexo que force timeout
    print("📊 Criando grafo complexo para forçar timeout...")
    G = nx.erdos_renyi_graph(50, 0.3, seed=42)  # Grafo maior e mais esparso
    
    print(f"Grafo criado: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
    print()
    
    # Teste 1: CliSAT com timeout baixo
    print("🔍 TESTE 1: CliSAT com timeout baixo")
    print("-" * 40)
    
    clisat = CliSAT(G, time_limit=5.0)  # 5 segundos
    
    print(f"Configuração: Timeout = {clisat.time_limit}s")
    print("Executando...")
    
    start_time = time.time()
    clique, size = clisat.solve()
    total_time = time.time() - start_time
    
    print(f"\nResultado:")
    print(f"  Tempo real: {total_time:.2f}s")
    print(f"  Clique encontrado: {size} vértices")
    
    if hasattr(clisat, 'timeout_estimate') and clisat.timeout_estimate:
        print(f"  ✅ ESTIMATIVA GERADA!")
        estimate = clisat.timeout_estimate
        print(f"  📊 Dados da estimativa:")
        print(f"     - Tempo estimado total: {estimate['estimated_total_time']:.2f}s")
        print(f"     - Tempo restante estimado: {estimate['estimated_remaining_time']:.2f}s")
        print(f"     - Nós explorados: {estimate['nodes_explored']:,}")
        print(f"     - Taxa de exploração: {estimate['exploration_rate']:.2f} nós/s")
    else:
        print(f"  ❌ Estimativa não foi gerada (algoritmo muito rápido)")
    
    print()
    
    # Teste 2: GRASP com timeout baixo e muitas iterações
    print("🔍 TESTE 2: GRASP com timeout baixo")
    print("-" * 40)
    
    params = GRASPParameters(
        max_iterations=100000,  # Muitas iterações
        time_limit=3.0,         # 3 segundos
        alpha=0.2
    )
    
    grasp = GRASPMaximumClique(G, params)
    
    print(f"Configuração: Timeout = {params.time_limit}s, Max iter = {params.max_iterations:,}")
    print("Executando...")
    
    clique, size, exec_time = grasp.solve()
    
    print(f"\nResultado:")
    print(f"  Tempo real: {exec_time:.2f}s")
    print(f"  Clique encontrado: {size} vértices")
    
    if hasattr(grasp, 'timeout_estimate') and grasp.timeout_estimate:
        print(f"  ✅ ESTIMATIVA GERADA!")
        estimate = grasp.timeout_estimate
        print(f"  📊 Dados da estimativa:")
        print(f"     - Tempo estimado total: {estimate['estimated_total_time']:.2f}s")
        print(f"     - Tempo restante estimado: {estimate['estimated_remaining_time']:.2f}s")
        print(f"     - Iterações restantes: {estimate['remaining_iterations']:,}")
        print(f"     - Taxa de progresso: {estimate['iteration_rate']:.2f} iter/s")
        print(f"     - Progresso: {estimate['progress_percentage']:.1f}%")
    else:
        print(f"  ❌ Estimativa não foi gerada (algoritmo muito rápido)")
    
    print()
    print("🎯 CONCLUSÃO:")
    print("Se as estimativas foram geradas, a funcionalidade está funcionando!")
    print("As estimativas são baseadas no progresso real dos algoritmos.")

if __name__ == "__main__":
    test_forced_timeout()
    """
    Testa a estimativa de tempo para timeout no CliSAT.
    """
    print("🧪 TESTE: Estimativa de tempo - CliSAT")
    print("="*50)
    
    # Criar um grafo maior para forçar timeout
    G = nx.erdos_renyi_graph(50, 0.7, seed=42)
    
    # Configurar CliSAT com timeout baixo
    clisat = CliSAT(G, time_limit=3.0)  # 3 segundos
    
    print(f"Grafo: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
    print(f"Tempo limite: {clisat.time_limit}s")
    print()
    
    # Executar (deve dar timeout)
    start_time = time.time()
    clique, size = clisat.solve()
    total_time = time.time() - start_time
    
    print(f"\n✅ Resultado:")
    print(f"   Clique encontrado: {size} vértices")
    print(f"   Tempo real: {total_time:.2f}s")
    
    # Verificar se a estimativa foi gerada
    if hasattr(clisat, 'timeout_estimate') and clisat.timeout_estimate:
        print(f"   ✅ Estimativa gerada com sucesso!")
        estimate = clisat.timeout_estimate
        print(f"   Tempo estimado: {estimate.get('estimated_total_time', 'N/A'):.2f}s")
        print(f"   Método: {estimate.get('calculation_method', 'N/A')}")
        return True
    else:
        print(f"   ❌ Estimativa não foi gerada (algoritmo não atingiu timeout)")
        return False

def test_grasp_timeout_estimation():
    """
    Testa a estimativa de tempo para timeout no GRASP.
    """
    print("\n🧪 TESTE: Estimativa de tempo - GRASP")
    print("="*50)
    
    # Criar um grafo maior para forçar timeout
    G = nx.erdos_renyi_graph(100, 0.5, seed=42)
    
    # Configurar GRASP com timeout baixo e muitas iterações
    params = GRASPParameters(
        max_iterations=100000,  # Muitas iterações
        time_limit=2.0,  # 2 segundos
        alpha=0.3
    )
    
    grasp = GRASPMaximumClique(G, params)
    
    print(f"Grafo: {G.number_of_nodes()} nós, {G.number_of_edges()} arestas")
    print(f"Tempo limite: {params.time_limit}s")
    print(f"Max iterações: {params.max_iterations}")
    print()
    
    # Executar (deve dar timeout)
    start_time = time.time()
    clique, size, exec_time = grasp.solve()
    
    print(f"\n✅ Resultado:")
    print(f"   Clique encontrado: {size} vértices")
    print(f"   Tempo real: {exec_time:.2f}s")
    
    # Verificar se a estimativa foi gerada
    if hasattr(grasp, 'timeout_estimate') and grasp.timeout_estimate:
        print(f"   ✅ Estimativa gerada com sucesso!")
        estimate = grasp.timeout_estimate
        print(f"   Tempo estimado: {estimate.get('estimated_total_time', 'N/A'):.2f}s")
        print(f"   Método: {estimate.get('calculation_method', 'N/A')}")
        return True
    else:
        print(f"   ❌ Estimativa não foi gerada (algoritmo não atingiu timeout)")
        return False

def test_estimator_formatting():
    """
    Testa a formatação da estimativa.
    """
    print("\n🧪 TESTE: Formatação da estimativa")
    print("="*50)
    
    # Criar dados de exemplo
    estimate_data = {
        'estimated_total_time': 1234.5,
        'estimated_remaining_time': 890.3,
        'current_time': 344.2,
        'exploration_rate': 156.7,
        'nodes_explored': 53890,
        'calculation_method': 'Baseado na taxa de exploração de nós da árvore de busca',
        'explanation': 'Taxa atual: 156.7 nós/s. Espaço restante estimado: 139,567 nós'
    }
    
    formatted = TimeoutEstimator.format_time_estimate(estimate_data)
    print(formatted)
    
    return True

def main():
    """
    Executar todos os testes.
    """
    print("🚀 INICIANDO TESTES DA ESTIMATIVA DE TEMPO (VERSÃO GRAFO MAIOR)")
    print("="*70)
    
    # Teste 1: Formatação
    format_ok = test_estimator_formatting()
    
    # Teste 2: CliSAT com timeout
    clisat_ok = test_clisat_timeout_estimation()
    
    # Teste 3: GRASP com timeout
    grasp_ok = test_grasp_timeout_estimation()
    
    # Resumo
    print("\n🏁 RESUMO DOS TESTES")
    print("="*70)
    print(f"✅ Formatação: OK")
    print(f"{'✅' if clisat_ok else '❌'} CliSAT timeout: {'OK' if clisat_ok else 'FALHOU'}")
    print(f"{'✅' if grasp_ok else '❌'} GRASP timeout: {'OK' if grasp_ok else 'FALHOU'}")
    
    if clisat_ok and grasp_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("A estimativa de tempo está funcionando corretamente.")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM!")
        print("Verifique se os algoritmos estão atingindo o timeout.")

if __name__ == "__main__":
    main()
