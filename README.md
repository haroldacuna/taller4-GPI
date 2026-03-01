# Taller 4 GPI

## Descripción General

Este proyecto es un simulador integral de proyectos de carbono que modela la dinámica del mercado de créditos de carbono internacionales. Genera datos realistas de emisión, retiro y precios de créditos de carbono, junto con análisis de riesgo de integridad para diferentes tipos de proyectos.

## Objetivo

Simular y analizar el comportamiento de proyectos de reducción de emisiones de carbono bajo el esquema de Reducción de Emisiones por Deforestación y Degradación (REDD+), Afforestación/Reforestación (ARR), proyectos de cocinas limpias (Cookstoves) y energías renovables (Renewables), considerando aspectos críticos como:

- Adicionalidad y rigor metodológico
- Riesgos de permanencia y fugas (leakage)
- Calidad de monitoreo, reporteo y verificación (MRV)
- Integridad de los créditos emitidos
- Dinámicas de precios del mercado
- Retiros de créditos por parte de compradores

## Estructura del Proyecto

```
proyecto/
├── data/
│   ├── raw/                          # Datos generados por la simulación
│   │   ├── projects.csv              # Características de los 150 proyectos
│   │   ├── issuance.csv              # Emisión mensual de créditos
│   │   └── prices.csv                # Precios mensuales del carbono
│   └── processed/                    # Datos procesados y análisis
│       ├── project_summary.csv       # Resumen a nivel de proyecto
│       └── issuance_with_revenue.csv # Ingresos por venta de créditos
├── results/
│   ├── figures/                      # Gráficos y visualizaciones
│   ├── exploratory/                  # Resultados de análisis exploratorio (EDA)
│   └── tables/                       # Tablas de análisis y regresión
│       └── top20_high_risk_projects.csv  # Top 20 proyectos de mayor riesgo
├── scripts/
│   ├── 01_download_data.py          # Descarga de datos desde Zenodo
│   ├── 02_analyze.py                # Análisis y procesamiento
│   ├── 03_visualize.py              # Visualizaciones
│   ├── 04_exploratory_analysis.py   # Análisis exploratorio (EDA)
│   ├── 05_regression_analysis.py    # Análisis de regresión
│   └── test_utilidades.py           # Pruebas unitarias
├── src/
│   ├── config.py                    # Parámetros de configuración
│   ├── analysis.py                  # Funciones de análisis
│   ├── visualization.py             # Funciones de visualización
│   └── utilidades.py                # Funciones de utilidad
├── environment.yml                  # Dependencias conda
├── runall.sh                        # Script bash para ejecutar el flujo completo
└── runall.ps1                       # Script PowerShell para ejecutar el flujo completo
```

## Flujo de Trabajo

El proyecto sigue un flujo de cinco etapas:

### 1. **Descarga de Datos** (`01_download_data.py`)

