#!/usr/bin/env python3
"""
Analisador de Resultados do CliSAT

Este script analisa os resultados da execução estratégica do CliSAT,
gera visualizações e produz a tabela final no formato solicitado.

Funcionalidades:
- Análise estatística dos resultados
- Geração de gráficos de performance
- Tabela formatada para o relatório
- Comparação com ótimos conhecidos
- Relatório de qualidade dos algoritmos

Autor: Walber
Data: Julho 2025
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from pathlib import Path
import json
import argparse
from typing import Dict, List, Optional
import logging

# Configurar estilo dos gráficos
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CliSATResultsAnalyzer:
    """
    Classe para análise e visualização dos resultados do CliSAT.
    """
    
    def __init__(self, results_dir: str = "execution_results"):
        """
        Inicializar analisador.
        
        Args:
            results_dir: Diretório com os resultados
        """
        self.results_dir = Path(results_dir)
        self.plots_dir = self.results_dir / "plots"
        self.reports_dir = self.results_dir / "reports"
        
        # Criar diretórios
        self.plots_dir.mkdir(exist_ok=True)
        self.reports_dir.mkdir(exist_ok=True)
        
        # Carregar resultados
        self.results_df = None
        self.load_results()

    def load_results(self):
        """
        Carregar resultados do arquivo CSV.
        """
        results_file = self.results_dir / "clisat_final_results.csv"
        
        if not results_file.exists():
            logger.warning(f"Arquivo de resultados não encontrado: {results_file}")
            return
        
        try:
            self.results_df = pd.read_csv(results_file)
            logger.info(f"Resultados carregados: {len(self.results_df)} instâncias")
        except Exception as e:
            logger.error(f"Erro ao carregar resultados: {e}")

    def generate_summary_statistics(self) -> Dict:
        """
        Gerar estatísticas resumidas dos resultados.
        
        Returns:
            Dicionário com estatísticas
        """
        if self.results_df is None:
            return {}
        
        df = self.results_df
        successful = df[df['Status'] == 'SUCCESS']
        
        stats = {
            'total_instances': len(df),
            'successful_executions': len(successful),
            'success_rate': len(successful) / len(df) * 100,
            'avg_execution_time': successful['Execution_Time'].mean(),
            'median_execution_time': successful['Execution_Time'].median(),
            'max_execution_time': successful['Execution_Time'].max(),
            'min_execution_time': successful['Execution_Time'].min(),
            'total_execution_time': successful['Execution_Time'].sum(),
            'avg_clique_size': successful['Clique_Size'].mean(),
            'max_clique_size': successful['Clique_Size'].max(),
            'min_clique_size': successful['Clique_Size'].min()
        }
        
        # Estatísticas de otimalidade
        optimal_comparisons = successful[successful['Known_Optimal'] != 'N/A']
        if len(optimal_comparisons) > 0:
            optimal_found = optimal_comparisons[optimal_comparisons['Is_Optimal'] == True]
            stats['instances_with_known_optimal'] = len(optimal_comparisons)
            stats['optimal_solutions_found'] = len(optimal_found)
            stats['optimality_rate'] = len(optimal_found) / len(optimal_comparisons) * 100
            
            # Gap médio para instâncias não ótimas
            non_optimal = optimal_comparisons[optimal_comparisons['Is_Optimal'] == False]
            if len(non_optimal) > 0:
                gaps = pd.to_numeric(non_optimal['Gap_Percent'], errors='coerce')
                stats['avg_gap_percent'] = gaps.mean()
                stats['max_gap_percent'] = gaps.max()
        
        return stats

    def generate_performance_plots(self):
        """
        Gerar gráficos de análise de performance.
        """
        if self.results_df is None:
            logger.warning("Nenhum resultado para plotar")
            return
        
        df = self.results_df
        successful = df[df['Status'] == 'SUCCESS']
        
        if len(successful) == 0:
            logger.warning("Nenhuma execução bem-sucedida para plotar")
            return
        
        # Configuração de plots
        fig, axes = plt.subplots(2, 3, figsize=(18, 12))
        fig.suptitle('Análise de Performance do CliSAT', fontsize=16, y=0.95)
        
        # 1. Distribuição dos tempos de execução
        ax1 = axes[0, 0]
        successful['Execution_Time'].hist(bins=20, ax=ax1, alpha=0.7, color='skyblue')
        ax1.set_xlabel('Tempo de Execução (s)')
        ax1.set_ylabel('Frequência')
        ax1.set_title('Distribuição dos Tempos de Execução')
        ax1.axvline(successful['Execution_Time'].mean(), color='red', linestyle='--', 
                   label=f'Média: {successful["Execution_Time"].mean():.1f}s')
        ax1.legend()
        
        # 2. Relação Tamanho vs Tempo
        ax2 = axes[0, 1]
        scatter = ax2.scatter(successful['Nodes'], successful['Execution_Time'], 
                            c=successful['Clique_Size'], cmap='viridis', alpha=0.7)
        ax2.set_xlabel('Número de Nós')
        ax2.set_ylabel('Tempo de Execução (s)')
        ax2.set_title('Tamanho do Grafo vs Tempo de Execução')
        ax2.set_yscale('log')
        plt.colorbar(scatter, ax=ax2, label='Tamanho do Clique')
        
        # 3. Distribuição dos tamanhos de clique
        ax3 = axes[0, 2]
        successful['Clique_Size'].hist(bins=15, ax=ax3, alpha=0.7, color='lightgreen')
        ax3.set_xlabel('Tamanho do Clique')
        ax3.set_ylabel('Frequência')
        ax3.set_title('Distribuição dos Tamanhos de Clique')
        
        # 4. Performance por densidade do grafo
        ax4 = axes[1, 0]
        # Calcular densidade aproximada
        successful['Density'] = 2 * successful['Edges'] / (successful['Nodes'] * (successful['Nodes'] - 1))
        ax4.scatter(successful['Density'], successful['Execution_Time'], alpha=0.7, color='orange')
        ax4.set_xlabel('Densidade do Grafo')
        ax4.set_ylabel('Tempo de Execução (s)')
        ax4.set_title('Densidade vs Tempo de Execução')
        
        # 5. Comparação com ótimos conhecidos (se disponível)
        ax5 = axes[1, 1]
        optimal_comparisons = successful[successful['Known_Optimal'] != 'N/A']
        if len(optimal_comparisons) > 0:
            # Converter Known_Optimal para numérico
            optimal_comparisons = optimal_comparisons.copy()
            optimal_comparisons['Known_Optimal_Num'] = pd.to_numeric(
                optimal_comparisons['Known_Optimal'], errors='coerce'
            )
            valid_comparisons = optimal_comparisons.dropna(subset=['Known_Optimal_Num'])
            
            if len(valid_comparisons) > 0:
                ax5.scatter(valid_comparisons['Known_Optimal_Num'], 
                           valid_comparisons['Clique_Size'], alpha=0.7, color='purple')
                ax5.plot([valid_comparisons['Known_Optimal_Num'].min(), 
                         valid_comparisons['Known_Optimal_Num'].max()],
                        [valid_comparisons['Known_Optimal_Num'].min(), 
                         valid_comparisons['Known_Optimal_Num'].max()],
                        'r--', label='Linha de Otimalidade')
                ax5.set_xlabel('Clique Ótimo Conhecido')
                ax5.set_ylabel('Clique Encontrado')
                ax5.set_title('Clique Encontrado vs Ótimo Conhecido')
                ax5.legend()
            else:
                ax5.text(0.5, 0.5, 'Dados insuficientes\npara comparação', 
                        ha='center', va='center', transform=ax5.transAxes)
                ax5.set_title('Comparação com Ótimos')
        else:
            ax5.text(0.5, 0.5, 'Nenhum ótimo\nconhecido disponível', 
                    ha='center', va='center', transform=ax5.transAxes)
            ax5.set_title('Comparação com Ótimos')
        
        # 6. Taxa de sucesso por tamanho
        ax6 = axes[1, 2]
        # Criar bins de tamanho
        df['Size_Bin'] = pd.cut(df['Nodes'], bins=5, labels=['Muito Pequeno', 'Pequeno', 'Médio', 'Grande', 'Muito Grande'])
        success_by_size = df.groupby('Size_Bin')['Status'].apply(lambda x: (x == 'SUCCESS').mean() * 100)
        success_by_size.plot(kind='bar', ax=ax6, color='coral')
        ax6.set_xlabel('Tamanho do Grafo')
        ax6.set_ylabel('Taxa de Sucesso (%)')
        ax6.set_title('Taxa de Sucesso por Tamanho')
        ax6.tick_params(axis='x', rotation=45)
        
        plt.tight_layout()
        plot_file = self.plots_dir / "performance_analysis.png"
        plt.savefig(plot_file, dpi=300, bbox_inches='tight')
        plt.close()
        
        logger.info(f"Gráficos de performance salvos em: {plot_file}")

    def generate_detailed_table(self) -> str:
        """
        Gerar tabela detalhada formatada para o relatório.
        
        Returns:
            String com a tabela formatada
        """
        if self.results_df is None:
            return "Nenhum resultado disponível"
        
        df = self.results_df.copy()
        
        # Ordenar por número de nós e nome da instância
        df = df.sort_values(['Nodes', 'Instance'])
        
        # Formatar colunas para melhor apresentação
        df['Execution_Time_Formatted'] = df['Execution_Time'].apply(
            lambda x: f"{x:.2f}s" if pd.notna(x) else "N/A"
        )
        
        df['Gap_Formatted'] = df['Gap_Percent'].apply(
            lambda x: f"{x:.1f}%" if pd.notna(x) and x != 'N/A' else "N/A"
        )
        
        # Criar tabela principal
        table_columns = [
            'Instance', 'Nodes', 'Edges', 'Clique_Size', 
            'Execution_Time_Formatted', 'Known_Optimal', 'Gap_Formatted', 'Status'
        ]
        
        display_df = df[table_columns].copy()
        display_df.columns = [
            'Instância', 'Nós', 'Arestas', 'Clique Máximo', 
            'Tempo de Execução', 'Ótimo Conhecido', 'Gap', 'Status'
        ]
        
        # Gerar string da tabela
        table_str = display_df.to_string(index=False, max_cols=None, max_colwidth=20)
        
        # Adicionar cabeçalho e estatísticas
        stats = self.generate_summary_statistics()
        
        header = """
