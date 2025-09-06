"""
Static Report Generator for Mumbai Railway Simulation
Creates professional presentation-ready reports and visualizations.
"""

import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os
from typing import Dict, List
import json

# Add project root to path
project_root = os.path.dirname(os.path.dirname(__file__))
sys.path.append(project_root)

# Import from mumbai_railway_sim
from mumbai_railway_sim import compare_scenarios

# Set style for professional reports
plt.style.use('seaborn-v0_8')
sns.set_palette("husl")


class ReportGenerator:
    """Generates professional reports for simulation results"""
    
    def __init__(self):
        self.figures_created = []
        
    def create_executive_summary_report(self, scenarios: Dict[str, Dict], output_dir: str = "reports"):
        """Create an executive summary report comparing different scenarios"""
        
        # Create output directory
        os.makedirs(output_dir, exist_ok=True)
        
        # Prepare data for comparison
        comparison_data = self._prepare_comparison_data(scenarios)
        
        # Create visualizations
        self._create_performance_comparison(comparison_data, output_dir)
        self._create_factor_impact_analysis(comparison_data, output_dir)
        self._create_operational_metrics_dashboard(comparison_data, output_dir)
        self._create_network_efficiency_trends(comparison_data, output_dir)
        
        # Generate summary statistics
        self._generate_summary_statistics(comparison_data, output_dir)
        
        print(f"Executive summary report generated in '{output_dir}' directory")
        print(f"Created {len(self.figures_created)} visualization files")
        
    def _prepare_comparison_data(self, scenarios: Dict[str, Dict]) -> pd.DataFrame:
        """Prepare data for comparison analysis"""
        
        data = []
        for scenario_name, results in scenarios.items():
            metrics = results.get('metrics', {})
            test_config = results.get('test_config', {})
            
            data.append({
                'Scenario': scenario_name,
                'Factors': ', '.join(test_config.get('factors_enabled', [])),
                'Total Passengers': metrics.get('total_passengers_transported', 0),
                'Average Delay (min)': metrics.get('average_delay_minutes', 0),
                'On-Time Performance (%)': metrics.get('on_time_performance', 100),
                'Network Efficiency (%)': metrics.get('network_efficiency', 100),
                'Capacity Utilization (%)': metrics.get('capacity_utilization', 0),
                'Total Delays': metrics.get('total_delays', 0),
                'Cancelled Services': metrics.get('cancelled_services', 0)
            })
        
        return pd.DataFrame(data)
    
    def _create_performance_comparison(self, df: pd.DataFrame, output_dir: str):
        """Create performance comparison charts"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 12))
        
        # On-time performance
        bars1 = ax1.bar(df['Scenario'], df['On-Time Performance (%)'], 
                       color='skyblue', alpha=0.8)
        ax1.axhline(y=85, color='red', linestyle='--', alpha=0.7, label='Target: 85%')
        ax1.set_title('On-Time Performance by Scenario', fontsize=14, fontweight='bold')
        ax1.set_ylabel('Percentage (%)')
        ax1.legend()
        ax1.tick_params(axis='x', rotation=45)
        
        # Add value labels on bars
        for bar in bars1:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Average delay
        bars2 = ax2.bar(df['Scenario'], df['Average Delay (min)'], 
                       color='lightcoral', alpha=0.8)
        ax2.axhline(y=5, color='green', linestyle='--', alpha=0.7, label='Target: <5 min')
        ax2.set_title('Average Delay by Scenario', fontsize=14, fontweight='bold')
        ax2.set_ylabel('Minutes')
        ax2.legend()
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars2:
            height = bar.get_height()
            ax2.text(bar.get_x() + bar.get_width()/2., height + 0.2,
                    f'{height:.1f}', ha='center', va='bottom')
        
        # Network efficiency
        bars3 = ax3.bar(df['Scenario'], df['Network Efficiency (%)'], 
                       color='lightgreen', alpha=0.8)
        ax3.axhline(y=90, color='orange', linestyle='--', alpha=0.7, label='Target: >90%')
        ax3.set_title('Network Efficiency by Scenario', fontsize=14, fontweight='bold')
        ax3.set_ylabel('Percentage (%)')
        ax3.legend()
        ax3.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars3:
            height = bar.get_height()
            ax3.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}%', ha='center', va='bottom')
        
        # Passengers transported
        bars4 = ax4.bar(df['Scenario'], df['Total Passengers'] / 1000, 
                       color='gold', alpha=0.8)
        ax4.set_title('Total Passengers Transported by Scenario', fontsize=14, fontweight='bold')
        ax4.set_ylabel('Thousands of Passengers')
        ax4.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars4:
            height = bar.get_height()
            ax4.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                    f'{height:.1f}K', ha='center', va='bottom')
        
        plt.tight_layout()
        filename = os.path.join(output_dir, 'performance_comparison.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        self.figures_created.append(filename)
        plt.show()
    
    def _create_factor_impact_analysis(self, df: pd.DataFrame, output_dir: str):
        """Create factor impact analysis visualization"""
        
        fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))
        
        # Performance vs number of factors
        df['Factor Count'] = df['Factors'].apply(lambda x: len(x.split(', ')) if x else 0)
        
        # Scatter plot: Factor count vs performance
        scatter = ax1.scatter(df['Factor Count'], df['On-Time Performance (%)'], 
                            s=df['Total Passengers']/100, alpha=0.6, c=df['Average Delay (min)'], 
                            cmap='Reds', edgecolors='black')
        
        ax1.set_xlabel('Number of Active Factors')
        ax1.set_ylabel('On-Time Performance (%)')
        ax1.set_title('Impact of Multiple Factors on Performance', fontsize=14, fontweight='bold')
        
        # Add scenario labels
        for i, row in df.iterrows():
            ax1.annotate(row['Scenario'], (row['Factor Count'], row['On-Time Performance (%)']),
                        xytext=(5, 5), textcoords='offset points', fontsize=9)
        
        # Colorbar for delay
        cbar = plt.colorbar(scatter, ax=ax1)
        cbar.set_label('Average Delay (minutes)')
        
        # Correlation heatmap
        correlation_metrics = df[['Average Delay (min)', 'On-Time Performance (%)', 
                                'Network Efficiency (%)', 'Capacity Utilization (%)', 
                                'Factor Count']].corr()
        
        sns.heatmap(correlation_metrics, annot=True, cmap='RdYlBu_r', center=0, 
                   square=True, ax=ax2, cbar_kws={'label': 'Correlation Coefficient'})
        ax2.set_title('Metric Correlations', fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        filename = os.path.join(output_dir, 'factor_impact_analysis.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        self.figures_created.append(filename)
        plt.show()
    
    def _create_operational_metrics_dashboard(self, df: pd.DataFrame, output_dir: str):
        """Create operational metrics dashboard"""
        
        fig = plt.figure(figsize=(20, 12))
        
        # Create a grid layout
        gs = fig.add_gridspec(3, 4, hspace=0.3, wspace=0.3)
        
        # Key metrics summary
        ax1 = fig.add_subplot(gs[0, :2])
        metrics_table = df[['Scenario', 'On-Time Performance (%)', 'Average Delay (min)', 
                          'Network Efficiency (%)']].round(1)
        
        # Create table
        table_data = []
        for _, row in metrics_table.iterrows():
            table_data.append([row['Scenario'], 
                             f"{row['On-Time Performance (%)']}%",
                             f"{row['Average Delay (min)']} min",
                             f"{row['Network Efficiency (%)']}%"])
        
        table = ax1.table(cellText=table_data,
                         colLabels=['Scenario', 'On-Time %', 'Avg Delay', 'Efficiency %'],
                         cellLoc='center', loc='center')
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        ax1.axis('off')
        ax1.set_title('Key Performance Metrics Summary', fontsize=14, fontweight='bold')
        
        # Delay distribution
        ax2 = fig.add_subplot(gs[0, 2:])
        ax2.hist(df['Average Delay (min)'], bins=5, alpha=0.7, color='lightcoral', edgecolor='black')
        ax2.set_xlabel('Average Delay (minutes)')
        ax2.set_ylabel('Number of Scenarios')
        ax2.set_title('Distribution of Average Delays', fontsize=12, fontweight='bold')
        
        # Performance radar chart
        ax3 = fig.add_subplot(gs[1, :2], projection='polar')
        
        # Normalize metrics to 0-1 scale for radar chart
        metrics_for_radar = ['On-Time Performance (%)', 'Network Efficiency (%)', 
                           'Capacity Utilization (%)']
        
        angles = np.linspace(0, 2 * np.pi, len(metrics_for_radar), endpoint=False)
        angles = np.concatenate((angles, [angles[0]]))  # Complete the circle
        
        for _, row in df.iterrows():
            values = [row[metric]/100 for metric in metrics_for_radar]  # Normalize to 0-1
            values += [values[0]]  # Complete the circle
            ax3.plot(angles, values, 'o-', linewidth=2, label=row['Scenario'])
            ax3.fill(angles, values, alpha=0.25)
        
        ax3.set_xticks(angles[:-1])
        ax3.set_xticklabels(metrics_for_radar)
        ax3.set_ylim(0, 1)
        ax3.set_title('Performance Radar Chart', fontsize=12, fontweight='bold')
        ax3.legend(loc='upper right', bbox_to_anchor=(1.3, 1.0))
        
        # Service reliability comparison
        ax4 = fig.add_subplot(gs[1, 2:])
        x_pos = np.arange(len(df))
        
        # Stacked bar chart
        on_time = df['On-Time Performance (%)']
        delayed = 100 - on_time
        
        ax4.bar(x_pos, on_time, label='On-Time', color='green', alpha=0.7)
        ax4.bar(x_pos, delayed, bottom=on_time, label='Delayed', color='red', alpha=0.7)
        
        ax4.set_xlabel('Scenarios')
        ax4.set_ylabel('Percentage (%)')
        ax4.set_title('Service Reliability Breakdown', fontsize=12, fontweight='bold')
        ax4.set_xticks(x_pos)
        ax4.set_xticklabels(df['Scenario'], rotation=45)
        ax4.legend()
        
        # Efficiency vs utilization scatter
        ax5 = fig.add_subplot(gs[2, :2])
        scatter = ax5.scatter(df['Network Efficiency (%)'], df['Capacity Utilization (%)'],
                            s=df['Total Passengers']/50, alpha=0.6, 
                            c=df['Average Delay (min)'], cmap='Reds', edgecolors='black')
        
        ax5.set_xlabel('Network Efficiency (%)')
        ax5.set_ylabel('Capacity Utilization (%)')
        ax5.set_title('Efficiency vs Utilization', fontsize=12, fontweight='bold')
        
        # Add scenario labels
        for i, row in df.iterrows():
            ax5.annotate(row['Scenario'], 
                        (row['Network Efficiency (%)'], row['Capacity Utilization (%)']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Passenger impact analysis
        ax6 = fig.add_subplot(gs[2, 2:])
        
        # Calculate passenger impact score (lower is better)
        df['Passenger Impact Score'] = (df['Average Delay (min)'] * 10 + 
                                      (100 - df['On-Time Performance (%)']) * 5)
        
        bars = ax6.bar(df['Scenario'], df['Passenger Impact Score'], 
                      color='orange', alpha=0.7, edgecolor='black')
        ax6.set_xlabel('Scenarios')
        ax6.set_ylabel('Passenger Impact Score')
        ax6.set_title('Passenger Experience Impact', fontsize=12, fontweight='bold')
        ax6.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            ax6.text(bar.get_x() + bar.get_width()/2., height + 1,
                    f'{height:.1f}', ha='center', va='bottom', fontsize=9)
        
        plt.suptitle('Mumbai Railway Simulation - Operational Dashboard', 
                    fontsize=16, fontweight='bold', y=0.98)
        
        filename = os.path.join(output_dir, 'operational_dashboard.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        self.figures_created.append(filename)
        plt.show()
    
    def _create_network_efficiency_trends(self, df: pd.DataFrame, output_dir: str):
        """Create network efficiency trend analysis"""
        
        fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(16, 10))
        
        # Sort by efficiency for trend analysis
        df_sorted = df.sort_values('Network Efficiency (%)')
        
        # Efficiency trend
        ax1.plot(range(len(df_sorted)), df_sorted['Network Efficiency (%)'], 
                marker='o', linewidth=2, markersize=8, color='blue', alpha=0.7)
        ax1.fill_between(range(len(df_sorted)), df_sorted['Network Efficiency (%)'], 
                        alpha=0.3, color='blue')
        ax1.set_xticks(range(len(df_sorted)))
        ax1.set_xticklabels(df_sorted['Scenario'], rotation=45)
        ax1.set_ylabel('Network Efficiency (%)')
        ax1.set_title('Network Efficiency by Scenario (Sorted)', fontsize=12, fontweight='bold')
        ax1.grid(True, alpha=0.3)
        
        # Performance degradation analysis
        baseline_efficiency = df[df['Scenario'] == 'Normal Operations']['Network Efficiency (%)'].iloc[0] if 'Normal Operations' in df['Scenario'].values else df['Network Efficiency (%)'].max()
        
        df['Efficiency Drop'] = baseline_efficiency - df['Network Efficiency (%)']
        
        bars = ax2.bar(df['Scenario'], df['Efficiency Drop'], 
                      color='red', alpha=0.7, edgecolor='black')
        ax2.set_ylabel('Efficiency Drop (%)')
        ax2.set_title('Performance Degradation from Baseline', fontsize=12, fontweight='bold')
        ax2.tick_params(axis='x', rotation=45)
        
        # Add value labels
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                ax2.text(bar.get_x() + bar.get_width()/2., height + 0.5,
                        f'{height:.1f}%', ha='center', va='bottom')
        
        # Delay vs efficiency relationship
        ax3.scatter(df['Average Delay (min)'], df['Network Efficiency (%)'], 
                   s=df['Total Passengers']/100, alpha=0.6, color='purple', edgecolors='black')
        
        # Add trend line
        z = np.polyfit(df['Average Delay (min)'], df['Network Efficiency (%)'], 1)
        p = np.poly1d(z)
        ax3.plot(df['Average Delay (min)'], p(df['Average Delay (min)']), 
                "r--", alpha=0.8, linewidth=2)
        
        ax3.set_xlabel('Average Delay (minutes)')
        ax3.set_ylabel('Network Efficiency (%)')
        ax3.set_title('Delay vs Efficiency Correlation', fontsize=12, fontweight='bold')
        
        # Add scenario labels
        for i, row in df.iterrows():
            ax3.annotate(row['Scenario'], 
                        (row['Average Delay (min)'], row['Network Efficiency (%)']),
                        xytext=(5, 5), textcoords='offset points', fontsize=8)
        
        # Performance category analysis
        def categorize_performance(row):
            if row['On-Time Performance (%)'] >= 90:
                return 'Excellent'
            elif row['On-Time Performance (%)'] >= 80:
                return 'Good'
            elif row['On-Time Performance (%)'] >= 70:
                return 'Fair'
            else:
                return 'Poor'
        
        df['Performance Category'] = df.apply(categorize_performance, axis=1)
        category_counts = df['Performance Category'].value_counts()
        
        colors = {'Excellent': 'green', 'Good': 'lightgreen', 'Fair': 'orange', 'Poor': 'red'}
        pie_colors = [colors.get(cat, 'gray') for cat in category_counts.index]
        
        ax4.pie(category_counts.values, labels=category_counts.index, autopct='%1.1f%%',
               colors=pie_colors, startangle=90, explode=[0.05]*len(category_counts))
        ax4.set_title('Performance Category Distribution', fontsize=12, fontweight='bold')
        
        plt.tight_layout()
        filename = os.path.join(output_dir, 'efficiency_trends.png')
        plt.savefig(filename, dpi=300, bbox_inches='tight')
        self.figures_created.append(filename)
        plt.show()
    
    def _generate_summary_statistics(self, df: pd.DataFrame, output_dir: str):
        """Generate summary statistics and insights"""
        
        # Calculate key insights
        best_scenario = df.loc[df['On-Time Performance (%)'].idxmax()]
        worst_scenario = df.loc[df['On-Time Performance (%)'].idxmin()]
        
        most_efficient = df.loc[df['Network Efficiency (%)'].idxmax()]
        least_delays = df.loc[df['Average Delay (min)'].idxmin()]
        
        summary_stats = {
            'report_generated': datetime.now().isoformat(),
            'total_scenarios_analyzed': len(df),
            'best_performing_scenario': {
                'name': best_scenario['Scenario'],
                'on_time_performance': float(best_scenario['On-Time Performance (%)']),
                'average_delay': float(best_scenario['Average Delay (min)']),
                'factors': best_scenario['Factors']
            },
            'worst_performing_scenario': {
                'name': worst_scenario['Scenario'],
                'on_time_performance': float(worst_scenario['On-Time Performance (%)']),
                'average_delay': float(worst_scenario['Average Delay (min)']),
                'factors': worst_scenario['Factors']
            },
            'most_efficient_scenario': {
                'name': most_efficient['Scenario'],
                'efficiency': float(most_efficient['Network Efficiency (%)']),
                'factors': most_efficient['Factors']
            },
            'performance_statistics': {
                'average_on_time_performance': float(df['On-Time Performance (%)'].mean()),
                'average_delay': float(df['Average Delay (min)'].mean()),
                'average_efficiency': float(df['Network Efficiency (%)'].mean()),
                'total_passengers_served': int(df['Total Passengers'].sum())
            },
            'key_insights': [
                f"Best performance achieved with '{best_scenario['Scenario']}' scenario",
                f"Worst impact from '{worst_scenario['Scenario']}' scenario",
                f"Average performance degradation: {100 - df['On-Time Performance (%)'].mean():.1f}%",
                f"Most resilient factor combination shows {most_efficient['Network Efficiency (%)']:.1f}% efficiency"
            ]
        }
        
        # Save to JSON
        with open(os.path.join(output_dir, 'summary_statistics.json'), 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        # Create text summary
        with open(os.path.join(output_dir, 'executive_summary.txt'), 'w') as f:
            f.write("MUMBAI RAILWAY SIMULATION - EXECUTIVE SUMMARY\n")
            f.write("=" * 50 + "\n\n")
            f.write(f"Report Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"Scenarios Analyzed: {len(df)}\n\n")
            
            f.write("KEY FINDINGS:\n")
            f.write("-" * 20 + "\n")
            for insight in summary_stats['key_insights']:
                f.write(f"• {insight}\n")
            
            f.write("\nPERFORMANCE SUMMARY:\n")
            f.write("-" * 20 + "\n")
            f.write(f"Average On-Time Performance: {summary_stats['performance_statistics']['average_on_time_performance']:.1f}%\n")
            f.write(f"Average Delay: {summary_stats['performance_statistics']['average_delay']:.1f} minutes\n")
            f.write(f"Average Network Efficiency: {summary_stats['performance_statistics']['average_efficiency']:.1f}%\n")
            f.write(f"Total Passengers Served: {summary_stats['performance_statistics']['total_passengers_served']:,}\n")
            
            f.write("\nSCENARIO RANKINGS:\n")
            f.write("-" * 20 + "\n")
            ranked_df = df.sort_values('On-Time Performance (%)', ascending=False)
            for i, (_, row) in enumerate(ranked_df.iterrows(), 1):
                f.write(f"{i}. {row['Scenario']}: {row['On-Time Performance (%)']:.1f}% on-time\n")
        
        print(f"Summary statistics saved to {output_dir}/summary_statistics.json")
        print(f"Executive summary saved to {output_dir}/executive_summary.txt")


def run_scenario_comparison_demo():
    """Run a demo comparison of different scenarios"""
    
    print("Running scenario comparison for report generation...")
    
    # Define scenarios to test
    scenarios_to_test = {
        'Normal Operations': [],
        'Rush Hour Only': ['rush_hour'],
        'Heavy Rain': ['heavy_rain'],
        'Signal Failure': ['signal_failure'],
        'Rush + Rain': ['rush_hour', 'heavy_rain'],
        'Technical Issues': ['signal_failure', 'power_outage'],
        'Perfect Storm': ['rush_hour', 'heavy_rain', 'signal_failure']
    }
    
    # Import the comparison function from the main script
    results = compare_scenarios(scenarios_to_test, duration_hours=1)
    
    # Generate report
    report_gen = ReportGenerator()
    report_gen.create_executive_summary_report(results, "presentation_reports")
    
    return results


if __name__ == "__main__":
    run_scenario_comparison_demo()
