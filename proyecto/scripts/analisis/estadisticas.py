"""
Script de estadísticas descriptivas para proyectos de créditos de carbono.

Este script genera análisis exhaustivos de estadísticas descriptivas incluyendo:
- Medidas de tendencia central (media, mediana, moda)
- Medidas de dispersión (varianza, desv. estándar, rango, IQR)
- Medidas de forma (asimetría, curtosis)
- Percentiles y distribuciones
- Comparación de estadísticas por grupos
- Tablas de frecuencia

Resultados guardados en: results/tables/
"""

from pathlib import Path
import pandas as pd
import numpy as np
import sys
from scipy import stats

# Añadir directorio padre al path para importar módulos src
sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def print_section(title: str):
    """Imprime un encabezado de sección formateado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def estadisticas_descriptivas_completas(series: pd.Series, nombre: str = None) -> pd.DataFrame:
    """
    Calcula estadísticas descriptivas completas para una serie.
    
    Args:
        series: Series de pandas a analizar
        nombre: Nombre descriptivo de la serie
    
    Returns:
        DataFrame con estadísticas detalladas
    """
    stats_dict = {
        'variable': nombre or series.name or 'sin_nombre',
        'count': series.count(),
        'missing': series.isnull().sum(),
        'missing_pct': (series.isnull().sum() / len(series) * 100),
        'mean': series.mean(),
        'median': series.median(),
        'mode': series.mode().values[0] if len(series.mode()) > 0 else np.nan,
        'std': series.std(),
        'variance': series.var(),
        'min': series.min(),
        'q25': series.quantile(0.25),
        'q50': series.quantile(0.50),
        'q75': series.quantile(0.75),
        'q95': series.quantile(0.95),
        'q99': series.quantile(0.99),
        'max': series.max(),
        'range': series.max() - series.min(),
        'iqr': series.quantile(0.75) - series.quantile(0.25),
        'skewness': series.skew(),
        'kurtosis': series.kurtosis(),
        'cv': (series.std() / series.mean()) if series.mean() != 0 else np.nan
    }
    
    return pd.Series(stats_dict)


def estadisticas_por_grupo(df: pd.DataFrame, group_col: str, numeric_cols: list = None) -> dict:
    """
    Calcula estadísticas por grupos.
    
    Args:
        df: DataFrame a analizar
        group_col: Columna para agrupar
        numeric_cols: Columnas numéricas a analizar
    
    Returns:
        Diccionario con DataFrames de estadísticas por grupo
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    results = {}
    
    for col in numeric_cols:
        stats_by_group = df.groupby(group_col)[col].agg([
            'count', 'mean', 'median', 'std', 'min', 'max',
            ('q25', lambda x: x.quantile(0.25)),
            ('q75', lambda x: x.quantile(0.75)),
            ('iqr', lambda x: x.quantile(0.75) - x.quantile(0.25))
        ]).round(4)
        
        results[col] = stats_by_group
    
    return results


