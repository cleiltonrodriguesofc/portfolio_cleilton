// JavaScript principal para Sistema de Classificação de Grãos

document.addEventListener('DOMContentLoaded', function() {
    // Inicializar tooltips do Bootstrap
    var tooltipTriggerList = [].slice.call(document.querySelectorAll('[data-bs-toggle="tooltip"]'));
    var tooltipList = tooltipTriggerList.map(function (tooltipTriggerEl) {
        return new bootstrap.Tooltip(tooltipTriggerEl);
    });

    // Auto-hide alerts após 5 segundos
    setTimeout(function() {
        var alerts = document.querySelectorAll('.alert:not(.alert-permanent)');
        alerts.forEach(function(alert) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        });
    }, 5000);

    // Confirmação para exclusões
    // var deleteButtons = document.querySelectorAll('.btn-delete');
    // deleteButtons.forEach(function(button) {
    //     button.addEventListener('click', function(e) {
    //         if (!confirm('Tem certeza que deseja excluir este item?')) {
    //             e.preventDefault();
    //         }
    //     });
    // });

    // Formatação de números nos campos de entrada
    var numberInputs = document.querySelectorAll('input[type="number"]');
    numberInputs.forEach(function(input) {
        input.addEventListener('blur', function() {
            if (this.value && !isNaN(this.value)) {
                this.value = parseFloat(this.value).toFixed(2);
            }
        });
    });

    // Validação de formulários
    var forms = document.querySelectorAll('.needs-validation');
    forms.forEach(function(form) {
        form.addEventListener('submit', function(event) {
            if (!form.checkValidity()) {
                event.preventDefault();
                event.stopPropagation();
            }
            form.classList.add('was-validated');
        });
    });

    // Função para atualizar estatísticas em tempo real
    function updateStats() {
        fetch('/api/stats/')
            .then(response => response.json())
            .then(data => {
                if (data.total_amostras !== undefined) {
                    document.getElementById('total-amostras').textContent = data.total_amostras;
                }
                if (data.aceitas !== undefined) {
                    document.getElementById('aceitas').textContent = data.aceitas;
                }
                if (data.rejeitadas !== undefined) {
                    document.getElementById('rejeitadas').textContent = data.rejeitadas;
                }
                if (data.pendentes !== undefined) {
                    document.getElementById('pendentes').textContent = data.pendentes;
                }
            })
            .catch(error => console.log('Erro ao atualizar estatísticas:', error));
    }

    // Atualizar estatísticas a cada 30 segundos se estiver na página do dashboard
    if (document.getElementById('dashboard-page')) {
        setInterval(updateStats, 30000);
    }
});

// Função para ler peso da balança
function lerPesoBalanca() {
    var button = document.getElementById('btn-ler-balanca');
    var pesoInput = document.getElementById('id_peso_bruto');
    var spinner = button.querySelector('.spinner-border');
    var icon = button.querySelector('.fa-scale-balanced');
    
    // Mostrar loading
    button.disabled = true;
    spinner.classList.remove('d-none');
    icon.classList.add('d-none');
    
    fetch('/scale/read/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': document.querySelector('[name=csrfmiddlewaretoken]').value
        },
        body: JSON.stringify({
            port: '/dev/ttyUSB0',
            baudrate: 9600
        })
    })
    .then(response => response.json())
    .then(data => {
        if (data.weight) {
            pesoInput.value = data.weight;
            showAlert('Peso lido da balança: ' + data.weight + ' kg', 'success');
        } else {
            showAlert(data.error || 'Erro ao ler peso da balança', 'danger');
        }
    })
    .catch(error => {
        showAlert('Erro de conexão com a balança', 'danger');
    })
    .finally(() => {
        // Esconder loading
        button.disabled = false;
        spinner.classList.add('d-none');
        icon.classList.remove('d-none');
    });
}

// Função para mostrar alertas
function showAlert(message, type) {
    var alertContainer = document.getElementById('alert-container');
    if (!alertContainer) {
        alertContainer = document.createElement('div');
        alertContainer.id = 'alert-container';
        alertContainer.className = 'position-fixed top-0 end-0 p-3';
        alertContainer.style.zIndex = '1050';
        document.body.appendChild(alertContainer);
    }
    
    var alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    alertContainer.appendChild(alert);
    
    // Auto-remove após 5 segundos
    setTimeout(() => {
        if (alert.parentNode) {
            var bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }
    }, 5000);
}

// Função para filtrar tabela
function filterTable() {
    var searchInput = document.getElementById('search-input');
    var statusFilter = document.getElementById('status-filter');
    var grainFilter = document.getElementById('grain-filter');
    var table = document.getElementById('amostras-table');
    var rows = table.getElementsByTagName('tbody')[0].getElementsByTagName('tr');
    
    var searchTerm = searchInput ? searchInput.value.toLowerCase() : '';
    var statusValue = statusFilter ? statusFilter.value : '';
    var grainValue = grainFilter ? grainFilter.value : '';
    
    for (var i = 0; i < rows.length; i++) {
        var row = rows[i];
        var cells = row.getElementsByTagName('td');
        var showRow = true;
        
        // Filtro de busca
        if (searchTerm) {
            var found = false;
            for (var j = 0; j < cells.length; j++) {
                if (cells[j].textContent.toLowerCase().includes(searchTerm)) {
                    found = true;
                    break;
                }
            }
            if (!found) showRow = false;
        }
        
        // Filtro de status
        if (statusValue && showRow) {
            var statusCell = cells[4]; // Assumindo que status está na 5ª coluna
            if (statusCell && !statusCell.textContent.toLowerCase().includes(statusValue.toLowerCase())) {
                showRow = false;
            }
        }
        
        // Filtro de grão
        if (grainValue && showRow) {
            var grainCell = cells[1]; // Assumindo que tipo de grão está na 2ª coluna
            if (grainCell && !grainCell.textContent.toLowerCase().includes(grainValue.toLowerCase())) {
                showRow = false;
            }
        }
        
        row.style.display = showRow ? '' : 'none';
    }
}

// --- LÓGICA DO TOGGLE DA SIDEBAR ---

    // Pega o botão de toggle único
    const sidebarToggleButton = document.getElementById('sidebarToggle');
    
    // Função para aplicar o toggle
    function toggleSidebar() {
        // Adiciona/Remove a classe do <body>
        document.body.classList.toggle('sidebar-collapsed');

        // Salva o estado no localStorage para persistir
        if (document.body.classList.contains('sidebar-collapsed')) {
            localStorage.setItem('sidebarCollapsed', 'true');
        } else {
            localStorage.removeItem('sidebarCollapsed');
        }
    }

    // Adiciona o evento de clique
    if (sidebarToggleButton) {
        sidebarToggleButton.addEventListener('click', toggleSidebar);
    }

    // Verifica se o estado "recolhido" estava salvo ao carregar a página
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        document.body.classList.add('sidebar-collapsed');
    }
    // --- FIM DA LÓGICA DO TOGGLE ---