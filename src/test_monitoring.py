#!/usr/bin/env python3
"""
Teste dos diferentes modos de monitoramento com instância DIMACS real
"""

import networkx as nx
from clisat_algortithmb import solve_maximum_clique_clisat
import time

def create_dimacs_like_graph():
    """
    Criar um grafo similar às instâncias DIMACS mas menor para demonstração.
    Baseado nas características das instâncias brock e gen.
    """
    import random
    random.seed(42)
    
    # Grafo com 50 vértices (muito menor que instâncias reais)
    n = 50
    G = nx.Graph()
    G.add_nodes_from(range(1, n+1))
    
    # Criar estrutura similar ao brock200: clique escondido + arestas aleatórias
    # Clique escondido de tamanho 12
    hidden_clique = random.sample(range(1, n+1), 12)
    
    # Conectar o clique escondido
    for i in hidden_clique:
        for j in hidden_clique:
            if i < j:
                G.add_edge(i, j)
    
    # Adicionar arestas aleatórias (densidade ~0.4)
    for i in range(1, n+1):
        for j in range(i+1, n+1):
            if not G.has_edge(i, j) and random.random() < 0.4:
                G.add_edge(i, j)
    
    return G, hidden_clique

def test_monitoring_modes():
    """Testar diferentes modos com uma instância DIMACS-like."""
    
    print("🧪 TESTE COM INSTÂNCIA SIMILAR AO DIMACS")
    print("=" * 60)
    
    # Criar grafo teste
    G, expected_clique = create_dimacs_like_graph()
    
    print(f"📊 Grafo criado:")
    print(f"   🔢 Vértices: {G.number_of_nodes()}")
    print(f"   🔗 Arestas: {G.number_of_edges()}")
    print(f"   📏 Densidade: {nx.density(G):.3f}")
    print(f"   🎯 Clique esperado: {len(expected_clique)} vértices")
    print()
    
    modes = [
        ('silent', "🤫 Silencioso"),
        ('log', "📝 Log Tradicional"), 
        ('realtime', "📊 Tempo Real"),
        ('both', "🔄 Híbrido")
    ]
    
    results = {}
    
    for mode, description in modes:
        print(f"\n{description}")
        print("-" * 40)
        
        start_time = time.time()
        
        try:
            clique, size = solve_maximum_clique_clisat(
                G,
                time_limit=15.0,      # 15 segundos para cada teste
                log_interval=10,      # Logs frequentes para demo
                time_interval=2.0,    # A cada 2 segundos
                monitor_mode=mode
            )
            
            execution_time = time.time() - start_time
            results[mode] = {
                'clique_size': size,
                'time': execution_time,
                'clique': clique
            }
            
            print(f"\n✅ Resultado: {size} vértices em {execution_time:.2f}s")
            
        except KeyboardInterrupt:
            print(f"\n⏹️  Interrompido pelo usuário")
            results[mode] = {'clique_size': 0, 'time': 0, 'clique': []}
        except Exception as e:
            print(f"\n❌ Erro: {e}")
            results[mode] = {'clique_size': 0, 'time': 0, 'clique': []}
        
        time.sleep(1)  # Pausa entre testes
    
    # Resumo final
    print(f"\n📋 RESUMO DOS RESULTADOS")
    print("=" * 60)
    print(f"{'Modo':<12} {'Clique':<8} {'Tempo':<8} {'Performance'}")
    print("-" * 60)
    
    for mode, description in modes:
        if mode in results:
            result = results[mode]
            size = result['clique_size']
            time_taken = result['time']
            
            # Calcular performance relativa
            if time_taken > 0:
                perf = f"{size/time_taken:.1f} v/s"
            else:
                perf = "N/A"
            
            print(f"{description:<12} {size:<8} {time_taken:<8.2f} {perf}")
    
    print("\n🎯 ANÁLISE:")
    print(f"   Expected clique size: {len(expected_clique)}")
    print(f"   Hidden clique: {sorted(expected_clique)[:10]}{'...' if len(expected_clique) > 10 else ''}")
    
    # Verificar qual modo encontrou o melhor resultado
    best_size = max(results.values(), key=lambda x: x['clique_size'])['clique_size']
    best_modes = [mode for mode, result in results.items() if result['clique_size'] == best_size]
    
    print(f"   Melhor resultado: {best_size} vértices")
    print(f"   Encontrado por: {', '.join(best_modes)}")

if __name__ == "__main__":
    test_monitoring_modes()
