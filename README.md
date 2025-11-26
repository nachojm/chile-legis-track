# 🇨🇱 Seguimiento Legislativo Chile

Plataforma de visualización y análisis de datos del Congreso Nacional de Chile, inspirada en DataChile.

## 🎯 Objetivo

Proveer transparencia sobre la actividad legislativa chilena mediante visualizaciones interactivas y datos abiertos.

## 📊 Características

- **Datos en tiempo real** del API OpenData Cámara de Diputados
- **Visualizaciones interactivas** de actividad parlamentaria
- **Estadísticas** de proyectos de ley y votaciones
- **Datos descargables** en formato JSON

## 🚀 Inicio Rápido

### Requisitos Previos

- Python 3.8+
- Git
- Cuenta en GitHub

### Instalación

1. **Clonar el repositorio**
```bash
git clone https://github.com/tuusuario/seguimiento-legislativo-chile.git
cd seguimiento-legislativo-chile
```

2. **Instalar dependencias Python**
```bash
pip install -r requirements.txt
```

3. **Ejecutar script de actualización de datos**
```bash
python scripts/update_data.py
```

4. **Ver el sitio localmente**
- Abre `docs/index.html` en tu navegador
- O usa un servidor local:
```bash
python -m http.server 8000
# Visita http://localhost:8000/docs/
```

## 📁 Estructura del Proyecto

```
seguimiento-legislativo-chile/
├── data/                    # Datos recolectados
│   ├── raw/                 # Datos crudos del API
│   └── processed/           # Datos procesados
├── scripts/                 # Scripts Python
│   ├── api_client.py       # Cliente API Cámara
│   ├── data_processor.py   # Procesamiento de datos
│   └── update_data.py      # Script principal
├── docs/                    # Sitio web (GitHub Pages)
│   ├── index.html
│   ├── css/
│   ├── js/
│   └── data/               # Datos para visualización
└── requirements.txt
```

## 🔄 Actualizar Datos

Para actualizar los datos del sitio:

```bash
# 1. Ejecutar script de actualización
python scripts/update_data.py

# 2. Hacer commit de los cambios
git add .
git commit -m "Actualizar datos legislativos"
git push origin main
```

El sitio en GitHub Pages se actualizará automáticamente.

## 🌐 Publicar en GitHub Pages

1. **Sube tu repositorio a GitHub**
   - Abre GitHub Desktop
   - Asegúrate de que todos los cambios estén committed
   - Click en "Publish repository"
   - Marca como público (o privado si prefieres)
   - Click en "Publish repository"

2. **Activar GitHub Pages**
   - Ve a tu repositorio en GitHub.com
   - Settings → Pages (menú lateral izquierdo)
   - Source: Branch `main`, folder `/docs`
   - Click en "Save"
   - Espera 1-2 minutos

3. **Tu sitio estará disponible en:**
   ```
   https://TU-USUARIO-GITHUB.github.io/seguimiento-legislativo-chile/
   ```
   
   Reemplaza `TU-USUARIO-GITHUB` con tu nombre de usuario real.

## 📚 Fuentes de Datos

- [OpenData Cámara de Diputados](https://opendata.camara.cl/)
- Biblioteca del Congreso Nacional (próximamente)
- Senado de Chile (próximamente)

## 🛠️ Tecnologías

- **Backend**: Python, Requests, Pandas
- **Frontend**: HTML5, CSS3, JavaScript
- **Visualizaciones**: Chart.js
- **Hosting**: GitHub Pages

## 📈 Roadmap

- [x] Integración con API Cámara de Diputados
- [x] Visualizaciones básicas
- [ ] Datos del Senado
- [ ] Filtros avanzados
- [ ] Perfiles de parlamentarios
- [ ] Comparaciones temporales
- [ ] API pública propia
- [ ] Notificaciones de nuevas leyes

## 🤝 Contribuir

¡Las contribuciones son bienvenidas!

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/NuevaCaracteristica`)
3. Commit tus cambios (`git commit -m 'Agregar nueva característica'`)
4. Push a la rama (`git push origin feature/NuevaCaracteristica`)
5. Abre un Pull Request

## 📝 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para más detalles.

## 👥 Autores

- Tu Nombre - [@tuusuario](https://github.com/tuusuario)

## 🙏 Agradecimientos

- Inspirado por [DataChile](https://datachile.io/)
- Datos provistos por OpenData Cámara de Diputados
- Comunidad de datos abiertos de Chile

---

**Nota**: Este es un proyecto independiente no afiliado oficialmente con el Congreso Nacional de Chile.