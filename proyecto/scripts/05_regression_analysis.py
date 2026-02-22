"""
Script de análisis de regresión para proyectos de créditos de carbono.

Este script entrena múltiples modelos de regresión para predecir:
1. Tasa de sobrecreditación (over_rate)
2. Score de riesgo de integridad (integrity_risk_score)
3. Tasa de retiro (retire_rate)

Los resultados incluyen:
- Coeficientes de los modelos
- Métricas de rendimiento (R², RMSE, MAE)
- Predicciones vs valores reales
- Comparación de modelos

Todos los resultados se guardan en results/tables/
"""

from pathlib import Path
import pandas as pd
import sys

# Añadir directorio padre al path para importar módulos src
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.analysis import (
    regression_analysis,
    multiple_regression_models,
    compare_models
)


def print_section(title: str):
    """Imprime un encabezado de sección formateado."""
    print("\n" + "=" * 80)
    print(f"  {title}")
    print("=" * 80 + "\n")


def main():
    """Función principal que ejecuta el análisis de regresión."""
    
    # Configurar rutas
    base = Path(__file__).resolve().parents[1]
    processed_dir = base / "data" / "processed"
    tables_dir = base / "results" / "tables"
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    print_section("ANÁLISIS DE REGRESIÓN - PROYECTOS DE CARBONO")
    
    # =========================================================================
    # 1. CARGAR DATOS
    # =========================================================================
    print_section("1. Cargando datos")
    
    try:
        summary = pd.read_csv(processed_dir / "project_summary.csv", 
                             parse_dates=['start_date', 'end_date'])
        print(f"✓ Datos cargados: {len(summary)} proyectos")
        print(f"✓ Variables disponibles: {len(summary.columns)} columnas")
    except FileNotFoundError as e:
        print(f"ERROR: Archivo no encontrado - {e}")
        print("Por favor, ejecuta primero los scripts 01 y 02.")
        sys.exit(1)
    
    # =========================================================================
    # 2. DEFINIR CONFIGURACIONES DE MODELOS
    # =========================================================================
    print_section("2. Configurando modelos de regresión")
    
    # Variables independientes comunes
    quality_features = [
        'mrv_quality', 
        'additionality_score', 
        'leakage_rate', 
        'permanence_risk'
    ]
    
    project_features = [
        'baseline_tCO2',
        'area_ha',
        'verification_frequency_months',
        'buffer_contribution_rate'
    ]
    
    all_features = quality_features + project_features
    
    # Configuraciones de modelos a entrenar
    regression_configs = [
        {
            'name': 'over_rate_quality',
            'target': 'over_rate',
            'features': quality_features,
            'model_type': 'linear'
        },
        {
            'name': 'over_rate_all',
            'target': 'over_rate',
            'features': all_features,
            'model_type': 'linear'
        },
        {
            'name': 'over_rate_ridge',
            'target': 'over_rate',
            'features': all_features,
            'model_type': 'ridge'
        },
        {
            'name': 'integrity_risk_quality',
            'target': 'integrity_risk_score',
            'features': quality_features,
            'model_type': 'linear'
        },
        {
            'name': 'integrity_risk_all',
            'target': 'integrity_risk_score',
            'features': all_features,
            'model_type': 'linear'
        },
        {
            'name': 'retire_rate_quality',
            'target': 'retire_rate',
            'features': quality_features,
            'model_type': 'linear'
        },
        {
            'name': 'retire_rate_all',
            'target': 'retire_rate',
            'features': all_features,
            'model_type': 'linear'
        }
    ]
    
    print(f"✓ {len(regression_configs)} modelos configurados")
    
    # =========================================================================
    # 3. ENTRENAR MODELOS
    # =========================================================================
    print_section("3. Entrenamiento de modelos")
    
    results = multiple_regression_models(summary, regression_configs)
    
    successful_models = sum(1 for r in results.values() if 'error' not in r)
    print(f"\n✅ {successful_models}/{len(results)} modelos entrenados exitosamente")
    
    # =========================================================================
    # 4. GUARDAR RESULTADOS DETALLADOS
    # =========================================================================
    print_section("4. Guardando resultados detallados")
    
    for model_name, result in results.items():
        if 'error' in result:
            continue
        
        # Guardar coeficientes
        coef_file = tables_dir / f"regression_coef_{model_name}.csv"
        result['coefficients'].to_csv(coef_file, index=False)
        print(f"✓ Coeficientes: {coef_file.name}")
        
        # Guardar métricas
        metrics_file = tables_dir / f"regression_metrics_{model_name}.csv"
        result['metrics'].to_csv(metrics_file, index=False)
        print(f"✓ Métricas: {metrics_file.name}")
        
        # Guardar predicciones (top 50)
        pred_file = tables_dir / f"regression_predictions_{model_name}.csv"
        result['predictions'].head(50).to_csv(pred_file, index=False)
        print(f"✓ Predicciones: {pred_file.name}")
    
    # =========================================================================
    # 5. COMPARACIÓN DE MODELOS
    # =========================================================================
    print_section("5. Comparación de modelos")
    
    comparison = compare_models(results)
    print("\n📊 COMPARACIÓN DE MODELOS:")
    print(comparison.to_string(index=False))
    
    comparison_file = tables_dir / "regression_model_comparison.csv"
    comparison.to_csv(comparison_file, index=False)
    print(f"\n✓ Comparación guardada: {comparison_file.name}")
    
    # =========================================================================
    # 6. ANÁLISIS DETALLADO DE MEJOR MODELO POR TARGET
    # =========================================================================
    print_section("6. Análisis de mejores modelos por objetivo")
    
    # Mejores modelos por target
    best_by_target = comparison.groupby('target').first().reset_index()
    print("\n🏆 MEJORES MODELOS POR OBJETIVO:\n")
    print(best_by_target.to_string(index=False))
    
    best_by_target_file = tables_dir / "regression_best_by_target.csv"
    best_by_target.to_csv(best_by_target_file, index=False)
    print(f"\n✓ Mejores modelos guardados: {best_by_target_file.name}")
    
    # Mostrar coeficientes de los mejores modelos
    print("\n" + "=" * 80)
    print("COEFICIENTES DE MEJORES MODELOS")
    print("=" * 80)
    
    for _, row in best_by_target.iterrows():
        model_name = row['model']
        target = row['target']
        
        if model_name in results and 'error' not in results[model_name]:
            print(f"\n📈 {target.upper()} (modelo: {model_name})")
            print(f"   R² = {row['test_R²']:.4f}")
            print("\n   Top 5 variables más importantes:")
            coefs = results[model_name]['coefficients'].head(5)
            for _, c in coefs.iterrows():
                print(f"   • {c['feature']:30s}: {c['coefficient']:8.4f}")
    
    # =========================================================================
    # 7. ANÁLISIS DE RESIDUOS
    # =========================================================================
    print_section("7. Análisis de residuos")
    
    for model_name, result in results.items():
        if 'error' in result:
            continue
        
        predictions = result['predictions']
        
        print(f"\n📉 {model_name}:")
        print(f"   Residuo medio: {predictions['residual'].mean():.6f}")
        print(f"   Residuo std: {predictions['residual'].std():.6f}")
        print(f"   MAE residual: {predictions['abs_residual'].mean():.6f}")
        
        # Top 10 peores predicciones
        worst = predictions.nlargest(10, 'abs_residual')
        worst_file = tables_dir / f"regression_worst_predictions_{model_name}.csv"
        worst.to_csv(worst_file, index=False)
    
    # =========================================================================
    # RESUMEN FINAL
    # =========================================================================
    print_section("RESUMEN DEL ANÁLISIS DE REGRESIÓN")
    
    print(f"""
    ✅ Análisis de regresión completado exitosamente
    
    📁 Resultados guardados en: {tables_dir}
    
    📊 Archivos generados:
       - Coeficientes de cada modelo (regression_coef_*.csv)
       - Métricas de rendimiento (regression_metrics_*.csv)
       - Predicciones vs valores reales (regression_predictions_*.csv)
       - Peores predicciones (regression_worst_predictions_*.csv)
       - Comparación de modelos (regression_model_comparison.csv)
       - Mejores modelos por objetivo (regression_best_by_target.csv)
    
    🎯 Objetivos analizados:
       - over_rate: Tasa de sobrecreditación
       - integrity_risk_score: Score de riesgo de integridad
       - retire_rate: Tasa de retiro de créditos
    
    🔧 Modelos entrenados: {len(results)}
    ✓ Exitosos: {successful_models}
    
    📈 Mejor modelo global: {comparison.iloc[0]['model']}
       Target: {comparison.iloc[0]['target']}
       R²: {comparison.iloc[0]['test_R²']:.4f}
    """)
    
    print("✨ Análisis de regresión completado.\n")


if __name__ == "__main__":
    main()
