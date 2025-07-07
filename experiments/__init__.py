"""
Experiments package for Maximum Clique Problem

Este pacote contém módulos para experimentos e benchmarks:
- Benchmark da atividade APA
- Geração de resultados
- Análise de resultados

Uso:
    from experiments.apa_benchmark import APABenchmark
    from experiments.results_generator import ResultsGenerator
"""

__version__ = "1.0.0"

try:
    from .apa_benchmark import APABenchmark
    from .results_generator import ResultsGenerator
    from .results_analyzer import ResultsAnalyzer
    
    __all__ = [
        'APABenchmark',
        'ResultsGenerator',
        'ResultsAnalyzer'
    ]
except ImportError:
    __all__ = []
