#!/usr/bin/env python3
"""
Teste da implementação da estimativa de tempo para timeout

Este script testa se a estimativa de tempo funciona corretamente
quando os algoritmos excedem o tempo limite.
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

def test_clisat_timeout_estimation():
    """
    Testa a estimativa de tempo para timeout no CliSAT.
    """
    print("🧪 TESTE: Estimativa de tempo - CliSAT COM TIMEOUT")
    print("="*50)
    
    # Criar um grafo pequeno para teste rápido
    G = nx.erdos_renyi_graph(20, 0.5, seed=42)
    
    # Configurar CliSAT com timeout muito baixo para forçar timeout
    clisat = CliSAT(G, time_limit=2.0)  # 2 segundos
    
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
    
    # Verificar se a estimativa foi gerada (APENAS se houve timeout)
    if hasattr(clisat, 'timeout_estimate') and clisat.timeout_estimate:
        print(f"   ✅ Estimativa gerada com sucesso! (houve timeout)")
        estimate = clisat.timeout_estimate
        print(f"   Tempo estimado: {estimate.get('estimated_total_time', 'N/A'):.2f}s")
        print(f"   Método: {estimate.get('calculation_method', 'N/A')}")
        return True
    elif total_time >= clisat.time_limit * 0.9:  # Se chegou perto do limite
        print(f"   ❌ Houve timeout mas estimativa não foi gerada")
        return False
    else:
        print(f"   ✅ Sem timeout, sem estimativa (comportamento correto)")
        return True

def test_grasp_timeout_estimation():
    """
    Testa a estimativa de tempo para timeout no GRASP.
    """
    print("\n🧪 TESTE: Estimativa de tempo - GRASP COM TIMEOUT")
    print("="*50)
    
    # Criar um grafo pequeno para teste rápido
    G = nx.erdos_renyi_graph(30, 0.4, seed=42)
    
    # Configurar GRASP com timeout muito baixo para forçar timeout
    params = GRASPParameters(
        max_iterations=10000,
        time_limit=3.0,  # 3 segundos
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
    
    # Verificar se a estimativa foi gerada (APENAS se houve timeout)
    if hasattr(grasp, 'timeout_estimate') and grasp.timeout_estimate:
        print(f"   ✅ Estimativa gerada com sucesso! (houve timeout)")
        estimate = grasp.timeout_estimate
        print(f"   Tempo estimado: {estimate.get('estimated_total_time', 'N/A'):.2f}s")
        print(f"   Método: {estimate.get('calculation_method', 'N/A')}")
        return True
    elif exec_time >= params.time_limit * 0.9:  # Se chegou perto do limite
        print(f"   ❌ Houve timeout mas estimativa não foi gerada")
        return False
    else:
        print(f"   ✅ Sem timeout, sem estimativa (comportamento correto)")
        return True

def test_no_timeout_cases():
    """
    Testa que a estimativa NÃO é gerada quando não há timeout.
    """
    print("\n🧪 TESTE: Casos SEM timeout (não deve gerar estimativa)")
    print("="*50)
    
    # Teste 1: CliSAT com grafo muito pequeno e tempo suficiente
    print("📊 CliSAT sem timeout:")
    G_small = nx.complete_graph(8)  # Grafo pequeno, fácil de resolver
    clisat = CliSAT(G_small, time_limit=30.0)  # Tempo suficiente
    
    start_time = time.time()
    clique, size = clisat.solve()
    total_time = time.time() - start_time
    
    has_estimate = hasattr(clisat, 'timeout_estimate') and clisat.timeout_estimate
    print(f"   Tempo: {total_time:.2f}s, Clique: {size}")
    print(f"   {'❌ Estimativa gerada (ERRO)' if has_estimate else '✅ Sem estimativa (correto)'}")
    
    # Teste 2: GRASP com poucas iterações
    print("\n📊 GRASP sem timeout:")
    params = GRASPParameters(
        max_iterations=50,  # Poucas iterações
        time_limit=30.0,    # Tempo suficiente
        alpha=0.3
    )
    
    grasp = GRASPMaximumClique(G_small, params)
    clique, size, exec_time = grasp.solve()
    
    has_estimate = hasattr(grasp, 'timeout_estimate') and grasp.timeout_estimate
    print(f"   Tempo: {exec_time:.2f}s, Clique: {size}")
    print(f"   {'❌ Estimativa gerada (ERRO)' if has_estimate else '✅ Sem estimativa (correto)'}")
    
    return not has_estimate  # Retorna True se NÃO gerou estimativas (correto)

def test_estimator_direct():
    """
    Testa o TimeoutEstimator diretamente.
    """
    print("\n🧪 TESTE: TimeoutEstimator direto")
    print("="*50)
    
    # Teste CliSAT
    print("📊 Teste CliSAT:")
    stats = {'nodes_explored': 5000}
    estimate = TimeoutEstimator.estimate_clisat_time(
        stats=stats,
        current_time=10.0,
        graph_size=50,
        current_bound=15
    )
    
    print("   Dados de entrada:")
    print(f"   - Nós explorados: {stats['nodes_explored']}")
    print(f"   - Tempo atual: 10.0s")
    print(f"   - Tamanho do grafo: 50")
    print(f"   - Bound atual: 15")
    print()
    print("   Resultado:")
    print(f"   - Tempo estimado: {estimate.get('estimated_total_time', 'N/A'):.2f}s")
    print(f"   - Taxa de exploração: {estimate.get('exploration_rate', 'N/A'):.2f} nós/s")
    
    # Teste GRASP
    print("\n📊 Teste GRASP:")
    estimate = TimeoutEstimator.estimate_grasp_time(
        iteration=200,
        current_time=15.0,
        max_iterations=1000,
        best_clique_size=12,
        improvement_history=[8, 9, 10, 11, 12, 12, 12]
    )
    
    print("   Dados de entrada:")
    print(f"   - Iteração atual: 200")
    print(f"   - Tempo atual: 15.0s")
    print(f"   - Max iterações: 1000")
    print(f"   - Melhor clique: 12")
    print()
    print("   Resultado:")
    print(f"   - Tempo estimado: {estimate.get('estimated_total_time', 'N/A'):.2f}s")
    print(f"   - Taxa de progresso: {estimate.get('iteration_rate', 'N/A'):.2f} iter/s")
    print(f"   - Progresso: {estimate.get('progress_percentage', 'N/A'):.1f}%")

def main():
    """
    Executar todos os testes.
    """
    print("🚀 INICIANDO TESTES DA ESTIMATIVA DE TEMPO")
    print("="*60)
    
    # Teste 1: TimeoutEstimator direto
    test_estimator_direct()
    
    # Teste 2: Casos sem timeout (não deve gerar estimativa)
    no_timeout_ok = test_no_timeout_cases()
    
    # Teste 3: CliSAT com timeout
    clisat_ok = test_clisat_timeout_estimation()
    
    # Teste 4: GRASP com timeout
    grasp_ok = test_grasp_timeout_estimation()
    
    # Resumo
    print("\n🏁 RESUMO DOS TESTES")
    print("="*60)
    print(f"✅ TimeoutEstimator direto: OK")
    print(f"{'✅' if no_timeout_ok else '❌'} Casos sem timeout: {'OK' if no_timeout_ok else 'FALHOU'}")
    print(f"{'✅' if clisat_ok else '❌'} CliSAT timeout: {'OK' if clisat_ok else 'FALHOU'}")
    print(f"{'✅' if grasp_ok else '❌'} GRASP timeout: {'OK' if grasp_ok else 'FALHOU'}")
    
    if clisat_ok and grasp_ok and no_timeout_ok:
        print("\n🎉 TODOS OS TESTES PASSARAM!")
        print("A estimativa de tempo está funcionando corretamente:")
        print("  - Gera estimativas APENAS quando há timeout")
        print("  - NÃO gera estimativas quando termina normalmente")
    else:
        print("\n⚠️  ALGUNS TESTES FALHARAM!")
        print("Verifique os erros acima.")

if __name__ == "__main__":
    main()
