"""
Script para probar el parsing de los archivos XML existentes
"""

import os
import sys
import glob
import json
import xml.etree.ElementTree as ET

sys.path.insert(0, os.path.dirname(__file__))
from api_client import CamaraAPI


def listar_archivos_xml(directorio='data/raw'):
    """Lista todos los archivos XML en el directorio"""
    patron = f"{directorio}/*.xml"
    archivos = glob.glob(patron)
    return archivos


def parsear_archivo_xml_directo(filepath):
    """
    Parsea un archivo XML directamente sin usar la clase
    Para verificar la estructura
    """
    print(f"\n{'='*70}")
    print(f"PARSEANDO: {filepath}")
    print('='*70)
    
    with open(filepath, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    try:
        # Namespace correcto
        namespace = {'ns': 'http://opendata.camara.cl/camaradiputados/v1'}
        
        root = ET.fromstring(xml_content)
        
        # Info del root
        print(f"\n📋 Información del documento:")
        print(f"  Root tag: {root.tag}")
        print(f"  Total votaciones: {len(root)}")
        
        votaciones = []
        
        # Parsear cada votación
        for votacion in root.findall('.//ns:Votacion', namespace):
            vot_dict = {}
            
            for child in votacion:
                # Remover namespace del tag
                tag = child.tag.replace('{http://opendata.camara.cl/camaradiputados/v1}', '')
                
                # Manejar elementos con atributos
                if child.attrib:
                    # Guardar el atributo Valor si existe
                    if 'Valor' in child.attrib:
                        vot_dict[f"{tag}_Codigo"] = child.attrib['Valor']
                    
                    # Guardar otros atributos
                    for attr_name, attr_value in child.attrib.items():
                        if attr_name != 'Valor':
                            vot_dict[f"{tag}_{attr_name}"] = attr_value
                
                # Guardar el texto del elemento
                if child.text and child.text.strip():
                    vot_dict[tag] = child.text.strip()
                elif 'Valor' in child.attrib:
                    # Si no hay texto, usar el valor del atributo
                    vot_dict[tag] = child.attrib['Valor']
            
            votaciones.append(vot_dict)
        
        # Mostrar primera votación completa
        if votaciones:
            print(f"\n✅ Parseadas {len(votaciones)} votaciones")
            print(f"\n📊 Primera votación (ejemplo):")
            for key, value in votaciones[0].items():
                print(f"  • {key}: {value}")
            
            return votaciones
        else:
            print("❌ No se encontraron votaciones")
            return []
            
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return []


def probar_con_api_client(filepath):
    """
    Prueba usando la clase CamaraAPI actualizada
    """
    print(f"\n{'='*70}")
    print("PROBANDO CON API CLIENT")
    print('='*70)
    
    api = CamaraAPI()
    
    with open(filepath, 'r', encoding='utf-8') as f:
        xml_content = f.read()
    
    # Explorar estructura
    api.explorar_xml(xml_content)
    
    # Parsear
    votaciones = api.parsear_xml_votaciones(xml_content)
    
    if votaciones:
        print(f"\n✅ Éxito! Parseadas {len(votaciones)} votaciones")
        
        # Guardar resultado
        output_file = 'data/raw/votaciones_parseadas_test.json'
        api.guardar_json(votaciones, 'votaciones_parseadas_test.json')
        
        return votaciones
    else:
        print("❌ No se pudieron parsear las votaciones")
        return []


def main():
    """Función principal"""
    
    print("\n" + "🔍 " * 20)
    print("TEST DE PARSING DE ARCHIVOS XML")
    print("🔍 " * 20)
    
    # Listar archivos XML disponibles
    archivos_xml = listar_archivos_xml()
    
    if not archivos_xml:
        print("\n❌ No se encontraron archivos XML en data/raw/")
        print("Ejecuta primero: python scripts/update_data.py")
        return
    
    print(f"\n📁 Archivos XML encontrados: {len(archivos_xml)}")
    for archivo in archivos_xml:
        print(f"  • {archivo}")
    
    # Usar el primer archivo como ejemplo
    archivo_test = archivos_xml[0]
    
    # Método 1: Parsing directo
    print("\n" + "="*70)
    print("MÉTODO 1: PARSING DIRECTO")
    print("="*70)
    votaciones_directo = parsear_archivo_xml_directo(archivo_test)
    
    # Método 2: Usando API Client
    print("\n" + "="*70)
    print("MÉTODO 2: API CLIENT")
    print("="*70)
    votaciones_api = probar_con_api_client(archivo_test)
    
    # Comparar resultados
    print("\n" + "="*70)
    print("RESUMEN")
    print("="*70)
    print(f"Parsing directo: {len(votaciones_directo)} votaciones")
    print(f"API Client: {len(votaciones_api)} votaciones")
    
    if votaciones_directo:
        print("\n✅ ¡Parsing exitoso!")
        print("\nCampos extraídos:")
        for key in votaciones_directo[0].keys():
            print(f"  • {key}")
        
        # Guardar JSON final
        os.makedirs('docs/data', exist_ok=True)
        
        datos_finales = {
            'metadata': {
                'total_votaciones': len(votaciones_directo),
                'archivo_fuente': archivo_test
            },
            'votaciones': votaciones_directo[:100]  # Primeras 100
        }
        
        with open('docs/data/votaciones.json', 'w', encoding='utf-8') as f:
            json.dump(datos_finales, f, ensure_ascii=False, indent=2)
        
        print("\n💾 Datos guardados en: docs/data/votaciones.json")
        
        # Estadísticas
        with open('docs/data/estadisticas.json', 'w', encoding='utf-8') as f:
            stats = {
                'total_votaciones': len(votaciones_directo),
                'fecha_actualizacion': '2024-12-18',
                'campos_disponibles': list(votaciones_directo[0].keys())
            }
            json.dump(stats, f, ensure_ascii=False, indent=2)
        
        print("💾 Estadísticas guardadas en: docs/data/estadisticas.json")
        print("\n✨ Ahora puedes abrir docs/index.html en tu navegador")
    else:
        print("\n❌ No se pudieron parsear los datos")


if __name__ == "__main__":
    main()