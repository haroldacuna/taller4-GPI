"""
Script para análisis exploratorio de datos (EDA) de proyectos de créditos de carbono.

Este script realiza un análisis exploratorio comprehensivo que incluye:
- Estadísticas descriptivas detalladas
- Análisis de correlaciones
- Detección de outliers
- Análisis temporal
- Análisis de riesgo por proyecto
- Análisis por tipo y país
- Reportes de calidad de datos

Los resultados se guardan en results/exploratory/ como archivos CSV y se imprimen
resúmenes en la consola.
"""

from pathlib import Path
import pandas as pd
import sys

# Añadir directorio padre al path para importar módulos src
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

# Importar funciones de análisis
from src.analysis import (
    exploratory_statistics,
    correlation_analysis,
    detect_outliers,
    group_analysis,
    time_series_analysis,
    data_quality_report,
    project_risk_analysis
)


def print_section(title: str):
    """Imprime un encabezado de sección formateado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """Función principal que ejecuta el análisis exploratorio."""
    
    # Configurar rutas
    base = Path(__file__).resolve().parents[1]
    processed_dir = base / "data" / "processed"
    raw_dir = base / "data" / "raw"
    results_dir = base / "results" / "exploratory"
    results_dir.mkdir(parents=True, exist_ok=True)
    
    print_section("ANÁLISIS EXPLORATORIO DE DATOS - PROYECTOS DE CARBONO")
    
    # =========================================================================
    # 1. CARGAR DATOS
    # =========================================================================
    print_section("1. Cargando datos...")
    
    try:
        projects = pd.read_csv(raw_dir / "projects.csv", parse_dates=['start_date', 'end_date'])
        issuance = pd.read_csv(raw_dir / "issuance.csv", parse_dates=['month'])
        prices = pd.read_csv(raw_dir / "prices.csv", parse_dates=['month'])
        summary = pd.read_csv(processed_dir / "project_summary.csv", parse_dates=['start_date', 'end_date'])
        revenue = pd.read_csv(processed_dir / "issuance_with_revenue.csv", parse_dates=['month'])
    except FileNotFoundError as e:
        print(f"ERROR: Archivo no encontrado - {e}")
        print("Por favor, ejecuta primero los scripts 01, 02 y 03.")
        sys.exit(1)
    
    print(f"✓ Projects: {len(projects)} registros")
    print(f"✓ Issuance: {len(issuance)} registros")
    print(f"✓ Prices: {len(prices)} registros")
    print(f"✓ Summary: {len(summary)} registros")
    print(f"✓ Revenue: {len(revenue)} registros")
    
    # =========================================================================
    # 2. ESTADÍSTICAS DESCRIPTIVAS
    # =========================================================================
    print_section("2. Estadísticas descriptivas detalladas")
    
    # Estadísticas de proyectos
    print("\n📊 ESTADÍSTICAS DE PROYECTOS:")
    project_stats = exploratory_statistics(projects)
    print(project_stats.to_string())
    project_stats.to_csv(results_dir / "project_statistics.csv")
    
    # Estadísticas de resumen (agregado por proyecto)
    print("\n📊 ESTADÍSTICAS DE RESUMEN (POR PROYECTO):")
    summary_stats = exploratory_statistics(summary)
    print(summary_stats[['mean', 'std', 'min', '50%', 'max', 'skewness', 'kurtosis']].to_string())
    summary_stats.to_csv(results_dir / "summary_statistics.csv")
    
    # =========================================================================
    # 3. ANÁLISIS DE CALIDAD DE DATOS
    # =========================================================================
    print_section("3. Reporte de calidad de datos")
    
    quality_projects = data_quality_report(projects)
    print("\n🔍 CALIDAD - Proyectos:")
    print(quality_projects.to_string())
    quality_projects.to_csv(results_dir / "quality_report_projects.csv", index=False)
    
    quality_summary = data_quality_report(summary)
    print("\n🔍 CALIDAD - Resumen:")
    print(quality_summary.to_string())
    quality_summary.to_csv(results_dir / "quality_report_summary.csv", index=False)
    
    # =========================================================================
    # 4. ANÁLISIS DE CORRELACIONES
    # =========================================================================
    print_section("4. Análisis de correlaciones")
    
    # Correlaciones en métricas clave de proyectos
    key_cols = [
        'mrv_quality', 'additionality_score', 'leakage_rate', 
        'permanence_risk', 'baseline_tCO2', 'true_reduction_tCO2'
    ]
    corr_projects = correlation_analysis(projects, cols=key_cols)
    print("\n🔗 CORRELACIONES - Métricas de proyectos:")
    print(corr_projects.round(3).to_string())
    corr_projects.to_csv(results_dir / "correlations_projects.csv")
    
    # Correlaciones en resumen agregado
    summary_cols = [
        'integrity_risk_score', 'over_rate', 'retire_rate',
        'mrv_quality', 'additionality_score', 'permanence_risk', 
        'over_total', 'issued_total', 'retired_total'
    ]
    corr_summary = correlation_analysis(summary, cols=summary_cols)
    print("\n🔗 CORRELACIONES - Resumen agregado:")
    print(corr_summary.round(3).to_string())
    corr_summary.to_csv(results_dir / "correlations_summary.csv")
    
    # =========================================================================
    # 5. ANÁLISIS DE OUTLIERS
    # =========================================================================
    print_section("5. Detección de outliers")
    
    outlier_cols = ['baseline_tCO2', 'true_reduction_tCO2', 'area_ha']
    for col in outlier_cols:
        outliers = detect_outliers(projects, col, method='iqr')
        n_outliers = outliers.sum()
        pct_outliers = (n_outliers / len(projects) * 100)
        print(f"📍 {col}: {n_outliers} outliers ({pct_outliers:.2f}%)")
        
        if n_outliers > 0:
            outlier_projects = projects[outliers][['project_id', 'type', 'country', col]]
            outlier_projects.to_csv(results_dir / f"outliers_{col}.csv", index=False)
    
    # =========================================================================
    # 6. ANÁLISIS POR GRUPOS (TIPO DE PROYECTO)
    # =========================================================================
    print_section("6. Análisis por tipo de proyecto")
    
    type_analysis = group_analysis(
        projects,
        group_col='type',
        agg_cols=['baseline_tCO2', 'true_reduction_tCO2', 'mrv_quality', 
                  'additionality_score', 'leakage_rate', 'permanence_risk']
    )
    print("\n📊 ANÁLISIS POR TIPO:")
    print(type_analysis.to_string())
    type_analysis.to_csv(results_dir / "analysis_by_type.csv")
    
    # =========================================================================
    # 7. ANÁLISIS POR PAÍS
    # =========================================================================
    print_section("7. Análisis por país")
    
    country_analysis = group_analysis(
        projects,
        group_col='country',
        agg_cols=['baseline_tCO2', 'true_reduction_tCO2', 'mrv_quality', 'additionality_score']
    )
    print("\n🌍 ANÁLISIS POR PAÍS:")
    print(country_analysis.to_string())
    country_analysis.to_csv(results_dir / "analysis_by_country.csv")
    
    # =========================================================================
    # 8. ANÁLISIS TEMPORAL (SERIES DE TIEMPO)
    # =========================================================================
    print_section("8. Análisis de series temporales")
    
    time_cols = ['issued_credits', 'retired_credits', 'overcrediting_tCO2', 'gross_revenue_usd']
    time_analysis = time_series_analysis(revenue, 'month', time_cols)
    
    print("\n📈 ESTADÍSTICAS MENSUALES (primeros 10 meses):")
    print(time_analysis['monthly_stats'].head(10).to_string())
    time_analysis['monthly_stats'].to_csv(results_dir / "time_series_monthly.csv")
    
    print("\n📈 PROMEDIO MÓVIL 3 MESES (primeros 10 meses):")
    print(time_analysis['rolling_3m'].head(10).to_string())
    time_analysis['rolling_3m'].to_csv(results_dir / "time_series_rolling3m.csv")
    
    print("\n📈 PROMEDIO MÓVIL 6 MESES (primeros 10 meses):")
    print(time_analysis['rolling_6m'].head(10).to_string())
    time_analysis['rolling_6m'].to_csv(results_dir / "time_series_rolling6m.csv")
    
    # =========================================================================
    # 9. ANÁLISIS DE RIESGO DE PROYECTOS
    # =========================================================================
    print_section("9. Análisis de riesgo de proyectos")
    
    risk_analysis = project_risk_analysis(summary)
    
    print("\n⚠️ ESTADÍSTICAS POR NIVEL DE RIESGO:")
    print(risk_analysis['risk_stats'].to_string())
    risk_analysis['risk_stats'].to_csv(results_dir / "risk_level_stats.csv")
    
    print("\n⚠️ TOP 20 PROYECTOS CON MAYOR SOBRECREDITACIÓN:")
    print(risk_analysis['top_overcrediting'].to_string())
    risk_analysis['top_overcrediting'].to_csv(results_dir / "top20_overcrediting.csv", index=False)
    
    print("\n⚠️ ANÁLISIS POR TIPO DE PROYECTO (RIESGO):")
    print(risk_analysis['type_analysis'].to_string())
    risk_analysis['type_analysis'].to_csv(results_dir / "risk_by_type.csv")
    
    # =========================================================================
    # 10. ANÁLISIS DE PRECIOS
    # =========================================================================
    print_section("10. Análisis de precios de carbono")
    
    price_stats = exploratory_statistics(prices)
    print("\n💰 ESTADÍSTICAS DE PRECIOS:")
    print(price_stats[['mean', 'std', 'min', '25%', '50%', '75%', 'max']].to_string())
    price_stats.to_csv(results_dir / "price_statistics.csv")
    
    # Evolución de precios
    print("\n💰 EVOLUCIÓN DE PRECIOS (primeros y últimos 5 meses):")
    print("Primeros 5 meses:")
    print(prices.head().to_string(index=False))
    print("\nÚltimos 5 meses:")
    print(prices.tail().to_string(index=False))
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_section("RESUMEN DEL ANÁLISIS EXPLORATORIO")
    
    print(f"""
    ✅ Análisis completado exitosamente
    
    📁 Resultados guardados en: {results_dir}
    
    📊 Archivos generados:
       - Estadísticas descriptivas (project_statistics.csv, summary_statistics.csv)
       - Reportes de calidad de datos (quality_report_*.csv)
       - Matrices de correlación (correlations_*.csv)
       - Análisis de outliers (outliers_*.csv)
       - Análisis por grupos (analysis_by_type.csv, analysis_by_country.csv)
       - Series temporales (time_series_*.csv)
       - Análisis de riesgo (risk_*.csv, top20_overcrediting.csv)
       - Estadísticas de precios (price_statistics.csv)
    
    🔍 Total de proyectos analizados: {len(projects)}
    📅 Período de análisis: {issuance['month'].min()} - {issuance['month'].max()}
    📈 Total de registros de emisión: {len(issuance):,}
    💰 Rango de precios: ${prices['price_usd'].min():.2f} - ${prices['price_usd'].max():.2f}
    """)
    
    print("✨ Análisis exploratorio completado.\n")


if __name__ == "__main__":
    main()
