#!/usr/bin/env python3
"""
Configuração otimizada para execução em 11 horas - TODAS AS 37 INSTÂNCIAS.

Esta configuração garante:
1. Execução de TODAS as 37 instâncias (CliSAT + GRASP)
2. Timeouts realistas para completar em 11h
3. Resultados comparativos completos para a dissertação
"""

# CONFIGURAÇÃO OTIMIZADA PARA 11 HORAS - TODAS AS INSTÂNCIAS
CONFIG_11H = {
    # CliSAT - Timeout otimizado para todas as instâncias
    'clisat_timeout': 600,  # 10 minutos por instância (realista)
    
    # GRASP - Eficiente, pode usar timeout maior se necessário
    'grasp_timeout': 180,   # 3 minutos por instância (buffer extra)
    
    # Execução completa
    'total_instances': 37,  # TODAS as instâncias DIMACS
    
    # Estimativa de tempo para TODAS as 37 instâncias:
    # - CliSAT: 37 × 10min = 370min (6.17h)
    # - GRASP: 37 × 3min = 111min (1.85h)  
    # - TOTAL: 481min (8.02h)
    # - BUFFER: 2.98h para imprevistos e instâncias difíceis
    # - MARGEM: Dentro das 11h disponíveis com boa folga!
}

# COMANDOS PARA APLICAR A NOVA CONFIGURAÇÃO

def apply_optimized_config():
    """Comandos para aplicar a configuração otimizada."""
    print("\n" + "="*60)
    print("🔧 COMANDOS PARA APLICAR A CONFIGURAÇÃO OTIMIZADA")
    print("="*60)
    
    print("\n1️⃣ PARAR EXECUÇÃO ATUAL DO CLISAT:")
    print("   # Encontrar e matar o processo que está há 4h+ rodando")
    print("   pkill -f 'execute_clisat_strategy.py'")
    print("   # Ou usar Ctrl+C no terminal onde está rodando")
    
    print("\n2️⃣ ATUALIZAR TIMEOUTS NO ALGORITMO:")
    print("   # Editar config/algorithm_params.py:")
    print("   CLISAT_TIME_LIMIT = 600      # 10 minutos")
    print("   GRASP_TIME_LIMIT = 180       # 3 minutos")
    
    print("\n3️⃣ EXECUTAR CLISAT COM NOVOS TIMEOUTS:")
    print("   ./venv-clique/bin/python scripts/execute_clisat_strategy.py \\")
    print("     --groups small_fast,medium,large \\")
    print("     --time-limit 600 \\")
    print("     --resume")
    
    print("\n4️⃣ EXECUTAR GRASP EM PARALELO:")
    print("   ./venv-clique/bin/python scripts/batch_execution.py \\")
    print("     --time-limit-exact 600 \\")
    print("     --time-limit-heuristic 180 \\")
    print("     --output resultados_finais_11h")
    
    print("\n5️⃣ OU APENAS GRASP (SE CLISAT AINDA ESTIVER RODANDO):")
    print("   ./venv-clique/bin/python scripts/grasp_only_execution.py \\")
    print("     --time-limit 180 \\")
    print("     --output grasp_11h_todas_instancias")
    
    print("\n📊 MONITORAMENTO:")
    print("   # Ver progresso CliSAT:")
    print("   tail -f data_files/logs/clisat_execution.log")
    print("   # Ver processos rodando:")
    print("   ps aux | grep python | grep -E '(clisat|grasp|batch)'")
    
    print("\n⏰ CRONOGRAMA SUGERIDO:")
    print("   Agora: Parar CliSAT atual e iniciar com novo timeout")
    print("   +6h: CliSAT terminará a maioria das instâncias")
    print("   +2h: GRASP processará todas as 37 instâncias")
    print("   +3h: Buffer para instâncias difíceis e análise")
    print("   = 11h TOTAL")

