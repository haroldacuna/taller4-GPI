"""
Módulo de utilidades para el proyecto de análisis de carbono.

Este módulo proporciona funciones helper para:
- Manejo de archivos y rutas
- Validación de datos
- Formateo y visualización
- Cálculos estadísticos comunes
- Logging y manejo de errores
- Exportación de resultados
"""

from pathlib import Path
import pandas as pd
import numpy as np
from typing import Union, Tuple, List, Dict, Any
import logging
from datetime import datetime
import json
import sys


# ============================================================================
# CONFIGURACIÓN DE LOGGING
# ============================================================================

def configurar_logger(nombre: str = __name__, nivel: int = logging.INFO) -> logging.Logger:
    """
    Configura un logger personalizado.
    
    Args:
        nombre: Nombre del logger
        nivel: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
    
    Returns:
        Logger configurado
    """
    logger = logging.getLogger(nombre)
    logger.setLevel(nivel)
    
    # Handler para consola
    handler_console = logging.StreamHandler(sys.stdout)
    handler_console.setLevel(nivel)
    
    # Formato
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    handler_console.setFormatter(formatter)
    
    logger.addHandler(handler_console)
    return logger


logger = configurar_logger(__name__)


# ============================================================================
# MANEJO DE RUTAS Y ARCHIVOS
# ============================================================================

def obtener_ruta_base() -> Path:
    """
    Obtiene la ruta base del proyecto.
    
    Returns:
        Path al directorio base del proyecto
    """
    return Path(__file__).resolve().parents[1]


def obtener_rutas_directorios() -> Dict[str, Path]:
    """
    Retorna diccionario con todas las rutas importantes del proyecto.
    
    Returns:
        Diccionario con rutas estándar
    """
    base = obtener_ruta_base()
    
    return {
        'base': base,
        'data_raw': base / 'data' / 'raw',
        'data_processed': base / 'data' / 'processed',
        'scripts': base / 'scripts',
        'src': base / 'src',
        'results': base / 'results',
        'results_tables': base / 'results' / 'tables',
        'results_figures': base / 'results' / 'figures',
        'results_exploratory': base / 'results' / 'exploratory'
    }


def crear_directorio(ruta: Union[str, Path]) -> Path:
    """
    Crea un directorio si no existe.
    
    Args:
        ruta: Ruta del directorio a crear
    
    Returns:
        Path creado
    """
    ruta = Path(ruta)
    ruta.mkdir(parents=True, exist_ok=True)
    logger.debug(f"Directorio creado/verificado: {ruta}")
    return ruta


def archivo_existe(ruta: Union[str, Path]) -> bool:
    """
    Verifica si un archivo existe.
    
    Args:
        ruta: Ruta del archivo
    
    Returns:
        True si existe, False en caso contrario
    """
    return Path(ruta).exists()


# ============================================================================
# CARGA Y VALIDACIÓN DE DATOS
# ============================================================================

def cargar_csv(ruta: Union[str, Path], **kwargs) -> pd.DataFrame:
    """
    Carga un archivo CSV con manejo de errores.
    
    Args:
        ruta: Ruta del archivo CSV
        **kwargs: Argumentos adicionales para pd.read_csv
    
    Returns:
        DataFrame cargado
    """
    ruta = Path(ruta)
    
    if not ruta.exists():
        raise FileNotFoundError(f"Archivo no encontrado: {ruta}")
    
    try:
        df = pd.read_csv(ruta, **kwargs)
        logger.info(f"✓ Cargado: {ruta.name} ({len(df)} registros)")
        return df
    except Exception as e:
        logger.error(f"Error al cargar {ruta}: {e}")
        raise


def guardar_csv(df: pd.DataFrame, ruta: Union[str, Path], 
                index: bool = False, **kwargs) -> Path:
    """
    Guarda un DataFrame a CSV.
    
    Args:
        df: DataFrame a guardar
        ruta: Ruta de destino
        index: Si incluir índice
        **kwargs: Argumentos adicionales para to_csv
    
    Returns:
        Path del archivo guardado
    """
    ruta = Path(ruta)
    crear_directorio(ruta.parent)
    
    try:
        df.to_csv(ruta, index=index, **kwargs)
        logger.info(f"✓ Guardado: {ruta.name} ({len(df)} registros)")
        return ruta
    except Exception as e:
        logger.error(f"Error al guardar {ruta}: {e}")
        raise


