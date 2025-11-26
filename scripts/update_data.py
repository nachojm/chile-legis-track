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
    total_annos = len(annos)
    
    for idx, anno in enumerate(annos, 1):
        print(f"\n📅 [{idx}/{total_annos}] Procesando año {anno}...")
        
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
                print(f"  ⚠️  No se encontraron votaciones para {anno}")
        else:
            print(f"  ⚠️  No se pudieron obtener datos de {anno}")
        
        # Pequeña pausa para no sobrecargar el API
        if idx < total_annos:
            import time
            time.sleep(0.5)
    
    print(f"\n{'='*70}")
    print(f"✅ TOTAL ACUMULADO: {len(todas_votaciones)} votaciones")
    print(f"{'='*70}")
    
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
    
    # Ordenar votaciones por fecha (más recientes primero)
    votaciones_ordenadas = sorted(
        votaciones, 
        key=lambda x: x.get('Fecha', ''), 
        reverse=True
    )
    
    # 1. Datos completos (limitados a últimas 1000)
    datos_completos = {
        'metadata': {
            'fecha_actualizacion': datetime.now().isoformat(),
            'total_votaciones': len(votaciones_ordenadas),
            'anio_mas_antiguo': min(v.get('Fecha', '')[:4] for v in votaciones if v.get('Fecha')),
            'anio_mas_reciente': max(v.get('Fecha', '')[:4] for v in votaciones if v.get('Fecha')),
            'version': '2.0'
        },
        'votaciones': votaciones_ordenadas[:1000]  # Últimas 1000 para el sitio
    }
    
    with open('docs/data/votaciones.json', 'w', encoding='utf-8') as f:
        json.dump(datos_completos, f, ensure_ascii=False, indent=2)
    print(f"✓ Generado: docs/data/votaciones.json ({len(datos_completos['votaciones'])} votaciones)")
    
    # 2. Estadísticas por año
    stats_por_anio = {}
    for v in votaciones:
        if v.get('Fecha'):
            anio = v['Fecha'][:4]
            if anio not in stats_por_anio:
                stats_por_anio[anio] = {
                    'total': 0,
                    'aprobados': 0,
                    'rechazados': 0
                }
            stats_por_anio[anio]['total'] += 1
            
            if v.get('Resultado'):
                if 'aprobado' in v['Resultado'].lower():
                    stats_por_anio[anio]['aprobados'] += 1
                elif 'rechazado' in v['Resultado'].lower():
                    stats_por_anio[anio]['rechazados'] += 1
    
    # 3. Estadísticas resumen
    stats = {
        'total_votaciones': len(votaciones),
        'fecha_actualizacion': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
        'periodo': {
            'inicio': min(v.get('Fecha', '') for v in votaciones if v.get('Fecha'))[:10],
            'fin': max(v.get('Fecha', '') for v in votaciones if v.get('Fecha'))[:10]
        },
        'por_anio': stats_por_anio,
        'campos_disponibles': list(votaciones[0].keys()) if votaciones else []
    }
    
    with open('docs/data/estadisticas.json', 'w', encoding='utf-8') as f:
        json.dump(stats, f, ensure_ascii=False, indent=2)
    print(f"✓ Generado: docs/data/estadisticas.json")
    
    # 4. Resumen ejecutivo
    total_aprobados = sum(1 for v in votaciones if v.get('Resultado', '').lower().find('aprobado') >= 0)
    total_rechazados = sum(1 for v in votaciones if v.get('Resultado', '').lower().find('rechazado') >= 0)
    
    print(f"\n📊 RESUMEN:")
    print(f"  • Total votaciones: {len(votaciones):,}")
    print(f"  • Periodo: {stats['periodo']['inicio']} - {stats['periodo']['fin']}")
    print(f"  • Aprobados: {total_aprobados:,} ({total_aprobados/len(votaciones)*100:.1f}%)")
    print(f"  • Rechazados: {total_rechazados:,} ({total_rechazados/len(votaciones)*100:.1f}%)")
    print(f"  • Años con datos: {len(stats_por_anio)}")
    
    # 5. README con info de última actualización
    readme_content = f"""# Datos - Seguimiento Legislativo Chile

**Última actualización:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Resumen de Datos

- **Total de votaciones:** {len(votaciones):,}
- **Periodo:** {stats['periodo']['inicio']} a {stats['periodo']['fin']}
- **Años con datos:** {len(stats_por_anio)}

### Votaciones por Año

| Año | Total | Aprobados | Rechazados |
|-----|-------|-----------|------------|
"""
    
    for anio in sorted(stats_por_anio.keys(), reverse=True):
        s = stats_por_anio[anio]
        readme_content += f"| {anio} | {s['total']:,} | {s['aprobados']:,} | {s['rechazados']:,} |\n"
    
    readme_content += f"""
## Archivos Disponibles

- `votaciones.json`: Últimas 1000 votaciones con todos los detalles
- `estadisticas.json`: Estadísticas agregadas y metadata

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
    
    # Años a consultar: desde 2001 hasta 2025
    annos_a_consultar = list(range(2001, 2026))  # 2001 a 2025
    
    print(f"📅 Consultando años: {annos_a_consultar[0]} - {annos_a_consultar[-1]}")
    print(f"   Total de años: {len(annos_a_consultar)}")
    print("\n⚠️  NOTA: Esto puede tomar varios minutos...")
    print("   El API procesará 25 años de datos.\n")
    
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