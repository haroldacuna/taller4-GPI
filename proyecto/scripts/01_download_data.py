"""
Script para descargar datos desde Zenodo API.

Este script descarga los archivos CSV de datos raw desde un repositorio de Zenodo
y los guarda en el directorio data/raw del proyecto.
"""

from pathlib import Path
import requests
import sys

from src.config import SimConfig


def download_file(url: str, destination: Path) -> bool:
    """
    Descarga un archivo desde una URL y lo guarda en el destino especificado.
    
    Args:
        url: URL del archivo a descargar
        destination: Ruta donde guardar el archivo
        
    Returns:
        True si la descarga fue exitosa, False en caso contrario
    """
    try:
        print(f"Descargando: {url}")
        response = requests.get(url, stream=True, timeout=60)
        response.raise_for_status()
        
        destination.parent.mkdir(parents=True, exist_ok=True)
        
        with open(destination, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
        
        file_size = destination.stat().st_size
        print(f"✓ Descargado: {destination.name} ({file_size:,} bytes)")
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error descargando {url}: {e}")
        return False
    except Exception as e:
        print(f"✗ Error inesperado: {e}")
        return False


def get_zenodo_files(record_id: str) -> dict:
    """
    Obtiene la lista de archivos disponibles en un record de Zenodo.
    
    Args:
        record_id: ID del record en Zenodo
        
    Returns:
        Diccionario con nombres de archivo como claves y URLs como valores
    """
    api_url = f"https://zenodo.org/api/records/{record_id}"
    
    try:
        print(f"Consultando Zenodo API: {api_url}")
        response = requests.get(api_url, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        files = {}
        for file_info in data.get('files', []):
            filename = file_info.get('key')
            file_url = file_info.get('links', {}).get('self')
            if filename and file_url:
                files[filename] = file_url
        
        print(f"✓ Archivos disponibles en Zenodo: {list(files.keys())}")
        return files
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error consultando Zenodo API: {e}")
        return {}
    except Exception as e:
        print(f"✗ Error procesando respuesta de Zenodo: {e}")
        return {}


def main():
    """
    Función principal que descarga todos los archivos necesarios desde Zenodo.
    """
    cfg = SimConfig()
    
    # Configurar directorios
    base = Path(__file__).resolve().parents[1]
    raw_dir = base / "data" / "raw"
    
    # Archivos esperados
    required_files = ["projects.csv", "prices.csv", "issuance.csv"]
    
    print(f"\n{'='*70}")
    print("DESCARGA DE DATOS DESDE ZENODO")
    print(f"{'='*70}")
    print(f"Record ID: {cfg.zenodo_record_id}")
    print(f"Destino: {raw_dir}")
    print(f"{'='*70}\n")
    
    # Obtener lista de archivos en Zenodo
    zenodo_files = get_zenodo_files(cfg.zenodo_record_id)
    
    if not zenodo_files:
        print("\n✗ ERROR: No se pudieron obtener los archivos de Zenodo.")
        print("Verifica que el record ID sea correcto y que el repositorio sea público.")
        sys.exit(1)
    
    # Descargar cada archivo requerido
    success_count = 0
    failed_files = []
    
    for filename in required_files:
        if filename not in zenodo_files:
            print(f"✗ Archivo no encontrado en Zenodo: {filename}")
            failed_files.append(filename)
            continue
        
        destination = raw_dir / filename
        file_url = zenodo_files[filename]
        
        if download_file(file_url, destination):
            success_count += 1
        else:
            failed_files.append(filename)
    
    # Resumen final
    print(f"\n{'='*70}")
    print("RESUMEN DE DESCARGA")
    print(f"{'='*70}")
    print(f"Archivos descargados exitosamente: {success_count}/{len(required_files)}")
    
    if failed_files:
        print(f"Archivos con errores: {', '.join(failed_files)}")
        sys.exit(1)
    else:
        print("✓ Todos los archivos descargados correctamente")
        print(f"✓ Datos disponibles en: {raw_dir}")
        print(f"{'='*70}\n")
        sys.exit(0)


if __name__ == "__main__":
    main()
