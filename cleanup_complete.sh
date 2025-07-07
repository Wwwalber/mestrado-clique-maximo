#!/bin/bash
# Script de limpeza completa - organiza tudo na nova estrutura

echo "🧹 LIMPEZA COMPLETA - Organizando projeto na nova estrutura..."

# 1. Remover arquivos Python redundantes
echo "1. Removendo arquivos Python redundantes..."
rm -f apa_results_generator.py
rm -f clique_heuristics.py 
rm -f grasp_maximum_clique.py
rm -f run_apa_activity.py
rm -f simple_test.py
rm -f test_algorithms.py
rm -f test_clisat_strategy.py
rm -f test_grasp_integration.py
rm -f test_logs.py

# 2. Mover documentação para docs/
echo "2. Organizando documentação..."
mv ESTRATEGIA_EXECUCAO.md docs/ 2>/dev/null || true
mv EXECUCAO_PRONTA.md docs/ 2>/dev/null || true
mv LOGS.md docs/ 2>/dev/null || true
mv MONITORAMENTO.md docs/ 2>/dev/null || true
mv SISTEMA_DUAS_ABORDAGENS.md docs/ 2>/dev/null || true
mv PROPOSTA_REORGANIZACAO.md docs/ 2>/dev/null || true

# 3. Mover arquivos de funcionalidade específica para scripts/
echo "3. Organizando scripts específicos..."
mv analyze_clisat_results.py scripts/analyze_clisat_results.py 2>/dev/null || true
mv apa_results_manager.py scripts/apa_results_manager.py 2>/dev/null || true
mv execute_clisat_strategy.py scripts/execute_clisat_strategy.py 2>/dev/null || true

# 4. Mover logs para data_files/
echo "4. Organizando logs..."
mkdir -p data_files/logs
mv clisat_execution.log data_files/logs/ 2>/dev/null || true
mv *.log data_files/logs/ 2>/dev/null || true

# 5. Remover cache e diretórios redundantes
echo "5. Removendo cache e diretórios redundantes..."
rm -rf __pycache__/

# Verificar se conteúdo foi copiado antes de remover
if [ -d "data_files/dimacs" ] && [ "$(ls -A data_files/dimacs)" ]; then
    echo "Removendo dimacs_data antigo..."
    rm -rf dimacs_data/
fi

if [ -d "data_files/results" ]; then
    echo "Removendo execution_results antigo..."
    rm -rf execution_results/
fi

# 6. Remover diretório src/ (conteúdo já movido)
echo "6. Removendo diretório src/ antigo..."
rm -rf src/

echo ""
echo "✅ LIMPEZA COMPLETA CONCLUÍDA!"
echo ""
echo "📁 ESTRUTURA FINAL:"
echo "├── algorithms/          # Algoritmos principais"
echo "├── data/               # Gerenciamento de dados"
echo "├── experiments/        # Experimentos"
echo "├── tests/              # Testes"
echo "├── scripts/            # Scripts executáveis"
echo "├── config/             # Configurações"
echo "├── docs/               # Documentação completa"
echo "├── data_files/         # Dados, logs e resultados"
echo "└── venv-clique/        # Ambiente virtual"
echo ""
echo "🎯 Projeto 100% organizado e limpo!"
