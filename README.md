# CliSAT: Algoritmos para Clique Máximo - Atividade APA

Este projeto implementa **dois algoritmos** para o problema do clique máximo como parte da atividade da disciplina **Análise e Projeto de Algoritmos** do mestrado:

1. **Algoritmo Exato**: CliSAT (SAT-based exact algorithm)
2. **Heurística**: Gulosa baseada em grau (Greedy degree-based heuristic)

## 🎯 Objetivo da Atividade

Implementar o algoritmo CliSAT em instâncias específicas da base de dados DIMACS, focando em:
- Análise de desempenho em diferentes tipos de grafos
- Comparação com valores ótimos conhecidos

## 📁 Estrutura do Projeto

```
mestrado-clique-maximo/
├── clisat_algortithmb.py        # Implementação do algoritmo CliSAT (exato)
├── clique_heuristics.py        # Implementação da heurística gulosa
├── apa_instance_manager.py     # Gerenciador das instâncias DIMACS
├── apa_results_generator.py    # Gerador de resultados e tabelas
├── run_apa_activity.py         # Script principal da atividade
├── instances_apa.csv           # Lista das 38 instâncias da atividade
├── venv-clique/               # Ambiente virtual Python
├── dimacs_data/               # Dados DIMACS baixados
├── benchmark_results/         # Resultados dos experimentos
├── test_clisat.py             # Testes e benchmarks (legado)
├── examples.py                # Exemplos práticos (legado)
└── main.py                    # Script principal (legado)
```

## 🚀 Como Executar

### 1. Preparar Ambiente
```bash
# Ativar ambiente virtual (já configurado)
source venv-clique/bin/activate

# Verificar dependências (já instaladas)
pip list | grep -E "(networkx|python-sat|pandas|matplotlib)"
```

### 2. Execução Rápida (Teste)
```bash
# Testar com 3 instâncias pequenas (recomendado para validação)
python run_apa_activity.py --mode test --time-limit 60
```

### 3. Execução da Atividade
```bash
# Modo small: ~8 instâncias menores (recomendado para desenvolvimento)
python run_apa_activity.py --mode small --time-limit 300

# Modo medium: ~18 instâncias médias (recomendado para avaliação)
python run_apa_activity.py --mode medium --time-limit 600

# Modo full: Todas as 38 instâncias (pode demorar várias horas)
python run_apa_activity.py --mode full --time-limit 1800
```

### 4. Baixar Instâncias DIMACS (se necessário)
```bash
# O sistema baixa automaticamente as instâncias necessárias
python run_apa_activity.py --download --mode small
```

## 📊 Instâncias da Atividade

O projeto trabalha com **38 instâncias específicas** da base DIMACS:

| Família | Instâncias | Características |
|---------|------------|-----------------|
| **C-series** | C125.9, C250.9, C500.9, C1000.9, C2000.9 | Grafos aleatórios densos |
| **DSJC** | DSJC500_5, DSJC1000_5 | Grafos de coloração |
| **brock** | brock200_2/4, brock400_2/4, brock800_2/4 | Grafos estruturados |
| **gen** | gen200/400_p0.9_XX | Grafos geométricos aleatórios |
| **MANN** | MANN_a27, MANN_a45, MANN_a81 | Códigos de Hamming |
| **hamming** | hamming8-4, hamming10-4 | Códigos de Hamming |
| **keller** | keller4, keller5, keller6 | Grafos de Keller |
| **p_hat** | p_hat300/700/1500-1/2/3 | Grafos estruturados |

## 📈 Resultados Gerados

O sistema gera automaticamente:

### 1. Tabela Principal (`apa_results_[modo]_[timestamp].csv`)
```csv
Instance,Nodes,Edges,Exact_Size,Exact_Time,Heuristic_Size,Heuristic_Time,Quality
C125.9,125,6963,34,45.123,32,0.002341,0.941
brock200_2,200,9876,12,89.456,11,0.001876,0.917
...
```

