#!/usr/bin/env python3
"""
Teste simples de download de instâncias.
"""

import sys
import logging
from pathlib import Path

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')

# Adicionar src ao path
sys.path.insert(0, str(Path(__file__).parent / "src"))

try:
    from apa_instance_manager import APAInstanceManager
    print("✅ Módulo importado com sucesso")
    
    manager = APAInstanceManager()
    print("✅ Manager criado")
    
    # Listar algumas instâncias
    instances = manager.list_instances()
    print(f"✅ Instâncias disponíveis: {len(instances)}")
    print(f"Primeiras 3: {instances[:3]}")
    
    # Tentar baixar uma instância pequena
    print("\n🔽 Testando download de C125.9...")
    success = manager.download_instance('C125.9')
    print(f"Resultado: {success}")
    
    if success:
        print("🔍 Verificando arquivo baixado...")
        file_path = Path("dimacs_data") / "C125.9.clq"
        if file_path.exists():
            print(f"✅ Arquivo existe: {file_path}")
            print(f"Tamanho: {file_path.stat().st_size} bytes")
            
            # Tentar carregar
            print("📖 Testando carregamento...")
            graph = manager.load_instance('C125.9')
            if graph:
                print(f"✅ Grafo carregado: {len(graph.nodes())} nós, {len(graph.edges())} arestas")
            else:
                print("❌ Erro ao carregar grafo")
        else:
            print("❌ Arquivo não foi criado")
    else:
        print("❌ Download falhou")

except ImportError as e:
    print(f"❌ Erro de importação: {e}")
except Exception as e:
    print(f"❌ Erro: {e}")
    import traceback
    traceback.print_exc()
