#!/usr/bin/env python3
"""
Script de Teste Rápido da Estratégia CliSAT

Este script executa um teste rápido da estratégia em algumas instâncias pequenas
para verificar se tudo está funcionando corretamente antes da execução completa.

Autor: Walber
Data: Julho 2025
"""

import sys
import time
from pathlib import Path

# Adicionar src ao path
sys.path.append(str(Path(__file__).parent / "src"))

from execute_clisat_strategy import CliSATExecutionStrategy
import logging

# Configurar logging mais detalhado
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def test_quick_execution():
    """
    Teste rápido com instâncias pequenas.
    """
    print("🚀 TESTE RÁPIDO DA ESTRATÉGIA CLISAT")
    print("="*50)
    
    # Criar estratégia de teste
    strategy = CliSATExecutionStrategy()
    
    # Definir instâncias de teste (pequenas e rápidas)
    test_instances = ['C125.9', 'brock200_2', 'keller4']
    test_time_limit = 1800  # 30 minutos por instância
    
    print(f"Testando {len(test_instances)} instâncias pequenas:")
    for inst in test_instances:
        print(f"  • {inst}")
    print(f"Tempo limite: {test_time_limit}s por instância")
    print()
    
    results = []
    total_start = time.time()
    
    for i, instance_name in enumerate(test_instances, 1):
        print(f"[{i}/{len(test_instances)}] Testando {instance_name}...")
        
        result = strategy.run_single_instance(instance_name, test_time_limit)
        results.append(result)
        
        if result['status'] == 'SUCCESS':
            print(f"  ✅ Sucesso: clique {result['clique_size']} em {result['execution_time']:.2f}s")
        else:
            print(f"  ❌ Erro: {result.get('error', 'Erro desconhecido')}")
        print()
    
    total_time = time.time() - total_start
    
    # Resumo do teste
    successful = [r for r in results if r['status'] == 'SUCCESS']
    
    print("="*50)
    print("RESUMO DO TESTE:")
    print(f"  • Instâncias testadas: {len(results)}")
    print(f"  • Sucessos: {len(successful)}/{len(results)}")
    print(f"  • Tempo total: {total_time:.2f}s")
    
    if successful:
        avg_time = sum(r['execution_time'] for r in successful) / len(successful)
        avg_clique = sum(r['clique_size'] for r in successful) / len(successful)
        print(f"  • Tempo médio: {avg_time:.2f}s")
        print(f"  • Clique médio: {avg_clique:.1f}")
    
    print()
    
    if len(successful) == len(results):
        print("🎉 TESTE CONCLUÍDO COM SUCESSO!")
        print("A estratégia está funcionando corretamente.")
        print("Use o script principal para execução completa:")
        print("  python execute_clisat_strategy.py --all")
    else:
        print("⚠️  ALGUNS TESTES FALHARAM")
        print("Verifique os erros acima antes da execução completa.")
    
    return len(successful) == len(results)


def test_strategy_structure():
    """
    Testar a estrutura da estratégia.
    """
    print("🔍 TESTANDO ESTRUTURA DA ESTRATÉGIA")
    print("="*40)
    
    strategy = CliSATExecutionStrategy()
    
    # Verificar grupos
    print("Grupos definidos:")
    for group_name, group_info in strategy.instance_groups.items():
        print(f"  • {group_name}: {len(group_info['instances'])} instâncias")
    
    print()
    
    # Verificar diretórios
    print("Diretórios:")
    print(f"  • Base: {strategy.base_dir}")
    print(f"  • Resultados: {strategy.results_dir}")
    print(f"  • Checkpoint: {strategy.checkpoint_file}")
    
    print()
    
    # Verificar total de instâncias
    total_instances = sum(len(group['instances']) for group in strategy.instance_groups.values())
    print(f"Total de instâncias: {total_instances}")
    
    # Verificar se há duplicatas
    all_instances = []
    for group in strategy.instance_groups.values():
        all_instances.extend(group['instances'])
    
    unique_instances = set(all_instances)
    if len(unique_instances) != len(all_instances):
        print(f"⚠️  ATENÇÃO: {len(all_instances) - len(unique_instances)} instâncias duplicadas encontradas")
    else:
        print("✅ Nenhuma duplicata encontrada")
    
    print()
    return True


def main():
    """
    Função principal do teste.
    """
    print("TESTE DA ESTRATÉGIA DE EXECUÇÃO DO CLISAT")
    print("="*60)
    print()
    
    try:
        # Testar estrutura
        if not test_strategy_structure():
            print("❌ Erro na estrutura da estratégia")
            return
        
        print()
        
        # Perguntar se deve executar teste prático
        response = input("Executar teste prático com instâncias pequenas? (s/n): ").lower()
        if response in ['s', 'sim', 'y', 'yes']:
            print()
            if test_quick_execution():
                print("\n🎯 PRÓXIMOS PASSOS:")
                print("1. Para execução completa:")
                print("   python execute_clisat_strategy.py --all")
                print()
                print("2. Para execução por grupos:")
                print("   python execute_clisat_strategy.py --groups small_fast")
                print("   python execute_clisat_strategy.py --groups medium")
                print("   python execute_clisat_strategy.py --groups large")
                print("   python execute_clisat_strategy.py --groups critical")
                print()
                print("3. Para ver resumo da estratégia:")
                print("   python execute_clisat_strategy.py --summary")
        else:
            print("\nTeste prático pulado. Use os comandos acima para execução.")
    
    except KeyboardInterrupt:
        print("\n\n⏹️  Teste interrompido pelo usuário")
    except Exception as e:
        print(f"\n❌ Erro durante o teste: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
