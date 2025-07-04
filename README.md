# CliSAT: Algoritmo SAT para Clique Máximo - Atividade APA

Este projeto implementa o algoritmo CliSAT para a disciplina de **Análise e Projeto de Algoritmos** do mestrado. O CliSAT é um solver exato baseado em SAT (Boolean Satisfiability) que combina técnicas de SAT solving com branch-and-bound para encontrar cliques máximos de forma eficiente.

## 🎯 Objetivo da Atividade

Implementar e avaliar o algoritmo CliSAT em instâncias específicas da base de dados DIMACS, focando em:
- Análise de desempenho em diferentes tipos de grafos
- Comparação com valores ótimos conhecidos
- Estudo da eficiência do algoritmo em grafos de diferentes características

## 📁 Estrutura do Projeto

```
mestrado-clique-maximo/
├── clisat_algorithm.py      # Implementação principal do algoritmo CliSAT
├── apa_instance_manager.py  # Gerenciador das instâncias APA
├── apa_benchmark.py         # Sistema de benchmark para instâncias APA
├── run_apa.py              # Script principal para atividade APA
├── instances_apa.csv       # Lista das instâncias da atividade
├── examples.py             # Exemplos de uso
├── test_clisat.py          # Testes unitários
├── requirements.txt        # Dependências Python
├── README.md              # Este arquivo
├── dimacs_data/           # Diretório para grafos DIMACS baixados
└── benchmark_results/     # Resultados dos benchmarks
```

## 🚀 Instalação e Configuração

### 1. Clonar o repositório
```bash
git clone <url-do-repositorio>
cd mestrado-clique-maximo
```

### 2. Criar ambiente virtual
```bash
python -m venv venv-clique
source venv-clique/bin/activate  # Linux/Mac
# ou
venv-clique\Scripts\activate     # Windows
```

### 3. Instalar dependências
```bash
pip install -r requirements.txt
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

```bash
# 1. Baixar todas as instâncias
python run_apa.py download

# 2. Executar benchmark completo com relatório
python run_apa.py benchmark --time-limit 300 --generate-report

# 3. Os resultados serão salvos em:
#    - benchmark_results/apa_benchmark_YYYYMMDD_HHMMSS.json
#    - benchmark_results/relatorio_apa.txt
#    - benchmark_results/*.png (gráficos)
```

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
- **Gap em relação ao ótimo conhecido** (quando disponível)
- **Taxa de otimalidade** (clique ótimo encontrado vs. tentativas)
- **Estatísticas do solver** (chamadas SAT, nós explorados, etc.)

### Valores Ótimos Conhecidos

O sistema inclui os valores ótimos conhecidos para todas as 37 instâncias:

| Instância     | Ótimo | Instância     | Ótimo | Instância     | Ótimo |
|---------------|-------|---------------|-------|---------------|-------|
| C125.9        | 34    | brock200_2    | 12    | gen200_p0.9_44| 44    |
| C250.9        | 44    | brock200_4    | 17    | gen200_p0.9_55| 55    |
| C500.9        | 57    | brock400_2    | 29    | hamming8-4    | 16    |
| ... (dados completos no sistema) |

### Categorias de Desempenho

**Instâncias Pequenas (≤ 300 nós)**
- Meta: Taxa de otimalidade > 80%
- Tempo médio esperado: < 60s

**Instâncias Médias (300-800 nós)**
- Meta: Taxa de otimalidade > 60%
- Tempo médio esperado: < 300s

**Instâncias Grandes (> 800 nós)**
- Meta: Gap médio < 20%
- Análise de escalabilidade

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
- **Número de chamadas SAT**
- **Nós explorados no branch-and-bound**
- **Reduções por preprocessing**
- **Gap em relação à solução conhecida**

### Formatos de Saída

1. **JSON**: Resultados completos estruturados
2. **CSV**: Resumo tabular para análise
3. **Relatório de texto**: Análise detalhada
4. **Gráficos**: Visualizações automáticas

### Gráficos Gerados

- Tamanho do grafo vs Tempo de execução
- Densidade vs Tamanho do clique
- Distribuição dos gaps
- Taxa de otimalidade por faixa de tamanho

## 🧪 Execução dos Testes para APA

### 1. Teste de Verificação (Instâncias Pequenas)

```bash
# Baixar e testar instâncias pequenas primeiro
python run_apa.py download --max-size 300
python run_apa.py benchmark --max-size 300 --time-limit 120 --generate-report
```

### 2. Benchmark Completo da Atividade

```bash
# Baixar todas as 37 instâncias
python run_apa.py download

