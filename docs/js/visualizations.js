/**
 * Visualizaciones con Chart.js
 */

let charts = {
    evolucion: null,
    actividad: null,
    resultados: null,
    tipos: null,
    votos: null
};

/**
 * Inicializa las visualizaciones cuando los datos están listos
 */
function initVisualizaciones() {
    const checkInterval = setInterval(() => {
        if (window.appState && !window.appState.cargando) {
            clearInterval(checkInterval);
            crearTodosLosGraficos();
        }
    }, 100);
}

/**
 * Crea todos los gráficos
 */
function crearTodosLosGraficos() {
    const votaciones = window.appState.votaciones;
    const statsPorAnio = window.appState.statsPorAnio;
    
    if (!votaciones || votaciones.length === 0) {
        console.log('No hay datos para visualizar');
        return;
    }
    
    console.log('📊 Creando visualizaciones con', votaciones.length, 'votaciones');
    console.log('📊 Stats por año:', Object.keys(statsPorAnio).length, 'años');
    
    crearGraficoEvolucion(statsPorAnio);
    crearGraficoActividad(votaciones);
    crearGraficoResultados(votaciones);
    crearGraficoTipos(votaciones);
    crearGraficoVotos(votaciones);
}

/**
 * Gráfico de evolución histórica por año
 */
function crearGraficoEvolucion(statsPorAnio) {
    const canvas = document.getElementById('evolucionChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Verificar que tengamos datos
    if (!statsPorAnio || Object.keys(statsPorAnio).length === 0) {
        console.log('No hay estadísticas por año');
        return;
    }
    
    // Ordenar años y extraer datos
    const anios = Object.keys(statsPorAnio).sort();
    const totales = anios.map(a => statsPorAnio[a].total);
    const aprobados = anios.map(a => statsPorAnio[a].aprobados);
    const rechazados = anios.map(a => statsPorAnio[a].rechazados);
    
    if (charts.evolucion) charts.evolucion.destroy();
    
    charts.evolucion = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: anios,
            datasets: [
                {
                    label: 'Aprobados',
                    data: aprobados,
                    backgroundColor: 'rgba(46, 204, 113, 0.8)',
                    borderColor: '#2ecc71',
                    borderWidth: 1
                },
                {
                    label: 'Rechazados',
                    data: rechazados,
                    backgroundColor: 'rgba(231, 76, 60, 0.8)',
                    borderColor: '#e74c3c',
                    borderWidth: 1
                },
                {
                    label: 'Total',
                    data: totales,
                    type: 'line',
                    borderColor: '#0039a6',
                    backgroundColor: 'rgba(0, 57, 166, 0.1)',
                    borderWidth: 3,
                    fill: false,
                    tension: 0.4,
                    pointRadius: 4,
                    pointHoverRadius: 6
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                title: {
                    display: true,
                    text: `Actividad Legislativa Histórica (${anios[0]}-${anios[anios.length-1]})`,
                    font: { size: 16, weight: 'bold' }
                },
                legend: { 
                    display: true,
                    position: 'top'
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            return `${context.dataset.label}: ${context.parsed.y.toLocaleString('es-CL')}`;
                        }
                    }
                }
            },
            scales: {
                y: { 
                    beginAtZero: true,
                    stacked: false,
                    ticks: {
                        callback: function(value) {
                            return value.toLocaleString('es-CL');
                        }
                    }
                },
                x: {
                    ticks: {
                        maxRotation: 45,
                        minRotation: 45
                    }
                }
            }
        }
    });
    
    console.log('✓ Gráfico de evolución creado con', anios.length, 'años');
}

/**
 * Gráfico de actividad reciente (últimos 12 meses)
 */