def validar_columnas(df: pd.DataFrame, columnas_requeridas: List[str]) -> bool:
    """
    Valida que un DataFrame tenga todas las columnas requeridas.
    
    Args:
        df: DataFrame a validar
        columnas_requeridas: Lista de columnas que deben existir
    
    Returns:
        True si todas las columnas existen
    
    Raises:
        ValueError si faltan columnas
    """
    faltantes = set(columnas_requeridas) - set(df.columns)
    
    if faltantes:
        raise ValueError(f"Columnas faltantes: {faltantes}")
    
    logger.debug(f"✓ Validación de columnas exitosa")
    return True


def eliminar_nulos(df: pd.DataFrame, columns: List[str] = None) -> pd.DataFrame:
    """
    Elimina filas con valores nulos.
    
    Args:
        df: DataFrame a limpiar
        columns: Columnas específicas a revisar (None = todas)
    
    Returns:
        DataFrame sin valores nulos
    """
    if columns is None:
        df_clean = df.dropna()
    else:
        df_clean = df.dropna(subset=columns)
    
    filas_eliminadas = len(df) - len(df_clean)
    logger.info(f"Filas con nulos eliminadas: {filas_eliminadas}")
    
    return df_clean


# ============================================================================
# ESTADÍSTICAS Y CÁLCULOS
# ============================================================================

def resumen_estadistico(series: pd.Series, nombre: str = None) -> Dict[str, Any]:
    """
    Genera un resumen estadístico rápido.
    
    Args:
        series: Series a resumir
        nombre: Nombre de la serie
    
    Returns:
        Diccionario con resumen estadístico
    """
    return {
        'nombre': nombre or series.name,
        'tipo': str(series.dtype),
        'count': series.count(),
        'nulos': series.isnull().sum(),
        'media': series.mean() if pd.api.types.is_numeric_dtype(series) else None,
        'mediana': series.median() if pd.api.types.is_numeric_dtype(series) else None,
        'std': series.std() if pd.api.types.is_numeric_dtype(series) else None,
        'min': series.min(),
        'max': series.max(),
        'únicos': series.nunique()
    }


def calcular_cambio_porcentual(valor_inicial: float, valor_final: float) -> float:
    """
    Calcula cambio porcentual entre dos valores.
    
    Args:
        valor_inicial: Valor de inicio
        valor_final: Valor final
    
    Returns:
        Cambio porcentual
    """
    if valor_inicial == 0:
        return np.nan
    
    return ((valor_final - valor_inicial) / abs(valor_inicial)) * 100


def normalizar_serie(series: pd.Series, método: str = 'minmax') -> pd.Series:
    """
    Normaliza una serie.
    
    Args:
        series: Series a normalizar
        método: 'minmax' (0-1) o 'zscore' (media=0, std=1)
    
    Returns:
        Series normalizada
    """
    if método == 'minmax':
        return (series - series.min()) / (series.max() - series.min())
    elif método == 'zscore':
        return (series - series.mean()) / series.std()
    else:
        raise ValueError("Método debe ser 'minmax' o 'zscore'")


def percentil_categorizado(series: pd.Series, categorias: int = 4) -> pd.Series:
    """
    Categoriza una serie en percentiles.
    
    Args:
        series: Series numérica
        categorias: Número de categorías (ej: 4 = cuartiles)
    
    Returns:
        Series categorizada
    """
    labels = [f"Q{i+1}" for i in range(categorias)]
    return pd.qcut(series, q=categorias, labels=labels, duplicates='drop')


# ============================================================================
# FORMATEO Y VISUALIZACIÓN
# ============================================================================

def imprimir_seccion(titulo: str, nivel: int = 1):
    """
    Imprime un encabezado de sección formateado.
    
    Args:
        titulo: Título de la sección
        nivel: Nivel (1=principal, 2=subsección)
    """
    if nivel == 1:
        print("\n" + "=" * 80)
        print(f"  {titulo}")
        print("=" * 80 + "\n")
    else:
        print(f"\n--- {titulo} ---\n")


def imprimir_dataframe_formateado(df: pd.DataFrame, max_rows: int = 10, 
                                  max_cols: int = 8, decimales: int = 2):
    """
    Imprime un DataFrame con formato amigable.
    
    Args:
        df: DataFrame a imprimir
        max_rows: Máximo de filas
        max_cols: Máximo de columnas
        decimales: Decimales a mostrar
    """
    pd.set_option('display.max_rows', max_rows)
    pd.set_option('display.max_columns', max_cols)
    pd.set_option('display.float_format', lambda x: f'{x:.{decimales}f}')
    print(df)
    pd.reset_option('display.float_format')


