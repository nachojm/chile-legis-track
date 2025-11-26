/**
 * Script principal para cargar y mostrar datos
 */

// Estado global de la aplicación
const appState = {
    votaciones: [],
    estadisticas: {},
    cargando: true
};

/**
 * Inicializa la aplicación
 */
async function init() {
    console.log('🚀 Inicializando aplicación...');
    
    try {
        // Cargar datos
        await cargarDatos();
        
        // Renderizar componentes
        renderizarEstadisticas();
        renderizarTabla();
        
        console.log('✅ Aplicación inicializada correctamente');
    } catch (error) {
        console.error('❌ Error inicializando aplicación:', error);
        mostrarError('Error cargando datos. Por favor, intenta más tarde.');
    }
}

/**
 * Carga datos desde archivos JSON
 */
async function cargarDatos() {
    try {
        // Cargar estadísticas
        const respuestaStats = await fetch('data/estadisticas.json');
        if (respuestaStats.ok) {
            appState.estadisticas = await respuestaStats.json();
            console.log('📊 Estadísticas cargadas:', appState.estadisticas);
        }
        
        // Cargar votaciones
        const respuestaVotaciones = await fetch('data/votaciones.json');
        if (respuestaVotaciones.ok) {
            const data = await respuestaVotaciones.json();
            appState.votaciones = data.votaciones || [];
            console.log('📋 Votaciones cargadas:', appState.votaciones.length);
        }
        
        appState.cargando = false;
        
    } catch (error) {
        console.error('Error cargando datos:', error);
        appState.cargando = false;
        throw error;
    }
}

/**
 * Renderiza las estadísticas generales
 */
function renderizarEstadisticas() {
    const stats = appState.estadisticas;
    const votaciones = appState.votaciones;
    
    // Total votaciones
    const totalElement = document.getElementById('total-votaciones');
    if (totalElement) {
        totalElement.textContent = formatearNumero(votaciones.length || 0);
    }
    
    // Última actualización
    const fechaElement = document.getElementById('ultima-actualizacion');
    if (fechaElement && stats.fecha_actualizacion) {
        fechaElement.textContent = formatearFecha(stats.fecha_actualizacion);
    }
    
    // Total aprobados
    const aprobadosElement = document.getElementById('total-aprobados');
    if (aprobadosElement && votaciones.length > 0) {
        const aprobados = votaciones.filter(v => 
            v.Resultado && v.Resultado.toLowerCase().includes('aprobado')
        ).length;
        aprobadosElement.textContent = formatearNumero(aprobados);
    }
    
    // Promedio votos Sí
    const promedioElement = document.getElementById('promedio-si');
    if (promedioElement && votaciones.length > 0) {
        const suma = votaciones.reduce((acc, v) => acc + (parseInt(v.TotalSi) || 0), 0);
        const promedio = Math.round(suma / votaciones.length);
        promedioElement.textContent = formatearNumero(promedio);
    }
}

/**
 * Renderiza la tabla de datos
 */
function renderizarTabla() {
    const votaciones = appState.votaciones;
    
    if (!votaciones || votaciones.length === 0) {
        console.log('No hay votaciones para mostrar');
        return;
    }
    
    // Campos importantes a mostrar
    const camposImportantes = ['Fecha', 'Descripcion', 'Resultado', 'Tipo', 'TotalSi', 'TotalNo'];
    
    // Renderizar headers
    const headersRow = document.getElementById('table-headers');
    if (headersRow) {
        headersRow.innerHTML = camposImportantes
            .map(campo => `<th>${formatearCampo(campo)}</th>`)
            .join('');
    }
    
    // Renderizar datos (primeros 50 registros)
    const tbody = document.getElementById('table-body');
    if (tbody) {
        tbody.innerHTML = votaciones
            .slice(0, 50)
            .map(votacion => {
                const celdas = camposImportantes
                    .map(campo => {
                        let valor = votacion[campo] || '-';
                        
                        // Formatear fecha
                        if (campo === 'Fecha' && valor !== '-') {
                            try {
                                const fecha = new Date(valor);
                                valor = fecha.toLocaleDateString('es-CL');
                            } catch (e) {}
                        }
                        
                        // Agregar badge para resultado
                        if (campo === 'Resultado') {
                            const clase = valor.toLowerCase().includes('aprobado') ? 'badge-success' : 'badge-danger';
                            return `<td><span class="badge ${clase}">${valor}</span></td>`;
                        }
                        
                        return `<td>${truncarTexto(valor, 60)}</td>`;
                    })
                    .join('');
                
                return `<tr>${celdas}</tr>`;
            })
            .join('');
    }
}

/**
 * Muestra un mensaje de error
 */
function mostrarError(mensaje) {
    const main = document.querySelector('main');
    if (main) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'error-message';
        errorDiv.textContent = mensaje;
        main.insertBefore(errorDiv, main.firstChild);
    }
}

// Utilidades de formato

/**
 * Formatea un número con separadores de miles
 */
function formatearNumero(numero) {
    return new Intl.NumberFormat('es-CL').format(numero);
}

/**
 * Formatea una fecha
 */
function formatearFecha(fechaString) {
    try {
        const fecha = new Date(fechaString);
        return new Intl.DateTimeFormat('es-CL', {
            year: 'numeric',
            month: 'short',
            day: 'numeric'
        }).format(fecha);
    } catch (error) {
        return fechaString;
    }
}

/**
 * Formatea el nombre de un campo (camelCase a Título)
 */
function formatearCampo(campo) {
    return campo
        .replace(/([A-Z])/g, ' $1')
        .replace(/^./, str => str.toUpperCase())
        .trim();
}

/**
 * Trunca texto a longitud máxima
 */
function truncarTexto(texto, maxLength) {
    const str = String(texto);
    if (str.length <= maxLength) return str;
    return str.substring(0, maxLength) + '...';
}

// Iniciar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// Exportar para uso en otros scripts
window.appState = appState;