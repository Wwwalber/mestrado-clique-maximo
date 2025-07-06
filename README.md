# CliSAT: Algoritmo SAT para Clique Máximo - Atividade APA

Este projeto implementa o algoritmo CliSAT para a disciplina de **Análise e Projeto de Algoritmos** do mestrado. O CliSAT é um solver exato baseado em SAT (Boolean Satisfiability) que combina técnicas de SAT solving com branch-and-bound para encontrar cliques máximos de forma eficiente.

## 🎯 Objetivo da Atividade

Implementar o algoritmo CliSAT em instâncias específicas da base de dados DIMACS, focando em:
- Análise de desempenho em diferentes tipos de grafos
- Comparação com valores ótimos conhecidos

## 📁 Estrutura do Projeto

```
mestrado-clique-maximo/
├── clisat_algorithm.py      # Implementação principal do algoritmo CliSAT
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
from clisat_algorithm import CliSATSolver

# 1. Carregar uma instância específica
manager = APAInstanceManager()
graph = manager.load_graph("C125.9")

# 2. Executar CliSAT
solver = CliSATSolver(graph, time_limit=300.0)
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
from clisat_algorithm import CliSATSolver

# Carregar instância pequena
manager = APAInstanceManager()
graph = manager.load_graph("C125.9")  # 125 nós, ótimo = 34

# Executar CliSAT
solver = CliSATSolver(graph, time_limit=120.0)
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