def crear_resumen_tabla(df: pd.DataFrame, columnas: List[str] = None) -> pd.DataFrame:
    """
    Crea una tabla resumen de un DataFrame.
    
    Args:
        df: DataFrame a resumir
        columnas: Columnas a incluir (None = todas)
    
    Returns:
        DataFrame con resumen
    """
    if columnas is None:
        columnas = df.columns
    
    resumen = []
    for col in columnas:
        if pd.api.types.is_numeric_dtype(df[col]):
            resumen.append({
                'columna': col,
                'tipo': 'numérico',
                'válidos': df[col].count(),
                'nulos': df[col].isnull().sum(),
                'media': df[col].mean(),
                'mediana': df[col].median(),
                'mínim': df[col].min(),
                'máxim': df[col].max()
            })
        else:
            resumen.append({
                'columna': col,
                'tipo': 'categórico',
                'válidos': df[col].count(),
                'nulos': df[col].isnull().sum(),
                'únicos': df[col].nunique(),
                'moda': df[col].mode()[0] if len(df[col].mode()) > 0 else None
            })
    
    return pd.DataFrame(resumen)


# ============================================================================
# FILTRADO Y TRANSFORMACIÓN
# ============================================================================

def filtrar_por_rango(df: pd.DataFrame, columna: str, min_val: float = None, 
                      max_val: float = None) -> pd.DataFrame:
    """
    Filtra DataFrame por rango de valores.
    
    Args:
        df: DataFrame a filtrar
        columna: Columna a filtrar
        min_val: Valor mínimo
        max_val: Valor máximo
    
    Returns:
        DataFrame filtrado
    """
    df_copy = df.copy()
    
    if min_val is not None:
        df_copy = df_copy[df_copy[columna] >= min_val]
    
    if max_val is not None:
        df_copy = df_copy[df_copy[columna] <= max_val]
    
    logger.info(f"Filtrado: {len(df)} → {len(df_copy)} registros")
    return df_copy


def top_n_por_grupo(df: pd.DataFrame, grupo: str, valor: str, n: int = 10, 
                    ascendente: bool = False) -> pd.DataFrame:
    """
    Obtiene top N registros por grupo.
    
    Args:
        df: DataFrame
        grupo: Columna para agrupar
        valor: Columna para ordenar
        n: Número de registros por grupo
        ascendente: Ordenar ascendente
    
    Returns:
        DataFrame con top N por grupo
    """
    return df.groupby(grupo).apply(
        lambda x: x.nlargest(n, valor) if not ascendente else x.nsmallest(n, valor)
    ).reset_index(drop=True)


def crear_tabla_cruzada(df: pd.DataFrame, filas: str, columnas: str, 
                        valores: str = None, funcion: str = 'count') -> pd.DataFrame:
    """
    Crea una tabla cruzada (pivot table).
    
    Args:
        df: DataFrame
        filas: Columna para filas
        columnas: Columna para columnas
        valores: Columna para valores
        funcion: Función de agregación
    
    Returns:
        Tabla cruzada
    """
    return pd.pivot_table(
        df,
        values=valores,
        index=filas,
        columns=columnas,
        aggfunc=funcion,
        fill_value=0
    )


# ============================================================================
# VALIDACIONES Y CHEQUEOS
# ============================================================================

def validar_rango(valor: float, min_val: float, max_val: float, 
                  nombre: str = "valor") -> bool:
    """
    Valida que un valor esté en rango.
    
    Args:
        valor: Valor a validar
        min_val: Mínimo permitido
        max_val: Máximo permitido
        nombre: Nombre para mensajes
    
    Returns:
        True si está en rango
    
    Raises:
        ValueError si está fuera de rango
    """
    if not (min_val <= valor <= max_val):
        raise ValueError(
            f"{nombre} fuera de rango: {valor} (esperado [{min_val}, {max_val}])"
        )
    return True


def detectar_duplicados(df: pd.DataFrame, subset: List[str] = None) -> pd.DataFrame:
    """
    Detecta y retorna duplicados en un DataFrame.
    
    Args:
        df: DataFrame a revisar
        subset: Columnas a considerar (None = todas)
    
    Returns:
        DataFrame solo con duplicados
    """
    if subset is None:
        duplicados = df[df.duplicated(keep=False)]
    else:
        duplicados = df[df.duplicated(subset=subset, keep=False)]
    
    logger.info(f"Duplicados encontrados: {len(duplicados)}")
    return duplicados.sort_values(by=subset or list(df.columns))


