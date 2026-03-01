# Script de PowerShell para ejecutar el pipeline completo
# Autor: Taller 4 GPI

Write-Host "`n======================================================================"
Write-Host "PIPELINE COMPLETO - ANÁLISIS DE PROYECTOS DE CARBONO"
Write-Host "======================================================================`n"

# Configurar PYTHONPATH
$env:PYTHONPATH = $PWD

# 1. Descargar datos desde Zenodo
Write-Host "PASO 1/3: Descargando datos desde Zenodo..."
Write-Host "----------------------------------------------------------------------"
python scripts/01_download_data.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ ERROR: Fallo en la descarga de datos" -ForegroundColor Red
    exit 1
}

# 2. Análisis de datos
Write-Host "`nPASO 2/3: Analizando datos..."
Write-Host "----------------------------------------------------------------------"
python scripts/02_analyze.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ ERROR: Fallo en el análisis" -ForegroundColor Red
    exit 1
}

# 3. Visualización
Write-Host "`nPASO 3/3: Generando visualizaciones..."
Write-Host "----------------------------------------------------------------------"
python scripts/03_visualize.py
if ($LASTEXITCODE -ne 0) {
    Write-Host "`n✗ ERROR: Fallo en la visualización" -ForegroundColor Red
    exit 1
}

Write-Host "`n======================================================================"
Write-Host "Pipeline completo ✅" -ForegroundColor Green
Write-Host "======================================================================`n"