def correlacion_parcial(df: pd.DataFrame, numeric_cols: list = None) -> pd.DataFrame:
    """
    Calcula correlaciones de Pearson, Spearman y Kendall.
    
    Args:
        df: DataFrame a analizar
        numeric_cols: Columnas numéricas a analizar
    
    Returns:
        Diccionario con matrices de correlación
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    correlations = {}
    correlations['pearson'] = df[numeric_cols].corr(method='pearson')
    correlations['spearman'] = df[numeric_cols].corr(method='spearman')
    correlations['kendall'] = df[numeric_cols].corr(method='kendall')
    
    return correlations


def tabla_frecuencias(series: pd.Series, bins: int = 10) -> pd.DataFrame:
    """
    Genera tabla de frecuencias para una variable continua.
    
    Args:
        series: Series a analizar
        bins: Número de intervalos
    
    Returns:
        DataFrame con frecuencias
    """
    counts, edges = np.histogram(series.dropna(), bins=bins)
    
    freq_table = pd.DataFrame({
        'intervalo': [f"[{edges[i]:.2f}, {edges[i+1]:.2f})" for i in range(len(edges)-1)],
        'frecuencia': counts,
        'frecuencia_relativa': (counts / counts.sum()).round(4),
        'frecuencia_acumulada': np.cumsum(counts),
        'frecuencia_acumulada_relativa': (np.cumsum(counts) / counts.sum()).round(4)
    })
    
    return freq_table


def analisis_normalidad(series: pd.Series) -> dict:
    """
    Realiza pruebas de normalidad sobre una serie.
    
    Args:
        series: Series a analizar
    
    Returns:
        Diccionario con resultados de pruebas de normalidad
    """
    clean_data = series.dropna()
    
    # Shapiro-Wilk test
    shapiro_stat, shapiro_p = stats.shapiro(clean_data)
    
    # Anderson-Darling test
    anderson_result = stats.anderson(clean_data)
    
    # Kolmogorov-Smirnov test
    ks_stat, ks_p = stats.kstest(clean_data, 'norm', args=(clean_data.mean(), clean_data.std()))
    
    # D'Agostino and Pearson's test
    k2_stat, k2_p = stats.normaltest(clean_data)
    
    return {
        'shapiro_wilk': {'statistic': shapiro_stat, 'p_value': shapiro_p, 'normal': shapiro_p > 0.05},
        'anderson_darling': {'statistic': anderson_result.statistic, 'critical_values': anderson_result.critical_values},
        'kolmogorov_smirnov': {'statistic': ks_stat, 'p_value': ks_p, 'normal': ks_p > 0.05},
        'dagostino_pearson': {'statistic': k2_stat, 'p_value': k2_p, 'normal': k2_p > 0.05}
    }


def analisis_outliers_extremo(df: pd.DataFrame, numeric_cols: list = None, 
                               metodo: str = 'iqr', factor: float = 1.5) -> dict:
    """
    Análisis detallado de outliers.
    
    Args:
        df: DataFrame a analizar
        numeric_cols: Columnas numéricas
        metodo: 'iqr' o 'zscore'
        factor: Factor para IQR (default: 1.5 para outliers, 3.0 para extremos)
    
    Returns:
        Diccionario con análisis de outliers
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    results = {}
    
    for col in numeric_cols:
        outliers_list = []
        
        if metodo == 'iqr':
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower = Q1 - factor * IQR
            upper = Q3 + factor * IQR
            
            outliers_mask = (df[col] < lower) | (df[col] > upper)
            outliers_list = df[outliers_mask][[col]].copy()
            outliers_list['tipo'] = np.where(df[outliers_mask][col] < lower, 'bajo', 'alto')
            
        elif metodo == 'zscore':
            z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
            outliers_mask = z_scores > factor
            outliers_list = df[outliers_mask][[col]].copy()
        
        results[col] = {
            'n_outliers': len(outliers_list),
            'pct_outliers': (len(outliers_list) / len(df) * 100),
            'outliers': outliers_list
        }
    
    return results


