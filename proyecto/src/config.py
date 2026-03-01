"""
Módulo de configuración para la simulación de proyectos.

Este módulo define los parámetros globales de configuración que se utilizan
en toda la simulación. Los valores pueden ser personalizados para ajustar
el comportamiento de la simulación sin modificar el código principal.

Uso:
    from config import SimConfig
    config = SimConfig(seed=42, n_projects=150)
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class SimConfig:
    """
    Clase de configuración inmutable para los parámetros de la simulación.
    
    Los parámetros se definen como atributos de clase con valores por defecto.
    La configuración es "frozen" (congelada), lo que significa que no puede ser
    modificada después de su creación, asegurando consistencia en los parámetros.
    
    Attributes:
        zenodo_record_id (str): ID del record en Zenodo con los datos raw.
        seed (int): Semilla aleatoria para reproducibilidad de resultados.
        n_projects (int): Número total de proyectos a simular.
        start_month (str): Fecha de inicio de la simulación en formato "YYYY-MM-DD".
        n_months (int): Duración de la simulación en meses.
    """
    
    zenodo_record_id: str = "18819966"
    """ID del record de Zenodo. Por defecto: 18819966 (https://doi.org/10.5281/zenodo.18819966)"""
    
    seed: int = 42
    """Semilla para el generador de números aleatorios. Por defecto: 42"""
    
    n_projects: int = 150
    """Cantidad de proyectos a incluir en la simulación. Por defecto: 150"""
    
    start_month: str = "2020-01-01"
    """Fecha de inicio de la simulación. Por defecto: 2020-01-01"""
    
    n_months: int = 60
    """Número de meses que durará la simulación. Por defecto: 60 (5 años)"""