function crearGraficoActividad(votaciones) {
    const canvas = document.getElementById('actividadChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Filtrar últimos 12 meses
    const ahora = new Date();
    const hace12Meses = new Date(ahora.getFullYear(), ahora.getMonth() - 12, 1);
    
    const votacionesRecientes = votaciones.filter(v => {
        if (!v.Fecha) return false;
        try {
            const fecha = new Date(v.Fecha);
            return fecha >= hace12Meses;
        } catch (e) {
            return false;
        }
    });
    
    // Agrupar por mes
    const porMes = {};
    votacionesRecientes.forEach(v => {
        if (!v.Fecha) return;
        
        try {
            const fecha = new Date(v.Fecha);
            const mes = `${fecha.getFullYear()}-${String(fecha.getMonth() + 1).padStart(2, '0')}`;
            porMes[mes] = (porMes[mes] || 0) + 1;
        } catch (e) {}
    });
    
    const meses = Object.keys(porMes).sort();
    const valores = meses.map(m => porMes[m]);
    
    if (charts.actividad) charts.actividad.destroy();
    
    charts.actividad = new Chart(ctx, {
        type: 'line',
        data: {
            labels: meses.map(m => {
                const [y, mes] = m.split('-');
                return new Date(y, mes - 1).toLocaleDateString('es-CL', { month: 'short', year: 'numeric' });
            }),
            datasets: [{
                label: 'Votaciones',
                data: valores,
                borderColor: '#0039a6',
                backgroundColor: 'rgba(0, 57, 166, 0.1)',
                borderWidth: 3,
                fill: true,
                tension: 0.4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

/**
 * Gráfico de resultados (Aprobado/Rechazado)
 */
function crearGraficoResultados(votaciones) {
    const canvas = document.getElementById('resultadosChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Contar resultados
    const resultados = {};
    votaciones.forEach(v => {
        const resultado = v.Resultado || 'Sin especificar';
        resultados[resultado] = (resultados[resultado] || 0) + 1;
    });
    
    if (charts.resultados) charts.resultados.destroy();
    
    charts.resultados = new Chart(ctx, {
        type: 'doughnut',
        data: {
            labels: Object.keys(resultados),
            datasets: [{
                data: Object.values(resultados),
                backgroundColor: [
                    '#2ecc71',
                    '#e74c3c',
                    '#95a5a6',
                    '#f39c12'
                ],
                borderWidth: 2,
                borderColor: '#fff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            }
        }
    });
}

/**
 * Gráfico de tipos de proyectos
 */
function crearGraficoTipos(votaciones) {
    const canvas = document.getElementById('tiposChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Contar tipos
    const tipos = {};
    votaciones.forEach(v => {
        const tipo = v.Tipo || 'Sin especificar';
        tipos[tipo] = (tipos[tipo] || 0) + 1;
    });
    
    // Ordenar y tomar top 5
    const tiposOrdenados = Object.entries(tipos)
        .sort((a, b) => b[1] - a[1])
        .slice(0, 5);
    
    if (charts.tipos) charts.tipos.destroy();
    
    charts.tipos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: tiposOrdenados.map(t => t[0]),
            datasets: [{
                label: 'Cantidad',
                data: tiposOrdenados.map(t => t[1]),
                backgroundColor: '#0039a6',
                borderColor: '#002a75',
                borderWidth: 1
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: { beginAtZero: true }
            }
        }
    });
}

/**
 * Gráfico de distribución de votos
 */
function crearGraficoVotos(votaciones) {
    const canvas = document.getElementById('votosChart');
    if (!canvas) return;
    
    const ctx = canvas.getContext('2d');
    
    // Calcular promedios
    let totalSi = 0, totalNo = 0, totalAbstencion = 0;
    let count = 0;
    
    votaciones.forEach(v => {
        if (v.TotalSi) {
            totalSi += parseInt(v.TotalSi) || 0;
            totalNo += parseInt(v.TotalNo) || 0;
            totalAbstencion += parseInt(v.TotalAbstencion) || 0;
            count++;
        }
    });
    
    if (charts.votos) charts.votos.destroy();
    
    charts.votos = new Chart(ctx, {
        type: 'bar',
        data: {
            labels: ['Promedio de Votos'],
            datasets: [
                {
                    label: 'Votos Sí',
                    data: [Math.round(totalSi / count)],
                    backgroundColor: '#2ecc71'
                },
                {
                    label: 'Votos No',
                    data: [Math.round(totalNo / count)],
                    backgroundColor: '#e74c3c'
                },
                {
                    label: 'Abstenciones',
                    data: [Math.round(totalAbstencion / count)],
                    backgroundColor: '#95a5a6'
                }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'bottom'
                }
            },
            scales: {
                y: { beginAtZero: true },
                x: { stacked: false }
            }
        }
    });
}

// Inicializar cuando el script cargue
initVisualizaciones();

// Exportar
window.actualizarGraficos = crearTodosLosGraficos;