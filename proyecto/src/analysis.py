import pandas as pd
import numpy as np
from typing import Dict, Tuple

def project_level_summary(projects: pd.DataFrame, issuance: pd.DataFrame) -> pd.DataFrame:
    agg = issuance.groupby("project_id").agg(
        true_total=("true_reduction_tCO2", "sum"),
        reported_total=("reported_reduction_tCO2", "sum"),
        issued_total=("issued_credits", "sum"),
        retired_total=("retired_credits", "sum"),
        buffer_total=("buffer_credits", "sum"),
        over_total=("overcrediting_tCO2", "sum"),
        risk_events=("delivery_risk_flag", "sum"),
    ).reset_index()

    df = projects.merge(agg, on="project_id", how="left")

    df["over_rate"] = np.where(df["reported_total"] > 0, df["over_total"] / df["reported_total"], 0.0)
    df["retire_rate"] = np.where(df["issued_total"] > 0, df["retired_total"] / df["issued_total"], 0.0)

    # Score simple de “riesgo reputacional / calidad”
    df["integrity_risk_score"] = (
        0.45 * (1 - df["mrv_quality"]) +
        0.25 * (1 - df["additionality_score"]) +
        0.20 * df["permanence_risk"] +
        0.10 * df["leakage_rate"]
    )

    return df.sort_values(["integrity_risk_score", "over_rate"], ascending=False)

def market_revenue(issuance: pd.DataFrame, prices: pd.DataFrame) -> pd.DataFrame:
    df = issuance.merge(prices, on="month", how="left")
    df["gross_revenue_usd"] = (df["retired_credits"] * df["price_usd"]).round(2)
    return df


def exploratory_statistics(df: pd.DataFrame, numeric_cols: list = None) -> pd.DataFrame:
    """
    Genera estadísticas descriptivas completas para columnas numéricas.
    
    Args:
        df: DataFrame a analizar
        numeric_cols: Lista de columnas numéricas. Si es None, usa todas las columnas numéricas.
    
    Returns:
        DataFrame con estadísticas descriptivas expandidas
    """
    if numeric_cols is None:
        numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    stats = df[numeric_cols].describe().T
    stats['variance'] = df[numeric_cols].var()
    stats['skewness'] = df[numeric_cols].skew()
    stats['kurtosis'] = df[numeric_cols].kurtosis()
    stats['missing'] = df[numeric_cols].isnull().sum()
    stats['missing_pct'] = (df[numeric_cols].isnull().sum() / len(df) * 100).round(2)
    
    return stats


def correlation_analysis(df: pd.DataFrame, cols: list = None, method: str = 'pearson') -> pd.DataFrame:
    """
    Calcula la matriz de correlación para columnas especificadas.
    
    Args:
        df: DataFrame a analizar
        cols: Lista de columnas. Si es None, usa todas las numéricas.
        method: Método de correlación ('pearson', 'spearman', 'kendall')
    
    Returns:
        Matriz de correlación
    """
    if cols is None:
        cols = df.select_dtypes(include=[np.number]).columns.tolist()
    
    return df[cols].corr(method=method)


def detect_outliers(df: pd.DataFrame, col: str, method: str = 'iqr') -> pd.Series:
    """
    Detecta outliers en una columna usando el método IQR o Z-score.
    
    Args:
        df: DataFrame
        col: Nombre de la columna
        method: 'iqr' (rango intercuartílico) o 'zscore'
    
    Returns:
        Series booleana indicando si cada valor es outlier
    """
    if method == 'iqr':
        Q1 = df[col].quantile(0.25)
        Q3 = df[col].quantile(0.75)
        IQR = Q3 - Q1
        lower_bound = Q1 - 1.5 * IQR
        upper_bound = Q3 + 1.5 * IQR
        return (df[col] < lower_bound) | (df[col] > upper_bound)
    
    elif method == 'zscore':
        z_scores = np.abs((df[col] - df[col].mean()) / df[col].std())
        return z_scores > 3
    
    else:
        raise ValueError("method debe ser 'iqr' o 'zscore'")