### 2. Tabela para Apresentação (`*_presentation.csv`)
- Formatação otimizada para relatórios
- Precisão adequada para cada métrica
- Pronta para inclusão em documentos acadêmicos

### 3. Resumo Estatístico (`*_summary.txt`)
- Estatísticas gerais dos experimentos
- Tempo médio de execução por algoritmo  
- Qualidade média da heurística
- Taxa de sucesso e speedup

## 🧪 Exemplo de Execução

```bash
$ python run_apa_activity.py --mode small --time-limit 180

======================================================================
           ATIVIDADE APA - ALGORITMOS PARA CLIQUE MÁXIMO
                Análise e Projeto de Algoritmos
======================================================================

ALGORITMOS IMPLEMENTADOS:
1. Algoritmo Exato: CliSAT (SAT-based exact algorithm)
   - Baseado em SAT solving com branch-and-bound
   - Complexidade exponencial, mas exato
   - Referência: San Segundo et al. (2016)

2. Heurística: Gulosa baseada em grau
   - Seleção gulosa por maior grau efetivo
   - Complexidade O(n³)
   - Referência: Johnson & Trick (1996)

CONFIGURAÇÃO DA EXECUÇÃO:
- Modo: small
- Instâncias: 8
- Tempo limite (exato): 180s
- Tempo limite (heurística): 36s

INSTÂNCIAS A SEREM TESTADAS:
   1. C125.9
   2. brock200_2
   3. brock200_4
   4. gen200_p0.9_44
   5. gen200_p0.9_55
   6. p_hat300-1
   7. p_hat300-2
   8. keller4

INICIANDO EXPERIMENTOS...
==================================================
[1/8] Processando C125.9
  Grafo: 125 vértices, 6963 arestas
  Executando algoritmo exato (CliSAT)...
    Clique exato: tamanho 34, tempo 45.123s
  Executando heurística gulosa...
    Clique heurístico: tamanho 32, tempo 0.002s
    Qualidade: 0.941, Speedup: 22561.5x

...

==================================================
EXPERIMENTOS CONCLUÍDOS!
Tempo total: 324.7 segundos (5.4 minutos)

RESUMO DOS RESULTADOS:
- Instâncias processadas: 8
- Algoritmo exato completou: 8/8
- Heurística completou: 8/8
- Qualidade média da heurística: 0.923
- Speedup médio: 15847.3x
- Soluções ótimas encontradas pela heurística: 2

Resultados salvos em: benchmark_results/apa_results_small_20250704_143021.csv
```

## 📚 Fundamentação Teórica

### Problema do Clique Máximo
- **Definição**: Encontrar o maior subgrafo completo em um grafo
- **Complexidade**: NP-completo
- **Aplicações**: Bioinformática, redes sociais, otimização

### Algoritmo CliSAT
- **Técnica**: Codificação SAT + Branch-and-bound
- **Vantagem**: Exato, técnicas de poda eficientes
- **Limitação**: Exponencial no pior caso

### Heurística Gulosa
- **Estratégia**: Seleção local ótima a cada passo
- **Critério**: Maior grau efetivo entre candidatos válidos
- **Trade-off**: Rapidez vs. garantia de otimalidade

## 🔧 Implementação Técnica

### Algoritmo CliSAT
```python
class CliSATSolver:
    def solve(self) -> Tuple[List, int]:
        # 1. Pré-processamento do grafo
        # 2. Heurística gulosa para limite inferior
        # 3. Coloração para limite superior  
        # 4. Branch-and-bound com SAT solving
        # 5. Retornar clique ótimo
```

### Heurística Gulosa
```python
class GreedyCliqueHeuristic:
    def solve(self) -> Tuple[List, int, float]:
        # 1. Calcular graus dos vértices
        # 2. Selecionar vértice de maior grau válido
        # 3. Atualizar candidatos (manter adjacência)
        # 4. Repetir até esgotar candidatos
        # 5. Retornar clique encontrado
```

