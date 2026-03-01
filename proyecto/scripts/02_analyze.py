"""
Script de análisis de datos de proyectos de carbono.

Este script lee los datos raw descargados desde Zenodo y genera:
- Resúmenes a nivel de proyecto
- Datos de emisión con ingresos calculados  
- Top 20 proyectos de mayor riesgo
"""

from pathlib import Path
import pandas as pd

from src.analysis import project_level_summary, market_revenue


def main():
    """
    Función principal que ejecuta el análisis de datos.
    """
    base = Path(__file__).resolve().parents[1]
    raw_dir = base / "data" / "raw"
    processed_dir = base / "data" / "processed"
    tables_dir = base / "results" / "tables"
    
    # Crear directorios de salida
    processed_dir.mkdir(parents=True, exist_ok=True)
    tables_dir.mkdir(parents=True, exist_ok=True)
    
    print("="*70)
    print("ANÁLISIS DE DATOS")
    print("="*70)
    
    # 1. Cargar datos raw
    print("\n1. Cargando datos raw...")
    try:
        projects = pd.read_csv(raw_dir / "projects.csv")
        issuance = pd.read_csv(raw_dir / "issuance.csv")
        prices = pd.read_csv(raw_dir / "prices.csv")
        print(f"   ✓ projects.csv: {len(projects)} proyectos")
        print(f"   ✓ issuance.csv: {len(issuance)} registros")
        print(f"   ✓ prices.csv: {len(prices)} precios mensuales")
    except FileNotFoundError as e:
        print(f"\n   ✗ ERROR: No se encontraron los datos raw.")
        print(f"   {e}")
        print(f"\n   Ejecuta primero: python scripts/01_download_data.py")
        return
    
    # 2. Análisis a nivel de proyecto
    print("\n2. Generando resumen por proyecto...")
    summary = project_level_summary(projects, issuance)
    summary.to_csv(processed_dir / "project_summary.csv", index=False)
    print(f"   ✓ Guardado: {processed_dir / 'project_summary.csv'}")
    
    # 3. Top 20 proyectos de alto riesgo
    print("\n3. Identificando proyectos de alto riesgo...")
    top20 = summary.head(20)[[
        "project_id", "type", "country", "integrity_risk_score",
        "over_rate", "retire_rate", "issued_total", "retired_total"
    ]]
    top20.to_csv(tables_dir / "top20_high_risk_projects.csv", index=False)
    print(f"   ✓ Guardado: {tables_dir / 'top20_high_risk_projects.csv'}")
    
    # 4. Ingresos por emisión
    print("\n4. Calculando ingresos por emisión...")
    revenue = market_revenue(issuance, prices)
    revenue.to_csv(processed_dir / "issuance_with_revenue.csv", index=False)
    print(f"   ✓ Guardado: {processed_dir / 'issuance_with_revenue.csv'}")
    
    # Resumen final
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Proyectos totales: {len(projects)}")
    print(f"Promedio integrity_risk_score: {summary['integrity_risk_score'].mean():.3f}")
    print(f"Promedio over_rate: {summary['over_rate'].mean():.2%}")
    print(f"Promedio retire_rate: {summary['retire_rate'].mean():.2%}")
    print(f"Ingresos totales (USD): ${revenue['gross_revenue_usd'].sum():,.2f}")
    print("="*70)
    print("\n✓ Análisis completado exitosamente\n")


if __name__ == "__main__":
    main()