def group_analysis(df: pd.DataFrame, group_col: str, agg_cols: list, 
                   agg_funcs: list = ['mean', 'median', 'std', 'count']) -> pd.DataFrame:
    """
    Análisis agrupado por una variable categórica.
    
    Args:
        df: DataFrame
        group_col: Columna para agrupar
        agg_cols: Columnas a agregar
        agg_funcs: Funciones de agregación
    
    Returns:
        DataFrame con estadísticas por grupo
    """
    return df.groupby(group_col)[agg_cols].agg(agg_funcs).round(4)


def time_series_analysis(df: pd.DataFrame, date_col: str, value_cols: list) -> Dict[str, pd.DataFrame]:
    """
    Análisis de series temporales agregando por mes.
    
    Args:
        df: DataFrame con datos de series temporales
        date_col: Nombre de la columna de fecha
        value_cols: Columnas con valores a analizar
    
    Returns:
        Diccionario con DataFrames de análisis temporal
    """
    df_copy = df.copy()
    df_copy[date_col] = pd.to_datetime(df_copy[date_col])
    
    # Agregaciones mensuales
    monthly = df_copy.groupby(date_col)[value_cols].agg(['sum', 'mean', 'count']).round(2)
    
    # Tendencias (promedio móvil)
    rolling_3m = df_copy.groupby(date_col)[value_cols].sum().rolling(window=3).mean().round(2)
    rolling_6m = df_copy.groupby(date_col)[value_cols].sum().rolling(window=6).mean().round(2)
    
    return {
        'monthly_stats': monthly,
        'rolling_3m': rolling_3m,
        'rolling_6m': rolling_6m
    }


def data_quality_report(df: pd.DataFrame) -> pd.DataFrame:
    """
    Genera un reporte de calidad de datos.
    
    Args:
        df: DataFrame a analizar
    
    Returns:
        DataFrame con métricas de calidad por columna
    """
    quality = pd.DataFrame({
        'column': df.columns,
        'dtype': df.dtypes.values,
        'non_null_count': df.count().values,
        'null_count': df.isnull().sum().values,
        'null_pct': (df.isnull().sum() / len(df) * 100).round(2).values,
        'unique_count': df.nunique().values,
        'unique_pct': (df.nunique() / len(df) * 100).round(2).values
    })
    
    return quality


def project_risk_analysis(summary_df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
    """
    Análisis de riesgo específico para proyectos de carbono.
    
    Args:
        summary_df: DataFrame con resumen de proyectos
    
    Returns:
        Diccionario con varios análisis de riesgo
    """
    # Clasificación por nivel de riesgo
    summary_df = summary_df.copy()
    summary_df['risk_level'] = pd.cut(
        summary_df['integrity_risk_score'],
        bins=[0, 0.3, 0.5, 0.7, 1.0],
        labels=['Bajo', 'Medio', 'Alto', 'Muy Alto']
    )
    
    # Estadísticas por nivel de riesgo
    risk_stats = summary_df.groupby('risk_level').agg({
        'project_id': 'count',
        'over_total': 'sum',
        'over_rate': 'mean',
        'issued_total': 'sum',
        'retired_total': 'sum',
        'retire_rate': 'mean'
    }).round(2)
    risk_stats.columns = ['num_projects', 'total_overcrediting', 'avg_over_rate', 
                          'total_issued', 'total_retired', 'avg_retire_rate']
    
    # Top proyectos por sobrecreditación
    top_overcrediting = summary_df.nlargest(20, 'over_total')[
        ['project_id', 'type', 'country', 'over_total', 'over_rate', 
         'integrity_risk_score', 'risk_level']
    ]
    
    # Análisis por tipo de proyecto
    type_analysis = summary_df.groupby('type').agg({
        'project_id': 'count',
        'integrity_risk_score': 'mean',
        'over_rate': 'mean',
        'retire_rate': 'mean',
        'mrv_quality': 'mean',
        'additionality_score': 'mean'
    }).round(4)
    
    return {
        'risk_stats': risk_stats,
        'top_overcrediting': top_overcrediting,
        'type_analysis': type_analysis
    }