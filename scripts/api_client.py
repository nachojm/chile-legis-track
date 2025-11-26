"""
Cliente para interactuar con la API de OpenData Cámara de Diputados de Chile
"""

import requests
import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os


class CamaraAPI:
    """Cliente para la API de la Cámara de Diputados"""
    
    BASE_URL = "https://opendata.camara.cl/camaradiputados/WServices/WSLegislativo.asmx"
    
    def __init__(self, output_dir='data/raw'):
        self.session = requests.Session()
        self.output_dir = output_dir
        
        # Crear directorio si no existe
        os.makedirs(output_dir, exist_ok=True)
    
    def _hacer_peticion(self, endpoint, params):
        """
        Método genérico para hacer peticiones al API
        
        Args:
            endpoint (str): Endpoint del servicio
            params (dict): Parámetros de la petición
            
        Returns:
            str: XML response o None si hay error
        """
        url = f"{self.BASE_URL}/{endpoint}"
        
        try:
            response = self.session.post(url, data=params, timeout=30)
            response.raise_for_status()
            
            # Guardar XML crudo
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"{self.output_dir}/{endpoint}_{timestamp}.xml"
            
            with open(filename, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"✓ Datos guardados en: {filename}")
            return response.text
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error en la petición: {e}")
            return None
    
    def obtener_votaciones_por_anno(self, anno):
        """
        Obtiene votaciones por año
        
        Args:
            anno (int): Año de consulta (ej: 2024)
        
        Returns:
            str: XML con las votaciones
        """
        print(f"Obteniendo votaciones del año {anno}...")
        params = {'prmAnno': str(anno)}
        return self._hacer_peticion('retornarVotacionesXAnno', params)
    
    def parsear_xml_votaciones(self, xml_string):
        """
        Parsea el XML de votaciones a estructura Python
        
        Args:
            xml_string (str): XML a parsear
            
        Returns:
            list: Lista de diccionarios con votaciones
        """
        if not xml_string:
            return []
        
        try:
            # Namespace de la API de la Cámara
            namespace = {'ns': 'http://opendata.camara.cl/camaradiputados/v1'}
            
            root = ET.fromstring(xml_string)
            votaciones = []
            
            # Buscar todas las votaciones con namespace
            for votacion in root.findall('.//ns:Votacion', namespace):
                vot_dict = {}
                
                for child in votacion:
                    # Remover namespace del tag
                    tag = child.tag.replace('{http://opendata.camara.cl/camaradiputados/v1}', '')
                    
                    # Si el elemento tiene atributo 'Valor', usar ese
                    if 'Valor' in child.attrib:
                        vot_dict[tag + '_Valor'] = child.attrib['Valor']
                        vot_dict[tag] = child.text if child.text else child.attrib['Valor']
                    else:
                        # Usar el texto del elemento
                        vot_dict[tag] = child.text
                
                votaciones.append(vot_dict)
            
            print(f"✓ Parseadas {len(votaciones)} votaciones")
            return votaciones
            
        except Exception as e:
            print(f"✗ Error parseando XML: {e}")
            import traceback
            traceback.print_exc()
            
            # Intentar mostrar estructura para debugging
            try:
                root = ET.fromstring(xml_string)
                print(f"Root tag: {root.tag}")
                print(f"Namespace: {root.tag.split('}')[0] + '}' if '}' in root.tag else 'Sin namespace'}")
                print(f"Primeros elementos: {[child.tag for child in root[:3]]}")
            except:
                pass
            return []
    
    def explorar_xml(self, xml_string):
        """
        Explora la estructura del XML para debugging
        
        Args:
            xml_string (str): XML a explorar
        """
        if not xml_string:
            print("No hay datos para explorar")
            return
        
        try:
            root = ET.fromstring(xml_string)
            
            print("\n" + "="*60)
            print("ESTRUCTURA DEL XML")
            print("="*60)
            print(f"Root tag: {root.tag}")
            print(f"Root attribs: {root.attrib}")
            
            # Extraer namespace si existe
            if '}' in root.tag:
                namespace_url = root.tag.split('}')[0][1:]
                print(f"Namespace: {namespace_url}")
            
            # Mostrar primeros elementos
            print(f"\nTotal elementos hijos directos: {len(root)}")
            print("\nPrimera votación (ejemplo completo):")
            
            if len(root) > 0:
                votacion = root[0]
                print(f"\nTag: {votacion.tag}")
                for subchild in votacion:
                    # Limpiar tag del namespace
                    tag_clean = subchild.tag.split('}')[-1]
                    text = subchild.text if subchild.text else ''
                    attribs = dict(subchild.attrib) if subchild.attrib else {}
                    
                    if attribs:
                        print(f"  {tag_clean}: '{text}' | Atributos: {attribs}")
                    else:
                        print(f"  {tag_clean}: {text}")
                    
        except Exception as e:
            print(f"Error explorando XML: {e}")
            import traceback
            traceback.print_exc()
    
    def guardar_json(self, data, filename):
        """
        Guarda datos en formato JSON
        
        Args:
            data: Datos a guardar
            filename (str): Nombre del archivo
        """
        output_path = f"{self.output_dir}/{filename}"
        
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"✓ JSON guardado en: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error guardando JSON: {e}")
            return False


def main():
    """Función principal para testing"""
    
    api = CamaraAPI()
    
    # Obtener votaciones de 2024
    xml_data = api.obtener_votaciones_por_anno(2024)
    
    if xml_data:
        # Explorar estructura
        api.explorar_xml(xml_data)
        
        # Parsear datos
        votaciones = api.parsear_xml_votaciones(xml_data)
        
        if votaciones:
            # Guardar como JSON
            api.guardar_json(votaciones, 'votaciones_2024.json')
            
            # Mostrar resumen
            print(f"\n✓ Total votaciones: {len(votaciones)}")
            print("\nPrimera votación (primeros 5 campos):")
            if votaciones:
                for key, value in list(votaciones[0].items())[:5]:
                    print(f"  {key}: {value}")


if __name__ == "__main__":
    main()