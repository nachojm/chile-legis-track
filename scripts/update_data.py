"""
Script principal para actualizar datos del sitio web
Este script orquesta la recolección y procesamiento de datos
"""

import sys
import os
from datetime import datetime

# Añadir el directorio scripts al path
sys.path.insert(0, os.path.dirname(__file__))

from api_client import CamaraAPI
from data_processor import DataProcessor
import json
import shutil


def actualizar_datos_votaciones(annos=[2023, 2024]):
    """
    Actualiza datos de votaciones para los años especificados
    
    Args:
        annos (list): Lista de años a consultar
    """
    print("="*70)
    print("ACTUALIZANDO DATOS DE VOTACIONES")
    print("="*70)
    
    api = CamaraAPI(output_dir='data/raw')
    processor = DataProcessor(input_dir='data/raw', output_dir='data/processed')
    
    todas_votaciones = []
    
    for anno in annos:
        print(f"\n📅 Procesando año {anno}...")
        
        # Obtener datos del API
        xml_data = api.obtener_votaciones_por_anno(anno)
        
        if xml_data:
            # Parsear XML
            votaciones = api.parsear_xml_votaciones(xml_data)
            
            if votaciones:
                # Guardar JSON individual por año
                api.guardar_json(votaciones, f'votaciones_{anno}.json')
                todas_votaciones.extend(votaciones)
                print(f"  ✓ {len(votaciones)} votaciones del año {anno}")
            else:
                print(f"  ✗ No se pudieron parsear votaciones de {anno}")
        else:
            print(f"  ✗ No se pudieron obtener datos de {anno}")
    
    return todas_votaciones


def generar_datos_para_sitio(votaciones):
    """
    Genera archivos JSON optimizados para el sitio web
    
    Args:
        votaciones (list): Lista de votaciones
    """
    print("\n" + "="*70)
    print("GENERANDO DATOS PARA SITIO WEB")
    print("="*70)
    
    if not votaciones:
        print("✗ No hay votaciones para procesar")
        return
    
    # Crear directorio docs/data si no existe
    os.makedirs('docs/data', exist_ok=True)
    
    # 1. Datos completos (limitados)
    datos_completos = {
        'metadata': {
            'fecha_actualizacion': datetime.now().isoformat(),
            'total_votaciones': len(votaciones),
            'version': '1.0'
        },
        'votaciones': votaciones[:500]  # Limitar para performance
    }
    
    with open('docs/data/votaciones.json', 'w', encoding='utf-8') as f:
        json.dump(datos_completos, f, ensure_ascii=False, indent=2)
    print("✓ Generado: docs/data/votaciones.json")
    
    # 2. Estadísticas resumen
    stats = {
        'total_votaciones': len(votaciones),
        'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
    }
    
    # Intentar extraer más estadísticas si los campos existen
    if votaciones:
        primer_registro = votaciones[0]
        stats['campos_disponibles'] = list(primer_registro.keys())
    
    with open('docs/data/estadisticas.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print("✓ Generado: docs/data/estadisticas.json")
    
    # 3. README con info de última actualización
    readme_content = f"""# Datos - Seguimiento Legislativo Chile

**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Archivos Disponibles

- `votaciones.json`: Datos completos de votaciones (últimas 500)
- `estadisticas.json`: Estadísticas y metadata

## Fuente

Datos obtenidos de [OpenData Cámara de Diputados](https://opendata.camara.cl/)

---

*Datos actualizados automáticamente por scripts/update_data.py*
"""
    
    with open('docs/data/README.md', 'w', encoding='utf-8') as f:
        f.write(readme_content)
    print("✓ Generado: docs/data/README.md")


def explorar_estructura_datos(votaciones):
    """
    Explora y muestra la estructura de los datos obtenidos
    
    Args:
        votaciones (list): Lista de votaciones
    """
    if not votaciones:
        print("No hay datos para explorar")
        return
    
    print("\n" + "="*70)
    print("ESTRUCTURA DE DATOS")
    print("="*70)
    
    print(f"\nTotal registros: {len(votaciones)}")
    print(f"\nCampos disponibles en primer registro:")
    
    primer_registro = votaciones[0]
    for key, value in primer_registro.items():
        tipo_valor = type(value).__name__
        preview = str(value)[:50] if value else 'None'
        print(f"  • {key} ({tipo_valor}): {preview}")


def main():
    """Función principal"""
    
    print("\n" + "🇨🇱 " * 20)
    print("ACTUALIZADOR DE DATOS - SEGUIMIENTO LEGISLATIVO CHILE")
    print("🇨🇱 " * 20 + "\n")
    
    # Años a consultar (puedes modificar esto)
    annos_a_consultar = [2024]  # Empezar solo con 2024
    
    try:
        # 1. Obtener datos del API
        votaciones = actualizar_datos_votaciones(annos_a_consultar)
        
        # 2. Explorar estructura
        if votaciones:
            explorar_estructura_datos(votaciones)
            
            # 3. Generar archivos para sitio web
            generar_datos_para_sitio(votaciones)
            
            print("\n" + "="*70)
            print("✅ PROCESO COMPLETADO EXITOSAMENTE")
            print("="*70)
            print("\nPróximos pasos:")
            print("1. Revisa los archivos generados en data/")
            print("2. Verifica docs/data/votaciones.json")
            print("3. Haz commit de los cambios en GitHub Desktop")
            print("4. Push para actualizar el sitio web")
        else:
            print("\n" + "="*70)
            print("⚠️  NO SE OBTUVIERON DATOS")
            print("="*70)
            print("\nPosibles causas:")
            print("- El API podría estar caído")
            print("- Los años consultados no tienen datos")
            print("- Error de conexión a Internet")
            
    except Exception as e:
        print(f"\n❌ ERROR FATAL: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()