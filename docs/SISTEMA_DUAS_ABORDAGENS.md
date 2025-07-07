# Sistema de Comparação: CliSAT vs GRASP

## Arquitetura Final - Duas Abordagens Principais

O sistema foi finalizado com **apenas 2 abordagens** para o problema do clique máximo, conforme solicitado:

### 1. CliSAT (Algoritmo Exato)
- **Arquivo**: `src/clisat_algortithmb.py`
- **Função**: `solve_maximum_clique_clisat(graph, time_limit)`
- **Tipo**: Algoritmo exato baseado em SAT
- **Características**:
  - Garante solução ótima
  - Adequado para instâncias pequenas/médias
  - Tempo de execução pode ser exponencial

### 2. GRASP (Heurística de Alta Qualidade)
- **Arquivo**: `grasp_maximum_clique.py` + interface em `clique_heuristics.py`
- **Função**: `solve_maximum_clique_heuristic(graph, alpha, max_iterations, time_limit)`
- **Tipo**: Metaheurística GRASP
- **Características**:
  - Construção gulosa randomizada + busca local
  - Boa qualidade de soluções
  - Tempo de execução controlado
  - Configurável através de parâmetros

## Substituição Realizada

### ❌ Antiga Estrutura (Removida)
```python
# Heurística gulosa simples (substituída)
class GreedyCliqueHeuristic:
    def solve(self) -> Tuple[List, int, float]:
        # Algoritmo guloso baseado em grau
```

### ✅ Nova Estrutura (Implementada)
```python
# Heurística GRASP avançada
class GRASPCliqueHeuristic:
    def solve(self) -> Tuple[List, int, float]:
        # Metaheurística GRASP com construção randomizada + busca local
```

## Parâmetros GRASP

### Principais Parâmetros
- **alpha** (0.0-1.0): Controla aleatoriedade (0=guloso, 1=aleatório)
- **max_iterations**: Número máximo de iterações
- **time_limit**: Limite de tempo em segundos
- **seed**: Semente para reprodutibilidade

### Configurações Recomendadas
- **Rápida**: `alpha=0.3, max_iterations=50, time_limit=30s`
- **Balanceada**: `alpha=0.3, max_iterations=100, time_limit=60s`
- **Intensiva**: `alpha=0.3, max_iterations=500, time_limit=300s`

## Interface Unificada

### Para Benchmark/Experimentos
```python
from clique_heuristics import solve_maximum_clique_heuristic
from src.clisat_algortithmb import solve_maximum_clique_clisat

# CliSAT (exato)
clique_exact, size_exact, time_exact = solve_maximum_clique_clisat(graph, time_limit=300)

# GRASP (heurístico)
clique_heur, size_heur, time_heur = solve_maximum_clique_heuristic(
    graph, alpha=0.3, max_iterations=100, time_limit=60
)
```

## Arquivos Atualizados

### Principais Modificações
1. **`clique_heuristics.py`**: Substituído `GreedyCliqueHeuristic` por `GRASPCliqueHeuristic`
2. **`apa_results_manager.py`**: Removidas referências à classe antiga `CliqueHeuristics`
3. **Scripts de benchmark**: Mantida compatibilidade através da interface `solve_maximum_clique_heuristic`

### Novos Arquivos
- **`grasp_maximum_clique.py`**: Implementação completa do GRASP
- **`test_grasp_integration.py`**: Teste de validação da integração

## Testes de Validação

### Resultados dos Testes
```
Configuração               | α    | Tamanho | Qualidade | Tempo   | Válido
Guloso puro               | 0.0  | 4       | 100.0%    | 0.002s  | ✓
GRASP balanceado          | 0.3  | 4       | 100.0%    | 0.004s  | ✓
GRASP mais aleatório      | 0.7  | 4       | 100.0%    | 0.006s  | ✓
Totalmente aleatório      | 1.0  | 4       | 100.0%    | 0.002s  | ✓
```

## Status do Sistema

### ✅ Concluído
- [x] Implementação completa do GRASP
- [x] Substituição da heurística gulosa simples
- [x] Interface compatível mantida
- [x] Testes de validação aprovados
- [x] Sistema com apenas 2 abordagens principais

### 🎯 Próximos Passos (Opcionais)
- [ ] Executar benchmarks completos CliSAT vs GRASP
- [ ] Gerar tabelas de resultados comparativos
- [ ] Análise estatística das diferenças de performance
- [ ] Documentação final dos experimentos

## Comparação Teórica

| Aspecto | CliSAT (Exato) | GRASP (Heurístico) |
|---------|----------------|-------------------|
| **Garantia** | Solução ótima | Heurística de alta qualidade |
| **Complexidade** | Exponencial (pior caso) | O(k × n³) |
| **Escalabilidade** | Limitada por tempo | Boa para grandes instâncias |
| **Configurabilidade** | Tempo limite | Múltiplos parâmetros |
| **Uso Recomendado** | Instâncias pequenas/médias | Todas as instâncias |

---

**Data**: Julho 2025  
**Status**: ✅ **SISTEMA FINALIZADO COM 2 ABORDAGENS**
