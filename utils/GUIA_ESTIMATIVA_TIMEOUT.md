# Guia de Implementação: Estimativa de Tempo para Timeout

## Resumo da Solução

Esta solução calcula estimativas de tempo quando os algoritmos excedem o limite de tempo, **sem fazer alterações significativas** no código existente. Usa apenas dados que já são coletados durante a execução.

## Como Funciona

### 1. Para o CliSAT (Algoritmo Exato)

**Dados já disponíveis:**
- `self.stats['nodes_explored']` - número de nós explorados na árvore de busca
- `time.time() - self.start_time` - tempo decorrido
- `self.n` - número de vértices do grafo
- `self.lb` - tamanho do melhor clique encontrado

**Cálculo da estimativa:**
```python
taxa_exploração = nós_explorados / tempo_atual
espaço_restante = nós_explorados * (tamanho_grafo - melhor_clique)
tempo_estimado = espaço_restante / taxa_exploração
```

**Justificativa matemática:**
- O CliSAT explora uma árvore de busca exponencial
- A taxa atual de exploração indica a velocidade do algoritmo
- O espaço restante é proporcional ao gap entre o bound atual e o tamanho do grafo

### 2. Para o GRASP (Heurística)

**Dados já disponíveis:**
- `iteration` - iteração atual do loop principal
- `time.time() - start_time` - tempo decorrido
- `self.params.max_iterations` - número máximo de iterações
- `self.stats.clique_sizes_history` - histórico de tamanhos encontrados

**Cálculo da estimativa:**
```python
taxa_progresso = iteração_atual / tempo_atual
iterações_restantes = max_iterações - iteração_atual
tempo_estimado = iterações_restantes / taxa_progresso
```

**Justificativa matemática:**
- O GRASP tem número fixo de iterações
- A taxa de progresso indica velocidade de processamento
- Estimativa linear baseada no progresso atual

## Implementação Simples

### Passo 1: Adicionar ao CliSAT

No método `solve()` do CliSAT, onde já existe a verificação de timeout:

```python
if self._time_exceeded():
    # ADICIONAR ESTAS LINHAS:
    from utils.timeout_estimator import TimeoutEstimator
    
    current_time = time.time() - self.start_time
    estimate = TimeoutEstimator.estimate_clisat_time(
        stats=self.stats,
        current_time=current_time,
        graph_size=self.n,
        current_bound=self.lb
    )
    
    print(TimeoutEstimator.format_time_estimate(estimate))
    
    # Salvar para relatório
    self.timeout_estimate = estimate
    
    logger.warning("Tempo limite excedido")
    break
```

### Passo 2: Adicionar ao GRASP

No método `solve()` do GRASP, onde já existe a verificação de timeout:

```python
if time.time() - start_time >= self.params.time_limit:
    # ADICIONAR ESTAS LINHAS:
    from utils.timeout_estimator import TimeoutEstimator
    
    current_time = time.time() - start_time
    estimate = TimeoutEstimator.estimate_grasp_time(
        iteration=iteration,
        current_time=current_time,
        max_iterations=self.params.max_iterations,
        best_clique_size=self.best_clique_size,
        improvement_history=self.stats.clique_sizes_history
    )
    
    print(TimeoutEstimator.format_time_estimate(estimate))
    
    # Salvar para relatório
    self.timeout_estimate = estimate
    
    return False  # para sair do loop
```

## Exemplo de Saída

Quando há timeout, o sistema mostrará:

```
📊 ESTIMATIVA DE TEMPO:
   ⏱️  Tempo restante estimado: 2.5h
   🎯 Tempo total estimado: 3.2h
   📈 Método: Baseado na taxa de exploração de nós da árvore de busca
   💡 Detalhes: Taxa atual: 1250.5 nós/s. Espaço restante estimado: 11,234,567 nós
```

## Dados para o Relatório

O objeto `estimate` contém todos os dados necessários:

```python
{
    'estimated_total_time': 11520.0,      # segundos
    'estimated_remaining_time': 9000.0,   # segundos
    'current_time': 2520.0,               # segundos
    'exploration_rate': 1250.5,           # nós/segundo (CliSAT)
    'nodes_explored': 3151260,            # nós explorados
    'calculation_method': 'Baseado na taxa de exploração...',
    'explanation': 'Taxa atual: 1250.5 nós/s...'
}
```

## Vantagens da Solução

1. **Sem alterações significativas** - usa dados já coletados
2. **Matematicamente justificável** - baseado em taxas de progresso observadas
3. **Implementação simples** - apenas algumas linhas de código
4. **Informativo** - fornece contexto sobre o cálculo realizado

## Precisão da Estimativa

- **CliSAT**: Estimativa conservadora baseada na exploração atual
- **GRASP**: Estimativa mais precisa devido à natureza iterativa
- **Ambos**: Melhor precisão quanto mais tempo o algoritmo já executou

## Como Citar no Relatório

"A estimativa de tempo para casos de timeout foi calculada com base na taxa de progresso observada durante a execução parcial do algoritmo, extrapolando linearmente o tempo necessário para completar o espaço de busca restante."