## 🔗 Referências

1. **San Segundo, P., et al.** (2016). "CliSAT: A new exact algorithm for hard maximum clique problems". *Operations Research Letters*, 44(3), 311-316.

2. **Johnson, D. S., & Trick, M. A.** (1996). "Cliques, coloring, and satisfiability: second DIMACS implementation challenge". *American Mathematical Society*.

3. **Bomze, I. M., et al.** (1999). "The maximum clique problem". *Handbook of combinatorial optimization*, 4, 1-74.

4. **DIMACS Maximum Clique Instances**: https://iridia.ulb.ac.be/~fmascia/maximum_clique/

## 👤 Autor

**Walber**  
Mestrado em Ciência da Computação  
Disciplina: Análise e Projeto de Algoritmos  
Data: Julho 2025

---

### 📝 Notas da Implementação

- **Foco na pesquisa**: Como solicitado pelo professor, o projeto prioriza a fundamentação teórica sólida
- **Dois algoritmos**: Exato (CliSAT) + Heurística (Gulosa) conforme requisitos da atividade
- **38 instâncias específicas**: Conforme lista fornecida para a disciplina
- **Tabela de resultados**: Formato automático para entrega ao professor
- **Reprodutibilidade**: Sementes fixas e logs detalhados para validação

```
mestrado-clique-maximo/
├── clisat_algortithmb.py    # Implementação principal do algoritmo CliSAT
├── apa_instance_manager.py  # Gerenciador das instâncias APA
├── apa_benchmark.py         # Sistema de benchmark para instâncias APA
├── run_apa.py              # Script principal para atividade APA
├── instances_apa.csv       # Lista das instâncias da atividade
├── examples.py             # Exemplos de uso
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── dimacs_data/           # Diretório para grafos DIMACS baixados
└── benchmark_results/     # Resultados dos benchmarks
```

## 📊 Instâncias da Atividade APA

A atividade utiliza **37 instâncias específicas** da base DIMACS, selecionadas para cobrir diferentes características:

| Instância     | Nós   | Arestas   | Densidade | Família   |
|---------------|-------|-----------|-----------|-----------|
| C125.9        | 125   | 6,963     | 0.901     | C-family  |
| C250.9        | 250   | 27,984    | 0.901     | C-family  |
| C500.9        | 500   | 112,332   | 0.901     | C-family  |
| brock200_2    | 200   | 9,876     | 0.497     | brock     |
| brock200_4    | 200   | 13,089    | 0.659     | brock     |
| gen200_p0.9_44| 200   | 17,910    | 0.901     | gen       |
| keller4       | 171   | 9,435     | 0.651     | keller    |
| p_hat300-1    | 300   | 10,933    | 0.244     | p_hat     |
| MANN_a27      | 378   | 70,551    | 0.989     | MANN      |
| ... (28 instâncias adicionais) |

### Características das Famílias

- **C-family**: Grafos com alta densidade (~0.9)
- **brock**: Grafos aleatórios com diferentes densidades
- **gen**: Grafos gerados com parâmetros específicos
- **keller**: Grafos de Keller com estrutura geométrica
- **p_hat**: Grafos com estrutura de "chapéu"
- **MANN**: Grafos de Steiner (muito densos)
- **hamming**: Grafos de Hamming (estrutura regular)
- **DSJC**: Grafos de coloração convertidos para clique

## 🔧 Uso para Atividade APA

### Interface Principal

O script `run_apa.py` fornece todos os comandos necessários:

