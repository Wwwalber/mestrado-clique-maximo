# Modos de Monitoramento do CliSAT

## Diferenças entre Log e Monitoramento em Tempo Real

### 📝 **Modo LOG (Tradicional)**
```python
solver = CliSAT(graph, monitor_mode='log')
```

**Características:**
- ✅ **Histórico completo**: Todas as mensagens ficam visíveis
- ✅ **Análise posterior**: Fácil de revisar o progresso
- ✅ **Logging para arquivo**: Pode ser redirecionado para arquivo
- ✅ **Debugging**: Ideal para análise detalhada
- ❌ **Interface "suja"**: Muitas linhas podem poluir o terminal

**Exemplo de saída:**
```
🔍 PROGRESSO CliSAT:
   ⏱️  Tempo: 00:05:23
   🔢 Nós processados: 15,432
   📊 Taxa: 47.2 nós/seg
   🎯 Maior clique: 12 vértices
   ...
--------------------------------------------------

🔍 PROGRESSO CliSAT:
   ⏱️  Tempo: 00:05:53
   🔢 Nós processados: 16,891
   📊 Taxa: 48.1 nós/seg
   🎯 Maior clique: 12 vértices
   ...
--------------------------------------------------
```

### 📊 **Modo REALTIME (Tempo Real)**
```python
solver = CliSAT(graph, monitor_mode='realtime')
```

**Características:**
- ✅ **Interface limpa**: Dashboard atualizado na mesma posição
- ✅ **Visual atrativo**: Formato de painel organizado
- ✅ **Menos poluição**: Terminal fica limpo
- ✅ **Monitoramento live**: Ideal para acompanhar execuções longas
- ❌ **Sem histórico**: Apenas o estado atual é visível
- ❌ **Dependência de terminal**: Requer terminal compatível com ANSI

**Exemplo de saída:**
```
┌──────────────────────────────────────────────────────────┐
│                  🔍 CliSAT MONITOR                      │
├──────────────────────────────────────────────────────────┤
│ ⏱️  Tempo: 00:05:23                                    │
│ 🔢 Nós: 15,432                                         │
│ 📊 Taxa: 47.2 nós/seg                                  │
│ 🎯 Clique: 12 vértices                                 │
│ 📋 [1, 3, 5, 7, 9...+7]                              │
│ 🔗 SAT: 2,847                                          │
│ ✂️  Podas: 8,951                                       │
└──────────────────────────────────────────────────────────┘
```

### 🔄 **Modo BOTH (Híbrido)**
```python
solver = CliSAT(graph, monitor_mode='both')
```

**Características:**
- ✅ **Dashboard em tempo real**: Para progresso contínuo
- ✅ **Logs de eventos especiais**: Para descoberta de novos cliques
- ✅ **Melhor dos dois mundos**: Monitoramento + histórico de eventos importantes
- ⚠️ **Complexidade**: Pode ser confuso em alguns cenários

**Comportamento:**
- Dashboard atualizado em tempo real para progresso
- Logs tradicionais para eventos importantes (novos cliques, finalizações)

### 🤫 **Modo SILENT (Silencioso)**
```python
solver = CliSAT(graph, monitor_mode='silent')
```

**Características:**
- ✅ **Performance máxima**: Sem overhead de I/O
- ✅ **Execução limpa**: Sem poluição de saída
- ✅ **Ideal para produção**: Scripts automatizados
- ✅ **Benchmarking**: Medições de tempo precisas
- ❌ **Sem feedback**: Não sabemos o que está acontecendo durante execução

## Quando Usar Cada Modo

### 🔬 **Para Desenvolvimento e Debugging**
```python
# Use modo 'log' para análise detalhada
solver = CliSAT(graph, 
    monitor_mode='log',
    log_interval=100,     # Logs frequentes
    time_interval=5.0     # A cada 5 segundos
)
```