# Executar benchmark completo (pode levar várias horas)
python run_apa.py benchmark --time-limit 300 --generate-report
```

### 3. Análise por Categorias

```bash
# Testar apenas instâncias específicas por família
python run_apa.py benchmark --instances C125.9 C250.9 C500.9 --time-limit 180

# Analisar instâncias por densidade
python run_apa.py test p_hat300-1  # Baixa densidade
python run_apa.py test brock200_2  # Média densidade  
python run_apa.py test MANN_a27    # Alta densidade
```

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

### Exemplo 2: Benchmark de Família Específica

```python
from apa_benchmark import APABenchmark

benchmark = APABenchmark()

# Testar todas as instâncias da família C
c_family = ["C125.9", "C250.9", "C500.9", "C1000.9", "C2000.9"]
results = benchmark.run_benchmark_suite(
    instances=c_family,
    time_limit=300.0
)

# Analisar escalabilidade
for result in results:
    print(f"{result['instance_name']}: "
          f"{result['found_clique_size']} em {result['execution_time']:.1f}s")
```

### Exemplo 3: Comparação de Densidades

```python
# Instâncias com diferentes densidades
instances_by_density = {
    'Alta densidade (>0.8)': ['C125.9', 'gen200_p0.9_44', 'MANN_a27'],
    'Média densidade (0.4-0.8)': ['brock200_2', 'keller4', 'brock200_4'],
    'Baixa densidade (<0.4)': ['p_hat300-1', 'p_hat700-1', 'p_hat1500-1']
}

for category, instances in instances_by_density.items():
    print(f"\n=== {category} ===")
    results = benchmark.run_benchmark_suite(instances=instances)
    # Análise específica por categoria...
```

## � Análise de Resultados

### Saídas Geradas

Após executar o benchmark, o sistema gera:

1. **Arquivo JSON** (`apa_benchmark_YYYYMMDD_HHMMSS.json`)
   - Resultados completos estruturados
   - Todas as métricas coletadas
   - Timestamps e configurações

2. **Relatório de Texto** (`relatorio_apa.txt`)
   - Resumo executivo
   - Estatísticas gerais
   - Top 5 melhores/piores resultados
   - Análise por família de grafos

3. **Gráficos de Análise** (arquivos PNG)
   - `tempo_vs_tamanho.png`: Escalabilidade temporal
   - `gap_vs_densidade.png`: Qualidade vs. estrutura
   - `distribuicao_tempos.png`: Distribuição de performance
   - `tempos_por_familia.png`: Análise por família

### Interpretação dos Resultados

**Gap Percentual**: `(ótimo_conhecido - resultado_encontrado) / ótimo_conhecido * 100`
- Gap = 0%: Solução ótima encontrada
- Gap < 5%: Excelente qualidade
- Gap < 15%: Boa qualidade
- Gap > 20%: Necessita análise adicional

**Análise Temporal**:
- Verificar escalabilidade com o tamanho do grafo
- Identificar famílias mais desafiadoras
- Comparar com limites teóricos de complexidade

## 🤝 Contribuindo

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📚 Referências

- San Segundo, P., Furini, F., Álvarez, D. (2023). "CliSAT: A new exact algorithm for hard maximum clique problems"
- DIMACS Maximum Clique Database: https://iridia.ulb.ac.be/~fmascia/maximum_clique/
- NetworkX Documentation: https://networkx.org/
- PySAT Documentation: https://pysathq.github.io/

## 📄 Licença

Este projeto está licenciado sob a licença MIT - veja o arquivo LICENSE para detalhes.

## 👥 Autores

- **Seu Nome** - Implementação inicial - [seu-github](https://github.com/seu-usuario)

## 🙏 Agradecimentos

- Professores e orientadores do programa de mestrado
- Comunidade científica pelos algoritmos e datasets
- Desenvolvedores das bibliotecas utilizadas
