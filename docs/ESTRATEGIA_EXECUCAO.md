# Estratégia de Execução do CliSAT - Clique Máximo

Este documento descreve a estratégia completa para executar o algoritmo CliSAT em todas as instâncias DIMACS do projeto, incluindo organização por grupos, timeouts adaptativos e sistema de checkpoint.

## 📋 Visão Geral

A estratégia foi desenvolvida para executar o algoritmo CliSAT de forma eficiente e robusta em todas as 37 instâncias DIMACS, organizando-as por dificuldade computacional e implementando mecanismos de recuperação.

### 🎯 Objetivos

1. **Execução Completa**: Processar todas as instâncias da atividade APA
2. **Organização Inteligente**: Agrupar instâncias por dificuldade
3. **Robustez**: Sistema de checkpoint para recuperação
4. **Monitoramento**: Logs detalhados e análise em tempo real
5. **Resultados**: Tabela final formatada conforme solicitado

## 📊 Grupos de Instâncias

### Grupo 1: Small Fast (7 instâncias)
- **Instâncias**: C125.9, brock200_2, brock200_4, gen200_p0.9_44, gen200_p0.9_55, keller4, hamming8-4
- **Características**: < 300 nós, execução rápida
- **Tempo limite**: 30 minutos por instância
- **Tempo estimado**: 5-30 minutos por instância

### Grupo 2: Medium (12 instâncias)
- **Instâncias**: C250.9, brock400_2, brock400_4, gen400_*, MANN_a27, DSJC500_5, p_hat300_*, keller5
- **Características**: 300-800 nós, tempo moderado
- **Tempo limite**: 45 minutos por instância
- **Tempo estimado**: 10-45 minutos por instância

### Grupo 3: Large (12 instâncias)
- **Instâncias**: C500.9, brock800_*, p_hat700_*, MANN_a45, hamming10-4, C1000.9, DSJC1000_5, p_hat1500_1/2
- **Características**: 800-1500 nós, tempo considerável
- **Tempo limite**: 1 hora por instância
- **Tempo estimado**: 15-60 minutos por instância

### Grupo 4: Critical (6 instâncias)
- **Instâncias**: C2000.9, C2000.5, p_hat1500-3, keller6, MANN_a81, C4000.5
- **Características**: > 1500 nós ou conhecidamente difíceis
- **Tempo limite**: 66 minutos por instância
- **Tempo estimado**: 30-66 minutos por instância

## 🚀 Como Usar

### 1. Teste Inicial
```bash
# Teste rápido com instâncias pequenas
python test_clisat_strategy.py
```

### 2. Execução por Grupos
```bash
# Executar apenas instâncias pequenas
python execute_clisat_strategy.py --groups small_fast

# Executar instâncias médias
python execute_clisat_strategy.py --groups medium

# Executar múltiplos grupos
python execute_clisat_strategy.py --groups small_fast medium
```

### 3. Execução Completa
```bash
# Executar todos os grupos
python execute_clisat_strategy.py --all
```

### 4. Retomar Execução
```bash
# Retomar a partir do checkpoint
python execute_clisat_strategy.py --resume

# Iniciar do zero (ignorar checkpoint)
python execute_clisat_strategy.py --all --no-resume
```

### 5. Visualizar Estratégia
```bash
# Mostrar resumo da estratégia
python execute_clisat_strategy.py --summary
```

## 📈 Análise de Resultados

### Análise Rápida
```bash
# Resumo rápido dos resultados
python analyze_clisat_results.py --summary
```

### Análise Completa
```bash
# Gerar relatório completo e gráficos
python analyze_clisat_results.py --all
```

### Opções Específicas
```bash
# Apenas gráficos
python analyze_clisat_results.py --plots

# Apenas relatório
python analyze_clisat_results.py --report

# Tabela LaTeX
python analyze_clisat_results.py --latex
```

## 📁 Estrutura de Arquivos

```
execution_results/
├── execution_checkpoint.json      # Checkpoint da execução
├── clisat_final_results.csv      # Resultados finais
├── formatted_results_table.txt   # Tabela formatada
├── partial_results_*.json        # Backups parciais
├── plots/
│   └── performance_analysis.png  # Gráficos de análise
└── reports/
    ├── comprehensive_analysis_report.txt
    ├── latex_table.tex
    └── results_for_excel.csv
```

## ⚙️ Funcionalidades Avançadas

### Sistema de Checkpoint
- **Salvamento Automático**: Após cada instância processada
- **Recuperação**: Retoma exatamente do ponto de parada
- **Backup**: Backups parciais após cada grupo

### Monitoramento
- **Logs Detalhados**: Progresso em tempo real
- **Estatísticas**: Tempo, sucesso, progresso por grupo
- **Validação**: Verificação automática dos cliques encontrados

### Timeouts Adaptativos
- **Por Tamanho**: Timeouts baseados no tamanho das instâncias
- **Por Dificuldade**: Tempo maior para instâncias conhecidamente difíceis
- **Flexível**: Pode ser ajustado conforme necessário

## 📊 Formato da Tabela de Resultados

A tabela final seguirá o formato solicitado:

