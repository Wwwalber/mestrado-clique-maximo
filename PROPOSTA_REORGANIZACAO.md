## 📁 PROPOSTA DE REORGANIZAÇÃO DO PROJETO

### 🎯 **NOVA ESTRUTURA ORGANIZACIONAL**

```
mestrado-clique-maximo/
│
├── 📁 algorithms/                    # ALGORITMOS PRINCIPAIS
│   ├── __init__.py                  # Pacote Python
│   ├── clisat_exact.py              # Algoritmo CliSAT (exato)
│   ├── grasp_heuristic.py           # Algoritmo GRASP (heurístico)
│   └── algorithm_interface.py       # Interface comum dos algoritmos
│
├── 📁 data/                         # GERENCIAMENTO DE DADOS
│   ├── __init__.py                  # Pacote Python
│   ├── dimacs_loader.py             # Carregador DIMACS
│   ├── instance_manager.py          # Gerenciador de instâncias
│   └── graph_utils.py               # Utilitários para grafos
│
├── 📁 experiments/                  # EXPERIMENTOS E BENCHMARKS
│   ├── __init__.py                  # Pacote Python
│   ├── apa_benchmark.py             # Benchmark principal da atividade
│   ├── results_generator.py         # Gerador de resultados
│   ├── results_analyzer.py          # Analisador de resultados
│   └── comparison_tools.py          # Ferramentas de comparação
│
├── 📁 tests/                        # TODOS OS TESTES
│   ├── __init__.py                  # Pacote Python
│   ├── test_algorithms.py           # Testes dos algoritmos
│   ├── test_data_loading.py         # Testes de carregamento
│   ├── test_experiments.py          # Testes dos experimentos
│   └── test_integration.py          # Testes de integração
│
├── 📁 scripts/                      # SCRIPTS DE EXECUÇÃO
│   ├── run_apa_activity.py          # Script principal da atividade
│   ├── download_datasets.py         # Download automático DIMACS
│   ├── quick_test.py                # Teste rápido
│   └── benchmark_runner.py          # Executor de benchmarks
│
├── 📁 config/                       # CONFIGURAÇÕES
│   ├── __init__.py                  # Pacote Python
│   ├── algorithm_params.py          # Parâmetros dos algoritmos
│   ├── experiment_config.py         # Configurações de experimentos
│   └── logging_config.py            # Configuração de logs
│
├── 📁 docs/                         # DOCUMENTAÇÃO
│   ├── ALGORITMOS.md                # Documentação dos algoritmos
│   ├── EXPERIMENTOS.md              # Documentação dos experimentos
│   ├── INSTALACAO.md                # Instruções de instalação
│   └── RESULTADOS.md                # Formato dos resultados
│
├── 📁 data_files/                   # ARQUIVOS DE DADOS
│   ├── dimacs/                      # Grafos DIMACS baixados
│   ├── instances/                   # Lista de instâncias da atividade
│   └── results/                     # Resultados dos experimentos
│
├── 📁 notebooks/                    # JUPYTER NOTEBOOKS (OPCIONAL)
│   ├── analysis.ipynb               # Análise de resultados
│   ├── visualization.ipynb          # Visualizações
│   └── exploration.ipynb            # Exploração de dados
│
├── requirements.txt                 # Dependências Python
├── setup.py                        # Setup do pacote
├── README.md                        # Documentação principal
├── .gitignore                       # Arquivos ignorados pelo Git
└── venv-clique/                     # Ambiente virtual (mantido)
```

### 🔧 **VANTAGENS DA NOVA ESTRUTURA**

#### **1. Separação Clara de Responsabilidades**
- **`algorithms/`**: Apenas os algoritmos principais
- **`data/`**: Tudo relacionado a dados e grafos
- **`experiments/`**: Experimentos e benchmarks
- **`tests/`**: Todos os testes organizados
- **`scripts/`**: Scripts executáveis

#### **2. Facilita Importações**
```python
# Importações claras e organizadas
from algorithms.clisat_exact import solve_maximum_clique_clisat
from algorithms.grasp_heuristic import solve_maximum_clique_grasp
from data.dimacs_loader import DIMACSLoader
from experiments.apa_benchmark import APABenchmark
```

#### **3. Facilita Manutenção**
- Cada módulo tem responsabilidade específica
- Fácil localizar arquivos relacionados
- Estrutura escalável para futuras adições

#### **4. Padrão Profissional**
- Segue convenções Python estabelecidas
- Estrutura similar a projetos open-source
- Facilita colaboração e compreensão

### 📋 **MAPEAMENTO: ARQUIVOS ATUAIS → NOVA ESTRUTURA**

| Arquivo Atual | Nova Localização | Motivo |
|---------------|------------------|---------|
| `src/clisat_algortithmb.py` | `algorithms/clisat_exact.py` | Algoritmo principal |
| `grasp_maximum_clique.py` | `algorithms/grasp_heuristic.py` | Algoritmo principal |
| `clique_heuristics.py` | `algorithms/algorithm_interface.py` | Interface comum |
| `src/dimacs_loader.py` | `data/dimacs_loader.py` | Gerenciamento de dados |
| `src/apa_instance_manager.py` | `data/instance_manager.py` | Gerenciamento de dados |
| `apa_results_generator.py` | `experiments/results_generator.py` | Experimentos |
| `test_*.py` | `tests/test_*.py` | Organização de testes |
| `run_apa_activity.py` | `scripts/run_apa_activity.py` | Script executável |
| `dimacs_data/` | `data_files/dimacs/` | Dados |
| `execution_results/` | `data_files/results/` | Resultados |

### 🚀 **IMPLEMENTAÇÃO**

#### **Etapa 1: Criar Nova Estrutura**
- Criar diretórios
- Criar arquivos `__init__.py`
- Configurar pacotes Python

#### **Etapa 2: Mover e Refatorar Arquivos**
- Mover arquivos para localizações corretas
- Ajustar imports
- Manter funcionalidade

#### **Etapa 3: Atualizar Documentação**
- README.md atualizado
- Documentação por módulo
- Instruções de uso

#### **Etapa 4: Validação**
- Executar todos os testes
- Verificar funcionalidades
- Confirmar imports

### ❓ **PRÓXIMOS PASSOS**

1. **Aprovação da estrutura proposta**
2. **Execução da reorganização**
3. **Testes de validação**
4. **Atualização da documentação**

Esta estrutura torna o projeto mais profissional, organizativo e fácil de manter!