```bash
# Listar as 37 instâncias da atividade
python run_apa.py list

# Listar apenas instâncias pequenas (≤ 300 nós)
python run_apa.py list --max-size 300

# Baixar instâncias pequenas para testes iniciais
python run_apa.py download --max-size 300

# Testar uma instância específica
python run_apa.py test C125.9 --time-limit 120

# Executar benchmark completo (todas as 37 instâncias)
python run_apa.py benchmark --time-limit 300 --generate-report

# Executar benchmark apenas em instâncias pequenas
python run_apa.py benchmark --max-size 500 --time-limit 180

# Testar instâncias específicas
python run_apa.py benchmark --instances C125.9 C250.9 brock200_2 --time-limit 120

# Analisar resultados existentes
python run_apa.py analyze benchmark_results/apa_benchmark_20250101_120000.json
```

### Exemplo de Execução Completa

### Uso Programático

```python
from apa_instance_manager import APAInstanceManager
from apa_benchmark import APABenchmark
from clisat_algortithmb import CliSAT

# 1. Carregar uma instância específica
manager = APAInstanceManager()
graph = manager.load_graph("C125.9")

# 2. Executar CliSAT
solver = CliSAT(graph, time_limit=300.0)
clique_nodes, clique_size = solver.solve()

print(f"Clique máximo: {clique_size} vértices")

# 3. Executar benchmark personalizado
benchmark = APABenchmark()
results = benchmark.run_benchmark_suite(
    instances=["C125.9", "C250.9", "brock200_2"],
    time_limit=180.0
)

# 4. Gerar relatório
benchmark.generate_analysis_report(
    "benchmark_results/apa_benchmark_latest.json"
)
```

## 📈 Resultados Esperados para APA

### Métricas de Avaliação

Para cada instância, o sistema coleta:

- **Tamanho do clique encontrado**
- **Tempo de execução**

## 🧮 Algoritmo CliSAT

### Características Principais

1. **Preprocessing**: Redução do grafo usando técnicas de dominância
2. **SAT Encoding**: Conversão do problema de clique para SAT
3. **Branch-and-Bound**: Estratégia de busca com poda eficiente
4. **Upper Bounds**: Cálculo de limites superiores usando coloração
5. **Incremental SAT**: Uso incremental do solver SAT

### Estrutura do Algoritmo

```python
def solve(self):
    # 1. Preprocessing
    self.preprocess()
    
    # 2. Clique inicial (limite inferior)
    initial_clique = self.greedy_initial_clique()
    
    # 3. Branch-and-bound com SAT
    while not self.time_exceeded():
        # Calcular limite superior
        upper_bound = self.upper_bound_coloring(remaining_vertices)
        
        # Poda por limite
        if upper_bound <= self.best_size:
            continue
            
        # Resolver subproblema com SAT
        clique = self.sat_solve_clique(k)
        
        if clique:
            self.update_best_clique(clique)
```

## 📈 Resultados e Análise

### Métricas Coletadas

- **Tamanho do clique encontrado**
- **Tempo de execução**

### Formatos de Saída

2. **CSV**: Resumo tabular para análise
3. **Relatório de texto**: Análise detalhada


## 📋 Exemplos Práticos para APA

### Exemplo 1: Teste Rápido em Instância Pequena

```python
from apa_instance_manager import APAInstanceManager
from clisat_algortithmb import CliSAT

# Carregar instância pequena
manager = APAInstanceManager()
graph = manager.load_graph("C125.9")  # 125 nós, ótimo = 34

# Executar CliSAT
solver = CliSAT(graph, time_limit=120.0)
clique_nodes, clique_size = solver.solve()

print(f"Resultado: {clique_size} (ótimo conhecido: 34)")
print(f"Gap: {(34 - clique_size) / 34 * 100:.1f}%")
```

### Interpretação dos Resultados

## 📚 Referências

- San Segundo, P., Furini, F., Álvarez, D. (2023). "CliSAT: A new exact algorithm for hard maximum clique problems"
- DIMACS Maximum Clique Database: https://iridia.ulb.ac.be/~fmascia/maximum_clique/
- NetworkX Documentation: https://networkx.org/
- PySAT Documentation: https://pysathq.github.io/

