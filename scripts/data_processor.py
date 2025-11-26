"""
Procesamiento y análisis de datos legislativos
"""

import json
import pandas as pd
from datetime import datetime
from collections import Counter
import os


class DataProcessor:
    """Procesa datos legislativos para análisis y visualización"""
    
    def __init__(self, input_dir='data/raw', output_dir='data/processed'):
        self.input_dir = input_dir
        self.output_dir = output_dir
        os.makedirs(output_dir, exist_ok=True)
    
    def cargar_votaciones(self, filename):
        """
        Carga votaciones desde JSON
        
        Args:
            filename (str): Nombre del archivo JSON
            
        Returns:
            pd.DataFrame: DataFrame con votaciones
        """
        filepath = f"{self.input_dir}/{filename}"
        
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            df = pd.DataFrame(data)
            print(f"✓ Cargadas {len(df)} votaciones desde {filename}")
            return df
            
        except Exception as e:
            print(f"✗ Error cargando {filename}: {e}")
            return pd.DataFrame()
    
    def analizar_parlamentario(self, df, campo_parlamentario='Diputado'):
        """
        Analiza actividad por parlamentario
        
        Args:
            df (pd.DataFrame): DataFrame con votaciones
            campo_parlamentario (str): Nombre del campo con info del parlamentario
            
        Returns:
            pd.DataFrame: Estadísticas por parlamentario
        """
        if campo_parlamentario not in df.columns:
            print(f"✗ Campo '{campo_parlamentario}' no encontrado")
            print(f"Campos disponibles: {df.columns.tolist()}")
            return pd.DataFrame()
        
        # Agrupar por parlamentario
        stats = df.groupby(campo_parlamentario).agg({
            campo_parlamentario: 'count'  # Total votaciones
        }).rename(columns={campo_parlamentario: 'total_votaciones'})
        
        # Añadir más métricas si hay info de voto
        if 'Voto' in df.columns or 'TipoVoto' in df.columns:
            campo_voto = 'Voto' if 'Voto' in df.columns else 'TipoVoto'
            
            # Contar tipos de voto
            votos_pivot = pd.crosstab(df[campo_parlamentario], df[campo_voto])
            stats = stats.join(votos_pivot)
        
        return stats.reset_index()
    
    def generar_estadisticas_generales(self, df):
        """
        Genera estadísticas generales del dataset
        
        Args:
            df (pd.DataFrame): DataFrame con votaciones
            
        Returns:
            dict: Estadísticas generales
        """
        stats = {
            'total_votaciones': len(df),
            'columnas': df.columns.tolist(),
            'periodo': {
                'inicio': None,
                'fin': None
            },
            'resumen_campos': {}
        }
        
        # Intentar encontrar campo de fecha
        campos_fecha = [col for col in df.columns if 'fecha' in col.lower() or 'date' in col.lower()]
        if campos_fecha:
            campo_fecha = campos_fecha[0]
            try:
                df[campo_fecha] = pd.to_datetime(df[campo_fecha])
                stats['periodo']['inicio'] = df[campo_fecha].min().strftime('%Y-%m-%d')
                stats['periodo']['fin'] = df[campo_fecha].max().strftime('%Y-%m-%d')
            except:
                pass
        
        # Resumen de cada campo
        for col in df.columns:
            stats['resumen_campos'][col] = {
                'valores_unicos': df[col].nunique(),
                'valores_nulos': df[col].isna().sum(),
                'tipo': str(df[col].dtype)
            }
        
        return stats
    
    def preparar_para_visualizacion(self, df, filename='votaciones_viz.json'):
        """
        Prepara datos en formato óptimo para visualización web
        
        Args:
            df (pd.DataFrame): DataFrame con datos
            filename (str): Nombre del archivo de salida
            
        Returns:
            dict: Datos preparados para visualización
        """
        # Generar diferentes vistas de datos
        data_viz = {
            'metadata': {
                'fecha_generacion': datetime.now().isoformat(),
                'total_registros': len(df),
                'columnas': df.columns.tolist()
            },
            'datos': []
        }
        
        # Convertir DataFrame a lista de diccionarios
        # Limitar a primeros 1000 registros para no sobrecargar el frontend
        data_viz['datos'] = df.head(1000).to_dict('records')
        
        # Guardar
        output_path = f"{self.output_dir}/{filename}"
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(data_viz, f, ensure_ascii=False, indent=2)
            print(f"✓ Datos de visualización guardados en: {output_path}")
            return data_viz
        except Exception as e:
            print(f"✗ Error guardando datos de visualización: {e}")
            return None
    
    def generar_resumen_anual(self, df, campo_fecha='Fecha'):
        """
        Genera resumen de actividad por año
        
        Args:
            df (pd.DataFrame): DataFrame con votaciones
            campo_fecha (str): Campo con fecha
            
        Returns:
            pd.DataFrame: Resumen por año
        """
        if campo_fecha not in df.columns:
            print(f"✗ Campo '{campo_fecha}' no encontrado")
            return pd.DataFrame()
        
        try:
            # Convertir a datetime
            df[campo_fecha] = pd.to_datetime(df[campo_fecha])
            
            # Extraer año
            df['anno'] = df[campo_fecha].dt.year
            
            # Agrupar por año
            resumen = df.groupby('anno').size().reset_index(name='total_votaciones')
            
            return resumen
            
        except Exception as e:
            print(f"✗ Error generando resumen anual: {e}")
            return pd.DataFrame()
    
    def guardar_csv(self, df, filename):
        """
        Guarda DataFrame como CSV
        
        Args:
            df (pd.DataFrame): DataFrame a guardar
            filename (str): Nombre del archivo
        """
        output_path = f"{self.output_dir}/{filename}"
        try:
            df.to_csv(output_path, index=False, encoding='utf-8')
            print(f"✓ CSV guardado en: {output_path}")
            return True
        except Exception as e:
            print(f"✗ Error guardando CSV: {e}")
            return False


def main():
    """Función principal para testing"""
    
    processor = DataProcessor()
    
    # Cargar datos
    df = processor.cargar_votaciones('votaciones_2024.json')
    
    if not df.empty:
        print("\n" + "="*60)
        print("ANÁLISIS DE DATOS")
        print("="*60)
        
        # Estadísticas generales
        stats = processor.generar_estadisticas_generales(df)
        print(f"\nTotal votaciones: {stats['total_votaciones']}")
        print(f"Columnas: {', '.join(stats['columnas'])}")
        
        # Mostrar info de columnas
        print("\nInfo de columnas:")
        for col, info in stats['resumen_campos'].items():
            print(f"  {col}:")
            print(f"    - Valores únicos: {info['valores_unicos']}")
            print(f"    - Nulos: {info['valores_nulos']}")
        
        # Preparar datos para visualización
        processor.preparar_para_visualizacion(df)


if __name__ == "__main__":
    main()