#!/bin/bash
# Script de limpeza conservadora - remove apenas arquivos 100% redundantes

echo "🧹 LIMPEZA CONSERVADORA - Removendo arquivos redundantes..."

# Arquivos Python movidos para nova estrutura
echo "Removendo arquivos Python redundantes..."
rm -f apa_results_generator.py
rm -f clique_heuristics.py 
rm -f grasp_maximum_clique.py
rm -f run_apa_activity.py
rm -f simple_test.py

# Arquivos de teste movidos
echo "Removendo testes da raiz..."
rm -f test_algorithms.py
rm -f test_clisat_strategy.py
rm -f test_grasp_integration.py
rm -f test_logs.py

# Cache Python
echo "Removendo cache Python..."
rm -rf __pycache__/

# Diretórios vazios ou movidos (após verificar se conteúdo foi copiado)
echo "Verificando diretórios para remoção..."
if [ -d "data_files/dimacs" ] && [ "$(ls -A data_files/dimacs)" ]; then
    echo "Removendo dimacs_data antigo..."
    rm -rf dimacs_data/
fi

if [ -d "data_files/results" ]; then
    echo "Removendo execution_results antigo..."
    rm -rf execution_results/
fi

echo "✅ Limpeza conservadora concluída!"
echo "📋 Arquivos mantidos para análise:"
echo "   - analyze_clisat_results.py"
echo "   - apa_results_manager.py" 
echo "   - execute_clisat_strategy.py"
echo "   - Documentação em *.md"