RESULTADOS FINAIS - ALGORITMO CLISAT PARA CLIQUE MÁXIMO
===============================================================

RESUMO ESTATÍSTICO:
"""
        
        if stats:
            header += f"""
• Total de instâncias testadas: {stats['total_instances']}
• Execuções bem-sucedidas: {stats['successful_executions']} ({stats['success_rate']:.1f}%)
• Tempo médio de execução: {stats['avg_execution_time']:.2f}s
• Tempo total de execução: {stats['total_execution_time']:.1f}s ({stats['total_execution_time']/3600:.2f}h)
• Tamanho médio de clique: {stats['avg_clique_size']:.1f}
• Maior clique encontrado: {stats['max_clique_size']}
"""
            
            if 'optimality_rate' in stats:
                header += f"""
• Instâncias com ótimo conhecido: {stats['instances_with_known_optimal']}
• Soluções ótimas encontradas: {stats['optimal_solutions_found']} ({stats['optimality_rate']:.1f}%)
"""
                if 'avg_gap_percent' in stats:
                    header += f"• Gap médio (não ótimas): {stats['avg_gap_percent']:.1f}%\n"
        
        header += "\n" + "="*80 + "\nDETALHE POR INSTÂNCIA:\n" + "="*80 + "\n"
        
        return header + table_str

    def export_latex_table(self) -> str:
        """
        Exportar tabela em formato LaTeX para documentos acadêmicos.
        
        Returns:
            String com código LaTeX da tabela
        """
        if self.results_df is None:
            return ""
        
        df = self.results_df.copy()
        df = df.sort_values(['Nodes', 'Instance'])
        
        # Selecionar apenas instâncias bem-sucedidas para a tabela LaTeX
        successful = df[df['Status'] == 'SUCCESS']
        
        latex_str = """
