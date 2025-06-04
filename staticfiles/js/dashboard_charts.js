// Configuración común para los gráficos
Chart.defaults.color = "#858796";
Chart.defaults.font.family = "'Nunito', '-apple-system,system-ui,BlinkMacSystemFont,\"Segoe UI\",Roboto,\"Helvetica Neue\",Arial,sans-serif'";

// Gráfico de Pacientes por Género
function inicializarGraficoGenero(generos_labels, generos_data) {
    var generoCtx = document.getElementById('generoChart');
    if (generoCtx) {
        new Chart(generoCtx.getContext('2d'), {
            type: 'doughnut',
            data: {
                labels: generos_labels,
                datasets: [{
                    data: generos_data,
                    backgroundColor: ['#4e73df', '#1cc88a', '#36b9cc'],
                    hoverBackgroundColor: ['#2e59d9', '#17a673', '#2c9faf'],
                    hoverBorderColor: "rgba(234, 236, 244, 1)"
                }]
            },
            options: {
                maintainAspectRatio: false,
                plugins: {
                    legend: {
                        position: 'bottom'
                    }
                },
                cutout: '80%'
            }
        });
    }
}

// Gráfico de Evoluciones
function inicializarGraficoEvoluciones(evoluciones_labels, evoluciones_data) {
    var evolucionesCtx = document.getElementById('evolucionesChart');
    if (evolucionesCtx) {
        new Chart(evolucionesCtx.getContext('2d'), {
            type: 'bar',
            data: {
                labels: evoluciones_labels,
                datasets: [{
                    label: 'evoluciones',
                    data: evoluciones_data,
                    backgroundColor: '#4e73df',
                    hoverBackgroundColor: '#2e59d9',
                    borderColor: '#4e73df',
                    borderWidth: 1
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            stepSize: 1
                        }
                    }
                }
            }
        });
    }
}

// Gráfico de Signos Vitales
function inicializarGraficoSignosVitales(signos_vitales_labels, signos_vitales_data) {
    var signosVitalesCtx = document.getElementById('signosVitalesChart');
    if (signosVitalesCtx) {
        new Chart(signosVitalesCtx.getContext('2d'), {
            type: 'line',
            data: {
                labels: signos_vitales_labels,
                datasets: [{
                    label: 'Registros',
                    data: signos_vitales_data,
                    lineTension: 0.3,
                    backgroundColor: "rgba(78, 115, 223, 0.05)",
                    borderColor: "rgba(78, 115, 223, 1)",
                    pointRadius: 3,
                    pointBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointBorderColor: "rgba(78, 115, 223, 1)",
                    pointHoverRadius: 3,
                    pointHoverBackgroundColor: "rgba(78, 115, 223, 1)",
                    pointHoverBorderColor: "rgba(78, 115, 223, 1)",
                    pointHitRadius: 10,
                    pointBorderWidth: 2,
                    fill: true
                }]
            },
            options: {
                maintainAspectRatio: false,
                scales: {
                    y: {
                        beginAtZero: true
                    }
                },
                plugins: {
                    legend: {
                        display: false
                    }
                }
            }
        });
    }
}

// Gráfico de Pacientes por Día (para admin dashboard)
function inicializarGraficoPacientesDia(labels, data) {
    var ctx = document.getElementById('pacientesChart');
    if (ctx) {
        new Chart(ctx.getContext('2d'), {
            type: 'line',
            data: {
                labels: labels,
                datasets: [{
                    label: 'Pacientes nuevos',
                    data: data,
                    backgroundColor: 'rgba(54, 162, 235, 0.2)',
                    borderColor: 'rgba(54, 162, 235, 1)',
                    borderWidth: 2,
                    tension: 0.1
                }]
            },
            options: {
                scales: {
                    y: {
                        beginAtZero: true,
                        ticks: {
                            precision: 0
                        }
                    }
                },
                plugins: {
                    legend: {
                        display: true,
                        position: 'top'
                    }
                }
            }
        });
    }
} 