| Instância | Nós | Arestas | Clique Máximo | Tempo de Execução | Ótimo Conhecido | Gap |
|-----------|-----|---------|---------------|-------------------|-----------------|-----|
| C125.9    | 125 | 6963    | 34           | 45.2s            | 34              | 0.0% |
| ...       | ... | ...     | ...          | ...              | ...             | ... |

### Colunas da Tabela
- **Instância**: Nome da instância DIMACS
- **Nós**: Número de vértices do grafo
- **Arestas**: Número de arestas do grafo
- **Clique Máximo**: Tamanho do maior clique encontrado
- **Tempo de Execução**: Tempo em segundos
- **Ótimo Conhecido**: Valor ótimo conhecido (quando disponível)
- **Gap**: Diferença percentual para o ótimo conhecido

## 🔧 Configuração e Personalização

### Modificar Timeouts
Edite o arquivo `execute_clisat_strategy.py`, método `define_instance_groups()`:

```python
'small_fast': {
    'time_limit': 1800,  # Altere para o tempo desejado (30 minutos)
    # ...
}
```

### Adicionar/Remover Instâncias
Modifique as listas de instâncias nos grupos conforme necessário.

### Configurar Diretórios
```python
strategy = CliSATExecutionStrategy(base_dir="/caminho/personalizado")
```

## 📊 Estimativas de Tempo

### Cenário Otimista (30% do tempo limite)
- **Small Fast**: 35-105 minutos
- **Medium**: 90-270 minutos (1.5-4.5 horas)
- **Large**: 180-540 minutos (3-9 horas)
- **Critical**: 120-240 minutos (2-4 horas)
- **Total**: 7-17 horas

### Cenário Realista (60% do tempo limite)
- **Small Fast**: 70-210 minutos (1.2-3.5 horas)
- **Medium**: 180-540 minutos (3-9 horas)
- **Large**: 360-1080 minutos (6-18 horas)
- **Critical**: 240-480 minutos (4-8 horas)
- **Total**: 14-38 horas

### Cenário Pessimista (tempo limite completo)
- **Small Fast**: 210 minutos (3.5 horas)
- **Medium**: 540 minutos (9 horas)
- **Large**: 720 minutos (12 horas)
- **Critical**: 400 minutos (6.7 horas)
- **Total**: 31+ horas

## 🛡️ Tratamento de Erros

### Tipos de Erro Tratados
1. **Timeout**: Instância excede tempo limite
2. **Memória**: Esgotamento de memória
3. **Arquivo**: Problema ao carregar instância
4. **Algoritmo**: Erro interno do CliSAT

### Estratégias de Recuperação
- **Checkpoint**: Salva progresso automaticamente
- **Pular**: Continua com próxima instância
- **Log**: Registra todos os erros para análise
- **Retry**: Opção para reexecutar instâncias falhadas

## 📋 Lista Completa de Instâncias

```
Small Fast (7):  C125.9, brock200_2, brock200_4, gen200_p0.9_44, 
                 gen200_p0.9_55, keller4, hamming8-4

Medium (12):     C250.9, brock400_2, brock400_4, gen400_p0.9_55,
                 gen400_p0.9_65, gen400_p0.9_75, MANN_a27, DSJC500_5,
                 p_hat300-1, p_hat300-2, p_hat300-3, keller5

Large (12):      C500.9, brock800_2, brock800_4, p_hat700-1, 
                 p_hat700-2, p_hat700-3, MANN_a45, hamming10-4,
                 C1000.9, DSJC1000_5, p_hat1500-1, p_hat1500-2

Critical (6):    C2000.9, C2000.5, p_hat1500-3, keller6, 
                 MANN_a81, C4000.5

Total: 37 instâncias
```

## 🎯 Recomendações de Execução

### Para Desenvolvimento/Teste
1. Execute `test_clisat_strategy.py` primeiro
2. Teste com `--groups small_fast`
3. Verifique resultados antes de prosseguir

### Para Execução Completa
1. Execute em horário com menos uso do sistema
2. Use `nohup` para execução em background:
   ```bash
   nohup python execute_clisat_strategy.py --all > execution.log 2>&1 &
   ```
3. Monitore progresso via logs
4. Mantenha backups regulares

### Para Máxima Eficiência
1. Execute grupos paralelamente em máquinas diferentes
2. Priorize grupos pequenos primeiro
3. Reserve tempo maior para grupos críticos
4. Monitore uso de memória e CPU

## 📞 Suporte e Depuração

### Logs Importantes
- `clisat_execution.log`: Log principal da execução
- `execution_checkpoint.json`: Estado atual da execução
- `partial_results_*.json`: Backups parciais

### Comandos Úteis de Depuração
```bash
# Ver últimas linhas do log
tail -f clisat_execution.log

# Verificar checkpoint
cat execution_results/execution_checkpoint.json | jq .

# Contar instâncias concluídas
grep "SUCCESS" execution_results/clisat_final_results.csv | wc -l
```

### Problemas Comuns
1. **Instância não carrega**: Verifique se arquivo DIMACS existe
2. **Timeout muito curto**: Aumente tempo limite no grupo
3. **Erro de memória**: Monitore uso de RAM
4. **Checkpoint corrompido**: Delete e reinicie com `--no-resume`

---

**Autor**: Walber  
**Data**: Julho 2025  
**Projeto**: Análise e Projeto de Algoritmos - Mestrado
