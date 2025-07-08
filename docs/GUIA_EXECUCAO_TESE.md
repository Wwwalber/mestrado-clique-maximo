# Guia de Execução Completa - Tese de Mestrado

## Análise Experimental: CliSAT vs. GRASP para o Problema do Clique Máximo

Este guia fornece instruções passo a passo para executar ambos os algoritmos em todas as instâncias e gerar os resultados formatados para sua tese de mestrado.

---

## 📋 Preparação

### 1. Verificar Estrutura do Projeto

Certifique-se de que o projeto está na estrutura reorganizada:

```
mestrado-clique-maximo/
├── algorithms/           # Algoritmos implementados
│   ├── clisat_exact.py      # Algoritmo exato CliSAT
│   ├── grasp_heuristic.py   # Heurística GRASP
│   └── algorithm_interface.py
├── data/                # Módulos de dados
├── experiments/         # Scripts de experimentos
│   └── results_generator.py
├── scripts/            # Scripts de execução
│   ├── batch_execution.py   # Script principal em lote
│   └── quick_test_batch.py  # Teste rápido
├── data_files/         # Dados e resultados
│   ├── dimacs_instances/    # Instâncias DIMACS
│   └── thesis_results/      # Resultados da tese
└── data/
    └── instances_apa.csv    # Lista de instâncias
```

### 2. Ativar Ambiente Virtual

```bash
cd /home/cliSAT_project/mestrado-clique-maximo
source venv-clique/bin/activate
```

### 3. Verificar Dependências

```bash
pip install pandas networkx numpy
```

---

## 🧪 Execução dos Experimentos

### Opção 1: Teste Rápido (Recomendado primeiro)

Execute um teste com instâncias pequenas para verificar se tudo está funcionando:

```bash
# Teste com 3 instâncias pequenas
python scripts/batch_execution.py --test-mode --output test_results
```

**Resultado esperado:**
- Arquivo CSV com resultados das 3 instâncias
- Tabela LaTeX formatada
- Log detalhado da execução

### Opção 2: Execução por Grupos

Para evitar tempos muito longos, execute por grupos de instâncias:

```bash
# Instâncias pequenas (até 400 vértices)
python scripts/batch_execution.py --group pequenas --output resultados_pequenas

# Instâncias médias (400-800 vértices)
python scripts/batch_execution.py --group medias --output resultados_medias --time-limit-exact 900

# Instâncias grandes (800-2000 vértices)
python scripts/batch_execution.py --group grandes --output resultados_grandes --time-limit-exact 1800

# Instâncias muito grandes (2000+ vértices)
python scripts/batch_execution.py --group muito_grandes --output resultados_muito_grandes --time-limit-exact 3600
```

### Opção 3: Execução Completa

Para executar todas as 37 instâncias de uma vez:

```bash
python scripts/batch_execution.py --group all --output resultados_completos --time-limit-exact 1800
```

**⚠️ Aviso:** A execução completa pode levar várias horas!

---

## 📊 Interpretação dos Resultados

### Arquivos Gerados

Para cada execução, são gerados os seguintes arquivos em `data_files/thesis_results/`:

1. **`resultados_YYYYMMDD_HHMMSS.csv`** - Resultados completos em CSV
2. **`resultados_YYYYMMDD_HHMMSS.tex`** - Tabela LaTeX formatada para a tese
3. **`resultados_simple_YYYYMMDD_HHMMSS.csv`** - CSV simplificado
4. **`batch_execution_YYYYMMDD_HHMMSS.log`** - Log detalhado da execução

### Colunas da Tabela de Resultados

| Coluna | Descrição |
|--------|-----------|
| `Instance` | Nome da instância DIMACS |
| `Nodes` | Número de vértices |
| `Edges` | Número de arestas |
| `Exact_Size` | Tamanho do clique máximo (CliSAT) |
| `Exact_Time` | Tempo de execução do CliSAT (segundos) |
| `Heuristic_Size` | Tamanho do clique encontrado (GRASP) |
| `Heuristic_Time` | Tempo de execução do GRASP (segundos) |
| `Quality` | Razão heurístico/exato (0.0 a 1.0) |
| `Speedup` | Aceleração (tempo_exato/tempo_heurístico) |
| `Exact_Status` | Status do algoritmo exato |
| `Heuristic_Status` | Status da heurística |

### Exemplo de Resultado

```
Instance     | Nodes | Edges | Exact_Size | Exact_Time | Heuristic_Size | Heuristic_Time | Quality | Speedup
-------------|-------|-------|------------|------------|----------------|----------------|---------|--------
C125.9       | 125   | 6963  | 34         | 2.451      | 34             | 0.003421       | 1.000   | 716.5x
brock200_2   | 200   | 9876  | 12         | 15.231     | 11             | 0.001234       | 0.917   | 12346.1x
keller4      | 171   | 9435  | 11         | 0.892      | 11             | 0.002156       | 1.000   | 413.8x
```

---

## 📈 Análise para a Tese

### Métricas Importantes

1. **Taxa de Sucesso:** Porcentagem de instâncias resolvidas por cada algoritmo
2. **Qualidade Média:** Média da razão heurístico/exato
3. **Soluções Ótimas:** Quantas vezes o GRASP encontrou a solução ótima (Quality = 1.0)
4. **Speedup Médio:** Quantas vezes mais rápido é o GRASP em relação ao CliSAT
5. **Escalabilidade:** Como o desempenho varia com o tamanho da instância

### Estatísticas Automáticas

O script gera automaticamente:

- Resumo estatístico completo
- Contagem de soluções ótimas
- Análise de speedup
- Taxa de conclusão por algoritmo

---

## 🔧 Configurações Avançadas

### Tempos Limite Personalizados

```bash
# Algoritmo exato: 30 minutos, Heurística: 2 minutos
python scripts/batch_execution.py --time-limit-exact 1800 --time-limit-heuristic 120
```

### Execução de Instâncias Específicas

Para testar instâncias específicas, edite temporariamente a lista em `batch_execution.py`:

```python
# No script, substitua:
instances = ['C125.9', 'brock200_2', 'keller4']  # Suas instâncias escolhidas
```

---

## 📋 Checklist de Execução

- [ ] Ambiente virtual ativado
- [ ] Dependências instaladas
- [ ] Teste rápido executado com sucesso
- [ ] Execução por grupos ou completa realizada
- [ ] Arquivos de resultado gerados
- [ ] Tabela LaTeX criada
- [ ] Estatísticas analisadas
- [ ] Resultados validados

---

## 🎯 Uso dos Resultados na Tese

### 1. Tabela de Resultados

Use o arquivo `.tex` gerado diretamente no LaTeX da sua tese:

```latex
\input{resultados_YYYYMMDD_HHMMSS.tex}
```

### 2. Análise Estatística

Use os dados do CSV para gerar gráficos e análises:

- Gráfico de dispersão: Qualidade vs. Tamanho da instância
- Histograma: Distribuição da qualidade
- Gráfico de barras: Speedup por grupo de instâncias

### 3. Discussão dos Resultados

O log detalhado fornece informações para discussão:

- Casos onde o GRASP encontrou a solução ótima
- Instâncias onde houve timeout
- Padrões de desempenho por tipo de instância

---

**Boa sorte com sua tese de mestrado! 🎓**