### 👀 **Para Monitoramento de Execuções Longas**
```python
# Use modo 'realtime' para acompanhar visualmente
solver = CliSAT(graph,
    monitor_mode='realtime',
    log_interval=1000,    # Dashboard a cada 1000 nós
    time_interval=10.0    # Ou a cada 10 segundos
)
```

### 🏃 **Para Execução em Produção**
```python
# Use modo 'silent' para máxima performance
solver = CliSAT(graph, monitor_mode='silent')
```

### 📊 **Para Demonstrações e Apresentações**
```python
# Use modo 'both' para mostrar progresso e eventos
solver = CliSAT(graph,
    monitor_mode='both',
    log_interval=50,      # Dashboard frequente
    time_interval=3.0     # Atualização rápida
)
```

## Exemplos Práticos

### Teste Rápido com Feedback Visual
```python
import networkx as nx
from clisat_algortithmb import solve_maximum_clique_clisat

# Criar grafo
G = nx.erdos_renyi_graph(100, 0.5)

# Executar com dashboard em tempo real
clique, size = solve_maximum_clique_clisat(
    G,
    time_limit=60.0,
    monitor_mode='realtime',
    log_interval=50,
    time_interval=2.0
)
```

### Análise Detalhada para Debugging
```python
# Executar com logs completos
clique, size = solve_maximum_clique_clisat(
    G,
    time_limit=300.0,
    monitor_mode='log',
    log_interval=10,      # Log muito frequente
    time_interval=1.0     # A cada segundo
)
```

### Benchmark de Performance
```python
import time

# Medir tempo sem overhead de I/O
start = time.time()
clique, size = solve_maximum_clique_clisat(
    G,
    time_limit=600.0,
    monitor_mode='silent'
)
end = time.time()

print(f"Clique: {size} vértices em {end-start:.2f}s")
```

## Scripts de Demonstração

### Testar Todos os Modos
```bash
cd src
python monitor_demo.py --mode compare
```

### Testar Modo Específico
```bash
# Modo de log tradicional
python monitor_demo.py --mode log

# Modo tempo real
python monitor_demo.py --mode realtime

# Modo híbrido
python monitor_demo.py --mode both

# Modo silencioso
python monitor_demo.py --mode silent
```

### Testar com Grafos de Tamanhos Diferentes
```bash
# Grafo pequeno (teste rápido)
python monitor_demo.py --mode realtime --size small

# Grafo médio (demonstração)
python monitor_demo.py --mode realtime --size medium

# Grafo grande (teste de performance)
python monitor_demo.py --mode realtime --size large
```

## Vantagens de Cada Abordagem

### Log Tradicional (mode='log')
- 📜 **Auditoria completa**: Registro de tudo que aconteceu
- 🔍 **Debugging detalhado**: Fácil identificar onde problemas ocorreram
- 📁 **Arquivo de log**: Pode ser salvo para análise posterior
- 🔄 **Reprodutibilidade**: Sequência exata de eventos preservada

### Monitoramento em Tempo Real (mode='realtime')
- 👁️ **Feedback visual imediato**: Vê o progresso acontecendo
- 🎯 **Foco no essencial**: Apenas informações importantes visíveis
- 📱 **Interface moderna**: Aparência de aplicativo profissional
- 💻 **Economia de espaço**: Terminal não fica sobrecarregado

### Modo Híbrido (mode='both')
- 🎯 **Melhor de ambos**: Monitoramento visual + registro de eventos
- 🚨 **Alertas importantes**: Logs especiais para descobertas importantes
- 📊 **Dashboard contínuo**: Para acompanhar progresso geral
- 📝 **Log seletivo**: Apenas eventos significativos são registrados

### Modo Silencioso (mode='silent')
- ⚡ **Performance máxima**: Zero overhead de I/O
- 🤖 **Automação**: Ideal para scripts e sistemas automatizados
- 📏 **Medições precisas**: Timing sem interferência de I/O
- 🔧 **Produção**: Para sistemas em produção onde apenas resultado importa