def main():
    """Función principal."""
    
    # Configurar rutas
    base = Path(__file__).resolve().parents[2]
    processed_dir = base / "data" / "processed"
    tables_dir = base / "results" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    print_section("ESTADÍSTICAS DESCRIPTIVAS COMPLETAS")
    
    # =========================================================================
    # 1. CARGAR DATOS
    # =========================================================================
    print_section("1. Cargando datos")
    
    try:
        summary = pd.read_csv(processed_dir / "project_summary.csv", 
                             parse_dates=['start_date', 'end_date'])
        print(f"✓ Datos cargados: {len(summary)} proyectos")
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    
    # =========================================================================
    # 2. ESTADÍSTICAS DESCRIPTIVAS POR VARIABLE
    # =========================================================================
    print_section("2. Estadísticas descriptivas detalladas")
    
    numeric_cols = summary.select_dtypes(include=[np.number]).columns.tolist()
    
    stats_list = []
    for col in numeric_cols:
        stats_list.append(estadisticas_descriptivas_completas(summary[col], col))
    
    stats_df = pd.DataFrame(stats_list)
    print("\n📊 ESTADÍSTICAS DESCRIPTIVAS:")
    print(stats_df[['variable', 'count', 'mean', 'std', 'min', 'q50', 'max', 'skewness']].to_string())
    
    stats_df.to_csv(tables_dir / "estadisticas_descriptivas.csv", index=False)
    print("\n✓ Guardado: estadisticas_descriptivas.csv")
    
    # =========================================================================
    # 3. ESTADÍSTICAS POR TIPO DE PROYECTO
    # =========================================================================
    print_section("3. Estadísticas por tipo de proyecto")
    
    cols_to_analyze = ['over_rate', 'integrity_risk_score', 'mrv_quality', 'additionality_score', 'permanence_risk']
    stats_by_type = estadisticas_por_grupo(summary, 'type', cols_to_analyze)
    
    print("\n🏷️ OVER_RATE POR TIPO:")
    print(stats_by_type['over_rate'].to_string())
    stats_by_type['over_rate'].to_csv(tables_dir / "estadisticas_over_rate_por_tipo.csv")
    
    print("\n🏷️ INTEGRITY_RISK_SCORE POR TIPO:")
    print(stats_by_type['integrity_risk_score'].to_string())
    stats_by_type['integrity_risk_score'].to_csv(tables_dir / "estadisticas_integrity_risk_por_tipo.csv")
    
    # =========================================================================
    # 4. ESTADÍSTICAS POR PAÍS
    # =========================================================================
    print_section("4. Estadísticas por país")
    
    stats_by_country = estadisticas_por_grupo(summary, 'country', 
                                              ['over_rate', 'integrity_risk_score', 'mrv_quality'])
    
    print("\n🌍 OVER_RATE POR PAÍS:")
    print(stats_by_country['over_rate'].to_string())
    stats_by_country['over_rate'].to_csv(tables_dir / "estadisticas_over_rate_por_pais.csv")
    
    # =========================================================================
    # 5. CORRELACIONES
    # =========================================================================
    print_section("5. Matrices de correlación")
    
    corr = correlacion_parcial(summary, numeric_cols[:8])
    
    print("\n🔗 CORRELACIÓN PEARSON (primeras 5x5):")
    print(corr['pearson'].iloc[:5, :5].round(3).to_string())
    corr['pearson'].to_csv(tables_dir / "correlacion_pearson.csv")
    
    print("\n🔗 CORRELACIÓN SPEARMAN (primeras 5x5):")
    print(corr['spearman'].iloc[:5, :5].round(3).to_string())
    corr['spearman'].to_csv(tables_dir / "correlacion_spearman.csv")
    
    # =========================================================================
    # 6. TABLA DE FRECUENCIAS
    # =========================================================================
    print_section("6. Tablas de frecuencias")
    
    freq_over_rate = tabla_frecuencias(summary['over_rate'], bins=10)
    print("\n📊 DISTRIBUCIÓN DE OVER_RATE:")
    print(freq_over_rate.to_string())
    freq_over_rate.to_csv(tables_dir / "frecuencias_over_rate.csv", index=False)
    
    freq_integrity = tabla_frecuencias(summary['integrity_risk_score'], bins=10)
    print("\n📊 DISTRIBUCIÓN DE INTEGRITY_RISK_SCORE:")
    print(freq_integrity.to_string())
    freq_integrity.to_csv(tables_dir / "frecuencias_integrity_risk.csv", index=False)
    
    # =========================================================================
    # 7. PRUEBAS DE NORMALIDAD
    # =========================================================================
    print_section("7. Pruebas de normalidad")
    
    print("\n🔬 NORMALIDAD - OVER_RATE:")
    norm_test_over = analisis_normalidad(summary['over_rate'])
    print(f"  Shapiro-Wilk p-value: {norm_test_over['shapiro_wilk']['p_value']:.6f}")
    print(f"  ¿Normal?: {norm_test_over['shapiro_wilk']['normal']}")
    
    print("\n🔬 NORMALIDAD - INTEGRITY_RISK_SCORE:")
    norm_test_integrity = analisis_normalidad(summary['integrity_risk_score'])
    print(f"  Shapiro-Wilk p-value: {norm_test_integrity['shapiro_wilk']['p_value']:.6f}")
    print(f"  ¿Normal?: {norm_test_integrity['shapiro_wilk']['normal']}")
    
    norm_results = pd.DataFrame({
        'variable': ['over_rate', 'integrity_risk_score', 'mrv_quality'],
        'shapiro_p': [
            norm_test_over['shapiro_wilk']['p_value'],
            norm_test_integrity['shapiro_wilk']['p_value'],
            analisis_normalidad(summary['mrv_quality'])['shapiro_wilk']['p_value']
        ],
        'normal_alpha_005': [
            norm_test_over['shapiro_wilk']['normal'],
            norm_test_integrity['shapiro_wilk']['normal'],
            analisis_normalidad(summary['mrv_quality'])['shapiro_wilk']['normal']
        ]
    })
    norm_results.to_csv(tables_dir / "pruebas_normalidad.csv", index=False)
    print("\n✓ Pruebas de normalidad guardadas")
    
    # =========================================================================
    # 8. ANÁLISIS DE OUTLIERS
    # =========================================================================
    print_section("8. Análisis de outliers")
    
    outliers_1_5 = analisis_outliers_extremo(summary, numeric_cols[:5], metodo='iqr', factor=1.5)
    
    print("\n⚠️ OUTLIERS (IQR x 1.5):")
    for col, info in outliers_1_5.items():
        print(f"  {col}: {info['n_outliers']} outliers ({info['pct_outliers']:.2f}%)")
    
    outliers_3 = analisis_outliers_extremo(summary, numeric_cols[:5], metodo='iqr', factor=3.0)
    
    print("\n🔴 OUTLIERS EXTREMOS (IQR x 3.0):")
    for col, info in outliers_3.items():
        print(f"  {col}: {info['n_outliers']} outliers ({info['pct_outliers']:.2f}%)")
    
    # Guardar resumen de outliers
    outliers_summary = pd.DataFrame({
        'variable': list(outliers_1_5.keys()),
        'n_outliers_1_5': [outliers_1_5[col]['n_outliers'] for col in outliers_1_5.keys()],
        'pct_outliers_1_5': [outliers_1_5[col]['pct_outliers'] for col in outliers_1_5.keys()],
        'n_outliers_3_0': [outliers_3[col]['n_outliers'] for col in outliers_3.keys()],
        'pct_outliers_3_0': [outliers_3[col]['pct_outliers'] for col in outliers_3.keys()]
    })
    outliers_summary.to_csv(tables_dir / "resumen_outliers.csv", index=False)
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_section("RESUMEN")
    
    print(f"""
    ✅ Análisis de estadísticas descriptivas completado
    
    📁 Resultados guardados en: {tables_dir}
    
    📊 Archivos generados:
       - estadisticas_descriptivas.csv
       - estadisticas_over_rate_por_tipo.csv
       - estadisticas_integrity_risk_por_tipo.csv
       - estadisticas_over_rate_por_pais.csv
       - correlacion_pearson.csv
       - correlacion_spearman.csv
       - frecuencias_over_rate.csv
       - frecuencias_integrity_risk.csv
       - pruebas_normalidad.csv
       - resumen_outliers.csv
    
    🔍 Variables analizadas: {len(numeric_cols)}
    📊 Observaciones: {len(summary)}
    🏷️ Tipos: {summary['type'].nunique()}
    🌍 Países: {summary['country'].nunique()}
    """)
    
    print("✨ Análisis completado.\n")


if __name__ == "__main__":
    main()
