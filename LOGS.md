# Logs Periódicos do CliSAT

## Funcionalidades Implementadas

### 1. Logs de Inicialização
- **Início do algoritmo**: Mostra informações do grafo (vértices, arestas, densidade)
- **Configuração**: Exibe limite de tempo e intervalos de log
- **Clique inicial**: Apresenta o clique inicial encontrado pela heurística gulosa
- **Ordenação COLOR-SORT**: Confirma conclusão da ordenação dos vértices

### 2. Logs de Progresso Periódico
Os logs são exibidos automaticamente com base em dois critérios:

#### Por Número de Nós
- **Parâmetro**: `log_interval` (padrão: 1000 nós)
- **Quando**: A cada N nós processados pelo algoritmo

#### Por Tempo Decorrido
- **Parâmetro**: `time_interval` (padrão: 30 segundos)
- **Quando**: A cada N segundos de execução

#### Informações nos Logs Periódicos:
- ⏱️ **Tempo decorrido**: Formato HH:MM:SS
- 🔢 **Nós processados**: Contador total de nós explorados
- 📊 **Taxa de processamento**: Nós por segundo
- 🎯 **Maior clique atual**: Tamanho do melhor clique encontrado
- 📋 **Vértices do clique**: Lista dos vértices (limitada a 10 para legibilidade)
- 🔗 **Chamadas SAT**: Número de consultas ao solver SAT
- ✂️ **Podas**: Número de nós podados por limitantes
- 🧮 **Filter Phase**: Número de chamadas para a fase de filtragem
- 🎨 **SATCOL**: Número de chamadas para o refinamento SAT

### 3. Logs de Descoberta de Cliques
- **Quando**: Sempre que um clique maior que o atual é descoberto
- **Conteúdo**: 
  - 🎉 Anúncio de novo melhor clique
  - 📏 Novo tamanho
  - ⏱️ Tempo de descoberta
  - 🔢 Nó onde foi descoberto
  - 📋 Vértices do novo clique

### 4. Logs de Finalização
- **Resumo final**: Tempo total, melhor clique, estatísticas detalhadas
- **Validação**: Verificação se o clique encontrado é válido
- **Estatísticas completas**: Todos os contadores e métricas de execução

## Como Usar

### Configuração Básica
```python
from clisat_algortithmb import CliSAT

# Usar configurações padrão
solver = CliSAT(graph)
clique, size = solver.solve()
```

### Configuração Personalizada
```python
# Logs mais frequentes
solver = CliSAT(
    graph,
    time_limit=3600.0,    # 1 hora
    log_interval=100,     # A cada 100 nós
    time_interval=10.0    # A cada 10 segundos
)
clique, size = solver.solve()
```

### Função Conveniente
```python
from clisat_algortithmb import solve_maximum_clique_clisat

clique, size = solve_maximum_clique_clisat(
    graph,
    time_limit=600.0,     # 10 minutos
    log_interval=50,      # A cada 50 nós
    time_interval=5.0     # A cada 5 segundos
)
```

## Exemplos de Saída

### Log de Inicialização
```
🚀 INICIANDO CliSAT
   📊 Grafo: 14 vértices, 65 arestas
   ⏱️  Limite de tempo: 20s
   📋 Intervalo de log: a cada 5 nós ou 3.0s
==================================================

🎯 Clique inicial encontrado:
   📏 Tamanho: 8
   📋 Vértices: [1, 2, 3, 4, 6, 7, 9, 14]
```

### Log de Progresso
```
🔍 PROGRESSO CliSAT:
   ⏱️  Tempo: 00:05:23
   🔢 Nós processados: 15,432
   📊 Taxa: 47.2 nós/seg
   🎯 Maior clique: 12 vértices
   📋 Clique atual: [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
   🔗 Chamadas SAT: 2,847
   ✂️  Podas: 8,951
   🧮 Filter Phase: 156
   🎨 SATCOL: 423
--------------------------------------------------
```

### Log de Novo Clique
```
🎉 NOVO MELHOR CLIQUE ENCONTRADO!
   📏 Tamanho: 13
   ⏱️  Tempo: 00:12:45
   🔢 Nó: 28,461
   📋 Clique: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20]
        ... e mais 3 vértices
```

### Log de Finalização
```
🏁 CliSAT FINALIZADO!
   ⏱️  Tempo total: 18.45s
   🎯 Clique máximo: 13 vértices
   📋 Vértices: [2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 24, 26]
   📊 Nós explorados: 45,678
   🔗 Chamadas SAT: 8,912
   ✂️  Podas por limite: 28,341
==================================================
```

## Vantagens dos Logs

1. **Monitoramento em Tempo Real**: Acompanhar o progresso do algoritmo em execuções longas
2. **Detecção de Problemas**: Identificar se o algoritmo está travado ou progredindo lentamente
3. **Análise de Performance**: Entender quantos nós são processados por segundo
4. **Validação**: Confirmar que cliques maiores estão sendo descobertos
5. **Debugging**: Facilitar a identificação de gargalos no algoritmo
6. **Transparência**: Mostrar exatamente o que o algoritmo está fazendo

## Personalização

Os intervalos podem ser ajustados conforme a necessidade:

- **Para grafos pequenos**: Intervalos menores (log_interval=10, time_interval=1.0)
- **Para grafos grandes**: Intervalos maiores (log_interval=10000, time_interval=60.0)
- **Para debugging**: Intervalos muito pequenos (log_interval=1, time_interval=0.5)
- **Para produção**: Intervalos moderados (padrões atuais)
