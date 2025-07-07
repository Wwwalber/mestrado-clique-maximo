#!/bin/bash
# Script para visualizar arquivos que podem ser removidos (não remove nada)

echo "🔍 ANÁLISE DE ARQUIVOS REDUNDANTES - Modo Visualização"
echo "=============================================================="

echo ""
echo "📋 ARQUIVOS PYTHON REDUNDANTES (movidos para nova estrutura):"
echo "❌ apa_results_generator.py → experiments/results_generator.py"
echo "❌ clique_heuristics.py → integrado em algorithms/"
echo "❌ grasp_maximum_clique.py → algorithms/grasp_heuristic.py"
echo "❌ run_apa_activity.py → scripts/run_apa_activity.py"
echo "❌ simple_test.py → obsoleto"
echo "❌ test_*.py → tests/"

echo ""
echo "📁 DIRETÓRIOS REDUNDANTES:"
if [ -d "dimacs_data" ]; then
    echo "❌ dimacs_data/ ($(du -sh dimacs_data | cut -f1)) → data_files/dimacs/"
fi
if [ -d "execution_results" ]; then
    echo "❌ execution_results/ ($(du -sh execution_results | cut -f1)) → data_files/results/"
fi
if [ -d "src" ]; then
    echo "❌ src/ → conteúdo movido para nova estrutura"
fi
if [ -d "__pycache__" ]; then
    echo "❌ __pycache__/ → cache Python desnecessário"
fi

echo ""
echo "📄 DOCUMENTAÇÃO PARA REORGANIZAR:"
for file in ESTRATEGIA_EXECUCAO.md EXECUCAO_PRONTA.md LOGS.md MONITORAMENTO.md SISTEMA_DUAS_ABORDAGENS.md PROPOSTA_REORGANIZACAO.md; do
    if [ -f "$file" ]; then
        echo "⚠️  $file → docs/$file"
    fi
done

echo ""
echo "🔧 ARQUIVOS DE FUNCIONALIDADE ESPECÍFICA:"
for file in analyze_clisat_results.py apa_results_manager.py execute_clisat_strategy.py; do
    if [ -f "$file" ]; then
        echo "⚠️  $file (pode ser movido para scripts/ ou mantido)"
    fi
done

echo ""
echo "📊 LOGS E RESULTADOS:"
for file in *.log; do
    if [ -f "$file" ]; then
        echo "⚠️  $file → data_files/logs/"
    fi
done

echo ""
echo "=============================================================="
echo "🎯 RECOMENDAÇÕES:"
echo ""
echo "1. LIMPEZA CONSERVADORA (segura):"
echo "   bash cleanup_conservative.sh"
echo ""
echo "2. LIMPEZA COMPLETA (mais organizada):"
echo "   bash cleanup_complete.sh"
echo ""
echo "3. Este script não remove nada - apenas mostra o que pode ser limpo."
echo "=============================================================="
