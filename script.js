const API_URL = '/api';
let eventoEmEdicao = null;
const campos = ['titulo', 'descricao', 'data_inicio', 'data_fim', 'local', 'categoria', 'prioridade'];

// Carregar eventos ao iniciar
document.addEventListener('DOMContentLoaded', () => {
    carregarEventos();
    configurarNavegacaoEnter();
});

// Formulário principal
document.getElementById('formEvento').addEventListener('submit', async (e) => {
    e.preventDefault();
    await criarEvento();
});

// Formulário de edição
document.getElementById('formEdicao').addEventListener('submit', async (e) => {
    e.preventDefault();
    await salvarEdicao();
});

// Navegação com Enter entre campos
function configurarNavegacaoEnter() {
    const camposForm = document.querySelectorAll('#formEvento input, #formEvento textarea, #formEvento select');
    camposForm.forEach((campo, index) => {
        campo.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && campo.tagName !== 'TEXTAREA') {
                e.preventDefault();
                if (index < camposForm.length - 1) {
                    camposForm[index + 1].focus();
                }
            }
        });
    });

    const camposEdicao = document.querySelectorAll('#formEdicao input, #formEdicao textarea, #formEdicao select');
    camposEdicao.forEach((campo, index) => {
        campo.addEventListener('keydown', (e) => {
            if (e.key === 'Enter' && campo.tagName !== 'TEXTAREA') {
                e.preventDefault();
                if (index < camposEdicao.length - 1) {
                    camposEdicao[index + 1].focus();
                }
            }
        });
    });
}

async function carregarEventos() {
    try {
        const response = await fetch(`${API_URL}/eventos`);
        const eventos = await response.json();
        exibirEventos(eventos);
    } catch (error) {
        mostrarAlerta('Erro ao carregar eventos', 'erro');
    }
}

async function aplicarFiltros() {
    const categoria = document.getElementById('filtroCategoria').value;
    const prioridade = document.getElementById('filtroPrioridade').value;

    try {
        if (categoria || prioridade) {
            const response = await fetch(`${API_URL}/eventos`);
            let eventos = await response.json();

            if (categoria) {
                eventos = eventos.filter(evento => evento.categoria === categoria);
            }

            if (prioridade) {
                eventos = eventos.filter(evento => evento.prioridade === prioridade);
            }

            exibirEventos(eventos);
            return;
        }

        carregarEventos();
    } catch (error) {
        mostrarAlerta('Erro ao filtrar eventos', 'erro');
    }
}

function exibirEventos(eventos) {
    const lista = document.getElementById('eventosList');
    
    if (eventos.length === 0) {
        lista.innerHTML = '<p style="color: #999; text-align: center; padding: 20px;">Nenhum evento encontrado...</p>';
        return;
    }

    lista.innerHTML = eventos.map(evento => `
        <div class="evento-item">
            <div class="evento-titulo">${evento.titulo}</div>
            <div class="evento-data">
                📅 ${new Date(evento.data_inicio).toLocaleString('pt-BR')}
            </div>
            ${evento.local ? `<div class="evento-data">📍 ${evento.local}</div>` : ''}
            ${evento.descricao ? `<div class="evento-data">📝 ${evento.descricao}</div>` : ''}
            ${evento.categoria ? `<div class="evento-data">📂 ${evento.categoria}</div>` : ''}
            <span class="evento-prioridade prioridade-${evento.prioridade}">
                🔴 ${evento.prioridade.toUpperCase()}
            </span>
            <div class="evento-acoes">
                <button class="btn-pequeno btn-editar" onclick="abrirEdicao(${evento.id})">✏️ Editar</button>
                <button class="btn-pequeno btn-deletar" onclick="deletarEvento(${evento.id})">🗑️ Deletar</button>
            </div>
        </div>
    `).join('');
}

async function criarEvento() {
    const dados = {
        titulo: document.getElementById('titulo').value,
        descricao: document.getElementById('descricao').value,
        data_inicio: document.getElementById('data_inicio').value,
        data_fim: document.getElementById('data_fim').value,
        local: document.getElementById('local').value,
        categoria: document.getElementById('categoria').value,
        prioridade: document.getElementById('prioridade').value
    };

    try {
        const response = await fetch(`${API_URL}/eventos`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        if (response.ok) {
            mostrarAlerta('✓ Evento criado com sucesso!', 'sucesso');
            limparFormulario();
            carregarEventos();
        } else {
            mostrarAlerta('❌ Erro ao criar evento', 'erro');
        }
    } catch (error) {
        mostrarAlerta('❌ Erro na requisição', 'erro');
    }
}

async function abrirEdicao(id) {
    try {
        const response = await fetch(`${API_URL}/eventos/${id}`);
        const evento = await response.json();
        
        eventoEmEdicao = evento.id;
        document.getElementById('edit_titulo').value = evento.titulo;
        document.getElementById('edit_descricao').value = evento.descricao || '';
        document.getElementById('edit_data_inicio').value = evento.data_inicio;
        document.getElementById('edit_data_fim').value = evento.data_fim || '';
        document.getElementById('edit_local').value = evento.local || '';
        document.getElementById('edit_categoria').value = evento.categoria || '';
        document.getElementById('edit_prioridade').value = evento.prioridade;
        
        document.getElementById('modalEdicao').classList.add('show');
        document.getElementById('edit_titulo').focus();
        configurarNavegacaoEnter();
    } catch (error) {
        mostrarAlerta('❌ Erro ao carregar evento', 'erro');
    }
}

async function salvarEdicao() {
    if (!eventoEmEdicao) return;

    const dados = {
        titulo: document.getElementById('edit_titulo').value,
        descricao: document.getElementById('edit_descricao').value,
        data_inicio: document.getElementById('edit_data_inicio').value,
        data_fim: document.getElementById('edit_data_fim').value,
        local: document.getElementById('edit_local').value,
        categoria: document.getElementById('edit_categoria').value,
        prioridade: document.getElementById('edit_prioridade').value
    };

    try {
        const response = await fetch(`${API_URL}/eventos/${eventoEmEdicao}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(dados)
        });

        if (response.ok) {
            mostrarAlerta('✓ Evento atualizado com sucesso!', 'sucesso');
            fecharModal();
            carregarEventos();
        } else {
            mostrarAlerta('❌ Erro ao atualizar evento', 'erro');
        }
    } catch (error) {
        mostrarAlerta('❌ Erro na requisição', 'erro');
    }
}

function fecharModal() {
    document.getElementById('modalEdicao').classList.remove('show');
    eventoEmEdicao = null;
}

async function deletarEvento(id) {
    if (!confirm('Tem certeza que deseja deletar este evento?')) return;

    try {
        const response = await fetch(`${API_URL}/eventos/${id}`, { method: 'DELETE' });
        if (response.ok) {
            mostrarAlerta('✓ Evento deletado com sucesso!', 'sucesso');
            carregarEventos();
        }
    } catch (error) {
        mostrarAlerta('❌ Erro ao deletar evento', 'erro');
    }
}

function limparFormulario() {
    document.getElementById('formEvento').reset();
    document.getElementById('titulo').focus();
}

function mostrarAlerta(mensagem, tipo) {
    const alerta = document.getElementById('alerta');
    alerta.className = `alerta show alerta-${tipo}`;
    alerta.textContent = mensagem;
    setTimeout(() => {
        alerta.classList.remove('show');
    }, 4000);
}

// Fechar modal ao clicar fora
document.getElementById('modalEdicao').addEventListener('click', (e) => {
    if (e.target.id === 'modalEdicao') {
        fecharModal();
    }
});