Descarga los datos raw desde Zenodo (https://doi.org/10.5281/zenodo.18819966):

#### **projects.csv** (150 proyectos)
- Identificadores únicos, tipos y ubicaciones geográficas
- Características físicas: área (hectáreas), baseline de emisiones
- Indicadores de calidad: adicionalidad, calidad MRV
- Factores de riesgo: tasa de fugas, riesgo de permanencia
- Parámetros de verificación: frecuencia, contribución a buffer

#### **issuance.csv** (emisión mensual)
- Reducción "verdadera" de emisiones (basada en baseline y adicionalidad)
- Reducción "reportada" (incluye sesgos por baja calidad MRV)
- Créditos emitidos y retirados
- Créditos en buffer de permanencia
- Estimaciones de overcrediting
- Flags de riesgo de entrega

#### **prices.csv** (precios mensuales)
- Precios de carbono con tendencia alcista
- Volatilidad estocástica
- Shocks ocasionales de mercado
- Rango realista: USD 2–25 por tonelada de CO₂

### 2. **Análisis** (`02_analyze.py`)

Procesa datos brutos y genera análisis descriptivo:

#### **project_summary.csv**
Agrega datos a nivel de proyecto:
- Totales de emisiones verdaderas vs. reportadas
- Totales de créditos emitidos, retirados y en buffer
- Tasa de overcrediting (% del reported que es overcredited)
- Tasa de retiro (% de emitidos que fueron retirados)
- **Integrity Risk Score**: métrica sintética que combina:
  - Baja calidad MRV (45% de peso)
  - Baja adicionalidad (25%)
  - Riesgo de permanencia (20%)
  - Tasa de fugas (10%)

#### **issuance_with_revenue.csv**
Calcula ingresos financieros:
- Ingresos brutos = créditos retirados × precio del carbono
- Permite análisis de rentabilidad por mes y proyecto

#### **top20_high_risk_projects.csv**
Ranking de los 20 proyectos con mayor puntuación de riesgo de integridad.

### 3. **Visualización** (`03_visualize.py`)

Genera gráficos para explorar patrones en:
- Distribución de riesgos por tipo de proyecto y geografía
- Evolución de precios y correlación con retiros
- Tendencias de overcrediting
- Análisis de cohorte temporal

### 4. **Análisis Exploratorio (EDA)** (`04_exploratory_analysis.py`)

Realiza un análisis exploratorio comprehensivo que incluye:

#### Estadísticas descriptivas detalladas
- Medidas de tendencia central y dispersión
- Índices de asimetría (skewness) y curtosis
- Análisis por variable clave

#### Análisis de correlaciones
- Correlaciones de Pearson entre variables numéricas
- Identificación de relaciones significativas
- Matrices de correlación para proyectos y resúmenes

#### Detección de outliers
- Identificación sistemática usando IQR (Interquartile Range)
- Detección en variables críticas: área, baseline, reducciones
- Resumen de outliers por variable

#### Análisis temporal
- Series de tiempo mensuales agregadas
- Promedios móviles (rolling means) de 3 y 6 meses
- Tendencias de emisión, retiros e ingresos

#### Análisis de riesgo
- Distribución de proyectos por niveles de riesgo (bajo, medio, alto)
- Análisis de riesgo por tipo de proyecto
- Top 20 proyectos con mayor overcrediting

#### Análisis por grupos
- Análisis segmentado por tipo de proyecto
- Análisis segmentado por país
- Estadísticas comparativas entre grupos

#### Reporte de calidad de datos
- Detección de valores faltantes
- Identificación de valores atípicos
- Estadísticas de completitud

#### Salidas generadas (en `results/exploratory/`):
- `project_statistics.csv` - Estadísticas de proyectos
- `summary_statistics.csv` - Estadísticas de resumen
- `correlations_*.csv` - Matrices de correlación
- `outliers_*.csv` - Outliers por variable
- `time_series_*.csv` - Series temporales
- `analysis_by_type.csv` - Análisis por tipo de proyecto
- `analysis_by_country.csv` - Análisis por país
- `risk_*.csv` - Análisis de riesgo
- `quality_report_*.csv` - Reportes de calidad

### 5. **Análisis de Regresión** (`05_regression_analysis.py`)

Entrena múltiples modelos de regresión para predecir métricas clave:

#### Variables objetivo (targets):
1. **over_rate**: Tasa de sobrecreditación
2. **integrity_risk_score**: Score de riesgo de integridad
3. **retire_rate**: Tasa de retiro de créditos

#### Features utilizadas:
- **Variables de calidad**: mrv_quality, additionality_score, leakage_rate, permanence_risk
- **Variables de proyecto**: baseline_tCO2, area_ha, verification_frequency_months, buffer_contribution_rate

#### Modelos entrenados:
- **Regresión Lineal**: Modelos con variables de calidad solamente y con todas las variables
- **Ridge Regression**: Modelo regularizado para over_rate
- Comparación sistemática de rendimiento

#### Métricas de evaluación:
- R² (Coeficiente de determinación)
- RMSE (Root Mean Squared Error)
- MAE (Mean Absolute Error)
- Análisis de residuos

#### Salidas generadas (en `results/tables/`):
- `regression_coef_*.csv` - Coeficientes de los modelos
- `regression_metrics_*.csv` - Métricas de rendimiento
- `regression_predictions_*.csv` - Predicciones vs valores reales
- `regression_worst_predictions_*.csv` - Peores predicciones por modelo
- `regression_model_comparison.csv` - Comparación entre modelos
- `regression_best_by_target.csv` - Mejores modelos por variable objetivo
- Estadísticas adicionales: correlaciones, frecuencias, pruebas de normalidad

## Parámetros de Configuración

Los parámetros se definen en `src/config.py`:

```python
@dataclass(frozen=True)
class SimConfig:
    seed: int = 42              # Semilla para reproducibilidad
    n_projects: int = 150       # Número de proyectos
    start_month: str = "2020-01-01"  # Fecha de inicio
    n_months: int = 60          # Duración en meses (5 años)
```

Puede personalizarse creando una instancia con parámetros diferentes:

```python
from src.config import SimConfig
cfg = SimConfig(seed=123, n_projects=200, n_months=120)
```

## Tipos de Proyectos

El simulador genera cuatro tipos de proyectos con características diferenciadas:

| Tipo | Proporción | Características |
|------|-----------|-----------------|
| REDD+ | 35% | Grandes áreas, altos baselines, variable MRV |
| ARR | 20% | Muy grandes, baselines moderados, buena permanencia |
| Cookstoves | 25% | Pequeños, adicionalidad moderada, riesgos bajos |
| Renewables | 20% | Diversos tamaños, buena adicionalidad, riesgos mínimos |

### Distribución Geográfica

Seis países representativos:
- Colombia, Perú, Brasil (América Latina - REDD+/ARR)
- México (mixto)
- Kenya, Indonesia (trópicos remotos)

## Modelos de Simulación

### Reducción Verdadera vs. Reportada

La brecha entre emisiones "verdaderas" reportadas es modelada explícitamente:

- **Verdadera**: `baseline × (0.25 + 0.55×adicionalidad) × (1 - fugas) × (1 - 0.25×permanence_risk)`
- **Reportada**: `verdadera × (1 + bias_esperado + ruido)`
  - `bias_esperado = 0.35×(1 - MRV_quality) + 0.20×(1 - adicionalidad) + penalidad_verification`

### Factores de Riesgo

| Factor | Impacto | Modelado |
|--------|---------|----------|
| Calidad MRV | ↑ overcrediting | Distribución Beta(2.5, 1.7) |
| Adicionalidad | ↑ credibilidad | Distribución Beta(2.2, 1.8) |
| Permanencia | ↑ riesgo futuro | Distribución Beta variable |
| Fugas | ↓ emisiones netas | N(0.12, 0.08) truncada |

### Créditos y Retiros

- **Emitidos**: 1 tCO2 de reportado = 1 crédito (sin buffer)
- **Buffer**: Descuento de 5–35% según riesgos combinados
- **Retiros**: Fracción estocástica de emitidos netos (media 35%)

## Instalación y Uso

### Requisitos

- Python 3.8+
- conda o miniconda

### Instalación

```bash
# Clonar o descargar el repositorio
cd proyecto

# Crear ambiente conda
conda env create -f environment.yml

# Activar ambiente
conda activate gpi-carbon
```

### Ejecución

**Opción 1: Ejecutar el flujo completo (scripts 1-3)**

```bash
bash runall.sh
```

O en PowerShell:
```powershell
.\runall.ps1
```

**Opción 2: Ejecutar flujo completo con análisis avanzado (scripts 1-5)**

```bash
bash runall.sh
python scripts/04_exploratory_analysis.py
python scripts/05_regression_analysis.py
```

**Opción 3: Ejecutar scripts individualmente**

```bash
# 1. Descargar datos desde Zenodo
python scripts/01_download_data.py

# 2. Análisis y procesamiento
python scripts/02_analyze.py

# 3. Visualización
python scripts/03_visualize.py

# 4. Análisis exploratorio (EDA)
python scripts/04_exploratory_analysis.py

# 5. Análisis de regresión
python scripts/05_regression_analysis.py
```

## Salidas Principales

### CSV Generados

1. **data/raw/**
   - `projects.csv`: 150 filas × 14 columnas (características de proyectos)
   - `issuance.csv`: 150 × 60 = 9,000 filas (emisiones mensuales)
   - `prices.csv`: 60 filas (precios mensuales)

2. **data/processed/**
   - `project_summary.csv`: 150 filas con resúmenes y riesgos
   - `issuance_with_revenue.csv`: 9,000 filas con ingresos en USD

3. **results/exploratory/** (generados por script 04)
   - `project_statistics.csv`: Estadísticas descriptivas de proyectos
   - `summary_statistics.csv`: Estadísticas de resumen agregado
   - `correlations_projects.csv` y `correlations_summary.csv`: Matrices de correlación
   - `outliers_*.csv`: Outliers detectados por variable (área, baseline, reducciones)
   - `time_series_*.csv`: Series temporales mensuales y con promedios móviles
   - `analysis_by_type.csv` y `analysis_by_country.csv`: Análisis por grupos
   - `risk_*.csv`: Análisis de niveles de riesgo
   - `quality_report_*.csv`: Reportes de calidad de datos
   - `top20_overcrediting.csv`: Top 20 proyectos con mayor overcrediting

4. **results/tables/** (generados por scripts 02 y 05)
   - `top20_high_risk_projects.csv`: Top 20 de mayor riesgo de integridad
   - `estadisticas_*.csv`: Estadísticas por tipo y país
   - `correlacion_*.csv`: Correlaciones de Pearson y Spearman
   - `frecuencias_*.csv`: Distribuciones de frecuencia
   - `pruebas_normalidad.csv`: Pruebas de normalidad
   - `regression_coef_*.csv`: Coeficientes de modelos de regresión (9 modelos)
   - `regression_metrics_*.csv`: Métricas de rendimiento de modelos
   - `regression_predictions_*.csv`: Predicciones de cada modelo
   - `regression_worst_predictions_*.csv`: Peores predicciones por modelo
   - `regression_model_comparison.csv`: Comparación entre modelos
   - `regression_best_by_target.csv`: Mejor modelo por variable objetivo
   - `resumen_outliers.csv`: Resumen de outliers detectados

### Gráficos (si están implementados)

Ubicados en `results/figures/`:
- Distribución de riesgos de integridad
- Evolución de precios y retiros
- Correlación entre variables

## Indicadores Clave

### Integrity Risk Score

Métrica compuesta (0–1, donde 1 es máximo riesgo):

$$\text{Score} = 0.45(1 - \text{MRV}_\text{quality}) + 0.25(1 - \text{adicionalidad}) + 0.20 \times \text{permanence\_risk} + 0.10 \times \text{leakage\_rate}$$

### Tasa de Overcrediting

$$\text{Over\\_rate} = \frac{\sum \text{overcrediting\_tCO}_2}{\sum \text{reported\_reduction\_tCO}_2}$$

### Tasa de Retiro

$$\text{Retire\\_rate} = \frac{\sum \text{retired\_credits}}{\sum \text{issued\_credits}}$$

### Ingresos Brutos

$$\text{Revenue (USD)} = \text{retired\_credits} \times \text{monthly\_price}$$

## Capacidades de Análisis Avanzado

### Análisis Exploratorio (Script 04)

El análisis exploratorio proporciona una comprensión profunda de los datos mediante:

#### Métricas Estadísticas
- Medidas de tendencia central (media, mediana)
- Medidas de dispersión (desviación estándar, rango intercuartílico)
- Índices de forma de distribución (asimetría y curtosis)

#### Análisis de Relaciones
- Correlaciones lineales (Pearson) entre variables
- Identificación de variables altamente correlacionadas
- Matrices de correlación para análisis multivariado

#### Detección de Anomalías
- Identificación de outliers mediante método IQR
- Análisis de valores atípicos en variables críticas
- Resumen de frecuencia de outliers por variable

#### Análisis Temporal
- Agregaciones mensuales de emisiones, retiros e ingresos
- Suavizado de series con promedios móviles (3 y 6 meses)
- Identificación de tendencias y patrones estacionales

#### Segmentación
- Comparación de métricas entre tipos de proyectos
- Análisis por país de origen
- Distribución de riesgo por categorías

### Análisis de Regresión (Script 05)

El análisis de regresión permite predecir y entender los factores que influyen en:

#### Modelos Predictivos
1. **Predicción de Overcrediting**
   - Identifica variables que contribuyen a sobrecreditación
   - Cuantifica el impacto de calidad MRV y adicionalidad
   - Modelo regularizado (Ridge) para mayor estabilidad

2. **Predicción de Riesgo de Integridad**
   - Explica factores que componen el riesgo
   - Evalúa peso relativo de cada componente
   - Identifica proyectos en alto riesgo

3. **Predicción de Tasa de Retiro**
   - Analiza qué características favorecen retiros
   - Evalúa relación entre calidad y demanda
   - Identifica proyectos más atractivos para compradores

#### Interpretabilidad
- Coeficientes estandarizados para comparación
- Análisis de residuos para validar supuestos
- Identificación de predicciones problemáticas
- Comparación sistemática entre modelos

#### Validación
- División train/test (80/20)
- Múltiples métricas de rendimiento (R², RMSE, MAE)
- Validación de supuestos de regresión lineal

## Limitaciones y Supuestos

1. **Supuestos simplificadores**:
   - No modela ciclos económicos complejos
   - Precios generados sintéticamente (no históricos reales)
   - Retiros son estocásticos sin modelar comportamiento de compradores específico

2. **Restricciones**:
   - No incluye análisis de leyes o regulaciones
   - No modela dinámicas de doble conteo
   - Buffer modelado como descuento simple (no como holdings físicos)

3. **Alcance**:
   - Enfocado en dinámica de emisión y mercado
   - No incluye aspectos de adaptación o co-beneficios

## Dependencias

```yaml
python=3.9
numpy
pandas
matplotlib
seaborn
scikit-learn
scipy
requests
```

Ver `environment.yml` para lista completa.

## Autor y Contexto

Taller 4 - Maestría en Gestión de Proyectos de Inversión (GPI)
Universidad Nacional de Colombia

## Licencia

Código de propósito educativo. Libre para uso académico