\\begin{table}[htbp]
\\centering
\\caption{Resultados do Algoritmo CliSAT para o Problema do Clique Máximo}
\\label{tab:clisat_results}
\\begin{tabular}{lrrrrrl}
\\toprule
\\textbf{Instância} & \\textbf{Nós} & \\textbf{Arestas} & \\textbf{Clique} & \\textbf{Tempo (s)} & \\textbf{Ótimo} & \\textbf{Gap} \\\\
\\midrule
"""
        
        for _, row in successful.iterrows():
            instance = row['Instance'].replace('_', '\\_')
            nodes = int(row['Nodes'])
            edges = int(row['Edges'])
            clique_size = int(row['Clique_Size'])
            exec_time = f"{row['Execution_Time']:.2f}"
            
            known_optimal = row['Known_Optimal']
            if known_optimal != 'N/A':
                optimal_str = str(int(float(known_optimal)))
                gap = row['Gap_Percent']
                if pd.notna(gap) and gap != 'N/A':
                    gap_str = f"{gap:.1f}\\%"
                else:
                    gap_str = "0.0\\%"
            else:
                optimal_str = "N/A"
                gap_str = "N/A"
            
            latex_str += f"{instance} & {nodes} & {edges} & {clique_size} & {exec_time} & {optimal_str} & {gap_str} \\\\\n"
        
        latex_str += """\\bottomrule
