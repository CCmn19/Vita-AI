// --- LÓGICA INICIAL (SIN CAMBIOS) ---
function Inicio() {
    document.getElementById('inicio').classList.remove('hidden');
    document.getElementById('bienvenida').classList.add('hidden');
}

document.addEventListener('DOMContentLoaded', () => {
    const startButton = document.getElementById('startBtn');
    if (startButton) {
        startButton.addEventListener('click', Inicio);
    }

    // --- NUEVA LÓGICA PARA LA PANTALLA DE CHAT ---
    const chatForm = document.getElementById('chat-form');
    // Si el formulario de chat no existe en la página actual, no hagas nada.
    if (!chatForm) {
        return;
    }

    const chatWindow = document.getElementById('chat-window');
    const messageInput = document.getElementById('mensaje');

    // Función para añadir una burbuja de mensaje al chat
    const addMessage = (sender, message) => {
        const messageElement = document.createElement('div');
        messageElement.classList.add('chat-message', `${sender}-message`);
        
        // Usamos innerHTML para que el |safe de Flask funcione al cargar historial
        const p = document.createElement('p');
        p.innerHTML = message;
        messageElement.appendChild(p);
        
        chatWindow.appendChild(messageElement);
        // Mover el scroll hasta el final para ver el último mensaje
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };
    
    // Función para mostrar un indicador de "escribiendo..."
    const showLoading = () => {
        const loadingElement = document.createElement('div');
        loadingElement.classList.add('chat-message', 'ai-message', 'loading-indicator');
        loadingElement.innerHTML = `<p>Vita.IA está pensando...</p>`;
        loadingElement.id = 'loading'; // Le damos un id para poder quitarlo
        chatWindow.appendChild(loadingElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    };
    
    // Función para quitar el indicador
    const hideLoading = () => {
        const loadingElement = document.getElementById('loading');
        if (loadingElement) {
            loadingElement.remove();
        }
    };

    // Al cargar la página, mover el scroll al final del historial
    if(chatWindow){
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Manejar el envío del formulario
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault(); // Evita la recarga de la página

        const userMessage = messageInput.value.trim();
        if (userMessage === '') {
            return; // No envíes mensajes vacíos
        }

        // 1. Añade el mensaje del usuario a la ventana
        addMessage('user', userMessage);
        messageInput.value = ''; // Limpia el campo de texto
        messageInput.style.height = 'auto'; // Resetea la altura

        // 2. Muestra el indicador de carga
        showLoading();

        try {
            // 3. Envía el mensaje al backend
            const response = await fetch('/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ mensaje: userMessage }),
            });

            const data = await response.json();
            
            // 4. Quita el indicador de carga
            hideLoading();
            
            // 5. Añade la respuesta de la IA a la ventana
            if (data.respuesta) {
                addMessage('ai', data.respuesta);
            } else {
                addMessage('ai', 'Hubo un error al procesar tu solicitud.');
            }

        } catch (error) {
            hideLoading();
            addMessage('ai', 'Error de conexión. Inténtalo de nuevo.');
            console.error('Error:', error);
        }
    });
    
    // Hacer que el textarea crezca automáticamente
    messageInput.addEventListener('input', () => {
        messageInput.style.height = 'auto';
        messageInput.style.height = `${messageInput.scrollHeight}px`;
    });
});