"""
Script de prueba para las funciones de utilidades.
"""

from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.utilidades import *
import pandas as pd

print("\n=== PRUEBAS DE UTILIDADES ===\n")

# Test 1: Cargar datos
print("📥 Test 1: Cargando datos...")
df = cargar_csv('data/processed/project_summary.csv')

# Test 2: Resumen rápido
print("\n📊 Test 2: Resumen de estadísticas:\n")
for col in ['over_rate', 'integrity_risk_score', 'mrv_quality']:
    resumen = resumen_estadistico(df[col], col)
    print(f"{col}:")
    print(f"  - Media: {resumen['media']:.4f}")
    print(f"  - Std: {resumen['std']:.4f}")
    print(f"  - Range: [{resumen['min']:.4f}, {resumen['max']:.4f}]")
    print()

# Test 3: Validar columnas
print("\n✓ Test 3: Validación de columnas")
try:
    validar_columnas(df, ['over_rate', 'integrity_risk_score', 'type'])
    print("   ✓ Todas las columnas requeridas existen")
except ValueError as e:
    print(f"   ✗ Error: {e}")

# Test 4: Normalización
print("\n📈 Test 4: Normalización de datos")
df_norm = df[['over_rate']].copy()
df_norm['over_rate_minmax'] = normalizar_serie(df['over_rate'], método='minmax')
df_norm['over_rate_zscore'] = normalizar_serie(df['over_rate'], método='zscore')
print("Primeros 5 registros:")
print(df_norm.head())

# Test 5: Tabla cruzada
print("\n🔀 Test 5: Tabla cruzada - Proyectos por tipo y país:\n")
tabla_cruzada = pd.crosstab(df['type'], df['country'])
print(tabla_cruzada)

# Test 6: Top N por grupo
print("\n🏆 Test 6: Top 3 proyectos con mayor over_rate por tipo:\n")
top_3 = top_n_por_grupo(df, 'type', 'over_rate', n=3)
print(top_3[['project_id', 'type', 'over_rate']].to_string())

# Test 7: Percentil categorizado
print("\n📊 Test 7: Categorización de over_rate en cuartiles:\n")
df['over_rate_q'] = percentil_categorizado(df['over_rate'], categorias=4)
print(pd.crosstab(df['over_rate_q'], df['type']))

# Test 8: Duplicados
print("\n🔍 Test 8: Detección de duplicados:")
n_duplicados = len(detectar_duplicados(df))
print(f"   Duplicados encontrados: {n_duplicados}")

# Test 9: Resumen tabla
print("\n📋 Test 9: Tabla de resumen (primeras 3 variables):\n")
resumen_tabla = crear_resumen_tabla(df, df.columns[:3])
print(resumen_tabla.to_string(index=False))

# Test 10: Cambio porcentual
print("\n📈 Test 10: Cambio porcentual")
cambio = calcular_cambio_porcentual(100, 125)
print(f"   Cambio de 100 a 125: {cambio:.2f}%")

print("\n✨ Todos los tests completados exitosamente\n")