# COMANDOS DE MONITORAMENTO PARA O TERMINAL
def print_monitoring_commands():
    """Comandos práticos para monitorar execuções no terminal."""
    print("\n" + "="*60)
    print("📊 COMANDOS DE MONITORAMENTO (USE NO SEU TERMINAL)")
    print("="*60)
    
    print("\n🔍 VER PROCESSOS RODANDO:")
    print("ps aux | grep python | grep -E '(grasp|clisat)' | grep -v grep")
    
    print("\n📈 MONITORAR GRASP EM TEMPO REAL:")
    print("tail -f data_files/thesis_results/grasp_11h_todas_instancias_*.log")
    
    print("\n📈 MONITORAR CLISAT EM TEMPO REAL:")
    print("tail -f clisat_execution.log")
    
    print("\n📊 VER ÚLTIMOS RESULTADOS GRASP:")
    print("ls -la data_files/thesis_results/*grasp*11h* | tail -5")
    
    print("\n⏱️ TEMPO DE EXECUÇÃO DOS PROCESSOS:")
    print("ps -eo pid,etime,cmd | grep python | grep -E '(grasp|clisat)'")
    
    print("\n🔄 VERIFICAR PROGRESSO APROXIMADO:")
    print("# GRASP - contar instâncias processadas:")
    print("grep -c 'Processando' data_files/thesis_results/grasp_11h_todas_instancias_*.log | tail -1")
    print("# CliSAT - ver último checkpoint:")
    print("grep 'instâncias concluídas' clisat_execution.log | tail -1")
    
    print("\n💾 USO DE MEMÓRIA:")
    print("ps aux | grep python | grep -E '(grasp|clisat)' | awk '{print $2, $4\"%\", $11}' | head -10")
    
    print("\n🎯 ESTIMATIVA DE CONCLUSÃO:")
    print("# Se GRASP está na instância X de 37:")
    print("# Tempo restante ≈ (37-X) × 3min")
    print("# Se CliSAT está na instância Y de 31:")
    print("# Tempo restante ≈ (31-Y) × 10min")

# PARÂMETROS PARA SCRIPTS
SCRIPT_PARAMS = {
    'clisat_command': [
        './venv-clique/bin/python', 'scripts/execute_clisat_strategy.py',
        '--groups', 'small_fast,medium,large',
        '--time-limit', '600',
        '--resume'
    ],
    'batch_command': [
        './venv-clique/bin/python', 'scripts/batch_execution.py',
        '--time-limit-exact', '600',
        '--time-limit-heuristic', '180',
        '--output', 'resultados_finais_11h'
    ],
    'grasp_only_command': [
        './venv-clique/bin/python', 'scripts/grasp_only_execution.py',
        '--time-limit', '180',
        '--output', 'grasp_11h_todas_instancias'
    ]
}

def print_strategy():
    """Imprimir estratégia detalhada."""
    print("🎯 ESTRATÉGIA OTIMIZADA PARA 11 HORAS - TODAS AS INSTÂNCIAS")
    print("=" * 60)
    print(f"⏱️  CliSAT timeout: {CONFIG_11H['clisat_timeout']}s (10min)")
    print(f"⏱️  GRASP timeout: {CONFIG_11H['grasp_timeout']}s (3min)")
    print(f"📊 Total de instâncias: {CONFIG_11H['total_instances']} (TODAS)")
    print()
    print("📈 ESTIMATIVA DE TEMPO PARA TODAS AS 37 INSTÂNCIAS:")
    
    clisat_time = CONFIG_11H['total_instances'] * CONFIG_11H['clisat_timeout'] / 60
    grasp_time = CONFIG_11H['total_instances'] * CONFIG_11H['grasp_timeout'] / 60
    total_time = clisat_time + grasp_time
    
    print(f"   CliSAT: {clisat_time:.1f} min ({clisat_time/60:.1f}h)")
    print(f"   GRASP:  {grasp_time:.1f} min ({grasp_time/60:.1f}h)")
    print(f"   TOTAL:  {total_time:.1f} min ({total_time/60:.1f}h)")
    print(f"   BUFFER: {11 - total_time/60:.1f}h para imprevistos")
    print()
    if total_time/60 <= 11:
        print("✅ VIÁVEL para execução em 11 horas!")
        print("🎯 Vai processar TODAS as 37 instâncias com boa margem de segurança!")
    else:
        print("⚠️ Pode exceder 11 horas - considere reduzir timeouts")
    
    print()
    print("📋 PRÓXIMOS PASSOS:")
    print("1. 🛑 Parar execução CliSAT atual (está há 4h+ em uma instância)")
    print("2. ⚙️  Aplicar novos timeouts (10min CliSAT, 3min GRASP)")
    print("3. 🚀 Reiniciar com configuração otimizada")
    print("4. 📊 Obter resultados de TODAS as 37 as instâncias em ~8h")

if __name__ == "__main__":
    print_strategy()
    apply_optimized_config()
    print_monitoring_commands()