\\end{tabular}
\\end{table}
"""
        
        return latex_str

    def generate_comprehensive_report(self):
        """
        Gerar relatório completo de análise.
        """
        if self.results_df is None:
            logger.warning("Nenhum resultado para analisar")
            return
        
        # Gerar estatísticas
        stats = self.generate_summary_statistics()
        
        # Gerar tabela detalhada
        detailed_table = self.generate_detailed_table()
        
        # Gerar tabela LaTeX
        latex_table = self.export_latex_table()
        
        # Salvar relatório completo
        report_file = self.reports_dir / "comprehensive_analysis_report.txt"
        with open(report_file, 'w', encoding='utf-8') as f:
            f.write(detailed_table)
            f.write("\n\n")
            f.write("="*80 + "\n")
            f.write("ANÁLISE DETALHADA POR FAMÍLIA DE INSTÂNCIAS\n")
            f.write("="*80 + "\n")
            
            # Análise por família
            df = self.results_df
            successful = df[df['Status'] == 'SUCCESS']
            
            families = {}
            for _, row in successful.iterrows():
                instance = row['Instance']
                family = instance.split('_')[0] if '_' in instance else instance.split('.')[0]
                if family not in families:
                    families[family] = []
                families[family].append(row)
            
            for family, instances in sorted(families.items()):
                f.write(f"\nFamília {family}:\n")
                f.write("-" * 40 + "\n")
                f.write(f"• Instâncias: {len(instances)}\n")
                
                sizes = [inst['Clique_Size'] for inst in instances]
                times = [inst['Execution_Time'] for inst in instances]
                
                f.write(f"• Clique médio: {np.mean(sizes):.1f}\n")
                f.write(f"• Tempo médio: {np.mean(times):.2f}s\n")
                f.write(f"• Maior clique: {max(sizes)}\n")
                f.write(f"• Menor clique: {min(sizes)}\n")
        
        # Salvar tabela LaTeX separadamente
        latex_file = self.reports_dir / "latex_table.tex"
        with open(latex_file, 'w') as f:
            f.write(latex_table)
        
        # Salvar CSV formatado para Excel
        excel_file = self.reports_dir / "results_for_excel.csv"
        df_excel = self.results_df.copy()
        df_excel = df_excel.sort_values(['Nodes', 'Instance'])
        df_excel.to_csv(excel_file, index=False)
        
        logger.info(f"Relatório completo salvo em: {report_file}")
        logger.info(f"Tabela LaTeX salva em: {latex_file}")
        logger.info(f"CSV para Excel salvo em: {excel_file}")

    def print_quick_summary(self):
        """
        Imprimir resumo rápido dos resultados.
        """
        if self.results_df is None:
            print("❌ Nenhum resultado encontrado")
            return
        
        stats = self.generate_summary_statistics()
        
        print("\n" + "="*60)
        print("RESUMO RÁPIDO DOS RESULTADOS DO CLISAT")
        print("="*60)
        
        if stats:
            print(f"📊 Total de instâncias: {stats['total_instances']}")
            print(f"✅ Execuções bem-sucedidas: {stats['successful_executions']} ({stats['success_rate']:.1f}%)")
            print(f"⏱️  Tempo total: {stats['total_execution_time']:.1f}s ({stats['total_execution_time']/3600:.2f}h)")
            print(f"📈 Clique médio: {stats['avg_clique_size']:.1f}")
            print(f"🎯 Maior clique: {stats['max_clique_size']}")
            
            if 'optimality_rate' in stats:
                print(f"🏆 Taxa de otimalidade: {stats['optimality_rate']:.1f}%")
        
        print()
        
        # Top 5 maiores cliques
        successful = self.results_df[self.results_df['Status'] == 'SUCCESS']
        if len(successful) > 0:
            top_cliques = successful.nlargest(5, 'Clique_Size')
            print("🔝 TOP 5 MAIORES CLIQUES ENCONTRADOS:")
            for i, (_, row) in enumerate(top_cliques.iterrows(), 1):
                print(f"   {i}. {row['Instance']}: {row['Clique_Size']} vértices "
                     f"({row['Execution_Time']:.2f}s)")
        
        print()


def main():
    """
    Função principal com interface de linha de comando.
    """
    parser = argparse.ArgumentParser(
        description="Analisador de Resultados do CliSAT",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--results-dir', type=str, default='execution_results',
                       help='Diretório com os resultados')
    
    parser.add_argument('--summary', action='store_true',
                       help='Mostrar apenas resumo rápido')
    
    parser.add_argument('--plots', action='store_true',
                       help='Gerar gráficos de análise')
    
    parser.add_argument('--report', action='store_true',
                       help='Gerar relatório completo')
    
    parser.add_argument('--latex', action='store_true',
                       help='Gerar tabela LaTeX')
    
    parser.add_argument('--all', action='store_true',
                       help='Executar todas as análises')
    
    args = parser.parse_args()
    
    # Criar analisador
    analyzer = CliSATResultsAnalyzer(results_dir=args.results_dir)
    
    if args.summary or (not any([args.plots, args.report, args.latex, args.all])):
        analyzer.print_quick_summary()
    
    if args.plots or args.all:
        print("🎨 Gerando gráficos de análise...")
        analyzer.generate_performance_plots()
    
    if args.report or args.all:
        print("📋 Gerando relatório completo...")
        analyzer.generate_comprehensive_report()
    
    if args.latex or args.all:
        print("📝 Gerando tabela LaTeX...")
        latex_table = analyzer.export_latex_table()
        if latex_table:
            print("Tabela LaTeX gerada com sucesso!")
    
    if args.all:
        print("\n✅ Todas as análises concluídas!")
        print(f"📁 Arquivos salvos em: {analyzer.results_dir}")


if __name__ == "__main__":
    main()