def verificar_integridad_referencial(df: pd.DataFrame, columna_fk: str, 
                                      valores_validos: set) -> bool:
    """
    Verifica integridad referencial.
    
    Args:
        df: DataFrame
        columna_fk: Columna con referencias externas
        valores_validos: Conjunto de valores válidos
    
    Returns:
        True si todas las referencias son válidas
    
    Raises:
        ValueError si hay referencias inválidas
    """
    invalidas = set(df[columna_fk].unique()) - valores_validos
    
    if invalidas:
        raise ValueError(f"Referencias inválidas encontradas: {invalidas}")
    
    logger.info("✓ Integridad referencial verificada")
    return True


# ============================================================================
# EXPORTACIÓN Y SERIALIZACIÓN
# ============================================================================

def guardar_json(datos: Dict, ruta: Union[str, Path]) -> Path:
    """
    Guarda datos como JSON.
    
    Args:
        datos: Diccionario a guardar
        ruta: Ruta de destino
    
    Returns:
        Path del archivo guardado
    """
    ruta = Path(ruta)
    crear_directorio(ruta.parent)
    
    try:
        with open(ruta, 'w', encoding='utf-8') as f:
            json.dump(datos, f, indent=2, ensure_ascii=False)
        logger.info(f"✓ JSON guardado: {ruta.name}")
        return ruta
    except Exception as e:
        logger.error(f"Error al guardar JSON: {e}")
        raise


def cargar_json(ruta: Union[str, Path]) -> Dict:
    """
    Carga datos desde JSON.
    
    Args:
        ruta: Ruta del archivo JSON
    
    Returns:
        Diccionario cargado
    """
    ruta = Path(ruta)
    
    try:
        with open(ruta, 'r', encoding='utf-8') as f:
            datos = json.load(f)
        logger.info(f"✓ JSON cargado: {ruta.name}")
        return datos
    except Exception as e:
        logger.error(f"Error al cargar JSON: {e}")
        raise


def guardar_excel(df: pd.DataFrame, ruta: Union[str, Path], 
                  sheet_name: str = 'Sheet1', **kwargs) -> Path:
    """
    Guarda DataFrame como Excel.
    
    Args:
        df: DataFrame a guardar
        ruta: Ruta de destino
        sheet_name: Nombre de la hoja
        **kwargs: Argumentos adicionales
    
    Returns:
        Path del archivo guardado
    """
    ruta = Path(ruta)
    crear_directorio(ruta.parent)
    
    try:
        df.to_excel(ruta, sheet_name=sheet_name, index=False, **kwargs)
        logger.info(f"✓ Excel guardado: {ruta.name}")
        return ruta
    except Exception as e:
        logger.error(f"Error al guardar Excel: {e}")
        raise


# ============================================================================
# INFORMACIÓN DEL PROYECTO
# ============================================================================

def imprimir_informacion_proyecto():
    """Imprime información del proyecto."""
    rutas = obtener_rutas_directorios()
    
    imprimir_seccion("INFORMACIÓN DEL PROYECTO")
    
    print(f"""
    DirectorioBase: {rutas['base']}
    
    📁 Directorios:
       Data (raw):      {rutas['data_raw']}
       Data (proc):     {rutas['data_processed']}
       Scripts:         {rutas['scripts']}
       Results:         {rutas['results']}
       Tables:          {rutas['results_tables']}
       Figures:         {rutas['results_figures']}
    
    📦 Versión de dependencias:
       pandas:  {pd.__version__}
       numpy:   {np.__version__}
    """)


# ============================================================================
# DECORATORS (UTILIDADES DE FUNCIÓN)
# ============================================================================

def medir_tiempo(func):
    """Decorator para medir tiempo de ejecución."""
    import time
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        inicio = time.time()
        resultado = func(*args, **kwargs)
        duracion = time.time() - inicio
        logger.info(f"⏱️  {func.__name__} completado en {duracion:.2f}s")
        return resultado
    
    return wrapper


def manejo_errores(func):
    """Decorator para manejo genérico de errores."""
    from functools import wraps
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logger.error(f"Error en {func.__name__}: {e}")
            raise
    
    return wrapper
