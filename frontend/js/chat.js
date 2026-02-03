/**
 * Chat module
 * Handles WebSocket connection and chat functionality
 */

// DOM Elements
const chatMessages = document.getElementById('chat-messages');
const chatInput = document.getElementById('chat-input');
const sendBtn = document.getElementById('send-btn');
const wsStatus = document.getElementById('ws-status');

// WebSocket connection
let ws = null;
let reconnectTimeout = null;
let isConnecting = false;

/**
 * Connect to WebSocket server
 */
function connectWebSocket() {
    if (isConnecting || (ws && ws.readyState === WebSocket.OPEN)) {
        return;
    }

    isConnecting = true;

    try {
        ws = new WebSocket(WS_BASE);

        ws.onopen = () => {
            console.log('WebSocket connected');
            isConnecting = false;
            updateWsStatus('connected');
        };

        ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                handleWebSocketMessage(data);
            } catch (e) {
                console.error('Failed to parse WebSocket message:', e);
            }
        };

        ws.onclose = () => {
            console.log('WebSocket disconnected');
            isConnecting = false;
            updateWsStatus('disconnected');

            // Auto-reconnect after 5 seconds
            if (!reconnectTimeout) {
                reconnectTimeout = setTimeout(() => {
                    reconnectTimeout = null;
                    connectWebSocket();
                }, 5000);
            }
        };

        ws.onerror = (error) => {
            console.error('WebSocket error:', error);
            isConnecting = false;
        };

    } catch (error) {
        console.error('Failed to create WebSocket connection:', error);
        isConnecting = false;
        updateWsStatus('disconnected');
    }
}

/**
 * Update WebSocket status indicator
 * @param {string} status - Connection status
 */
function updateWsStatus(status) {
    if (status === 'connected') {
        wsStatus.textContent = '● WebSocket 已连接';
        wsStatus.className = 'status-indicator connected';
    } else {
        wsStatus.textContent = '● WebSocket 未连接';
        wsStatus.className = 'status-indicator disconnected';
    }
}

/**
 * Handle WebSocket message
 * @param {object} data - Message data
 */
function handleWebSocketMessage(data) {
    if (data.type === 'chunk') {
        // Append message chunk
        appendMessage('assistant', data.content, false);
    } else if (data.type === 'done') {
        // Complete message
        enableSendButton();
    } else if (data.type === 'error') {
        // Error message
        appendMessage('error', data.content);
        enableSendButton();
    } else if (data.type === 'pong') {
        // Heartbeat response
        console.log('WebSocket pong received');
    }
}

/**
 * Send message through WebSocket or fallback to HTTP
 */
async function sendMessage() {
    const query = chatInput.value.trim();
    if (!query) return;

    // Disable send button
    disableSendButton();

    // Add user message
    appendMessage('user', query);
    chatInput.value = '';

    // Try WebSocket first
    if (ws && ws.readyState === WebSocket.OPEN) {
        try {
            ws.send(JSON.stringify({
                type: 'execute',
                query: query
            }));
            return;
        } catch (error) {
            console.error('WebSocket send failed:', error);
        }
    }

    // Fallback to HTTP API
    try {
        showNotification('使用 HTTP API (WebSocket 未连接)', 'info');
        const result = await api('/execute', {
            method: 'POST',
            body: JSON.stringify({ query })
        });
        appendMessage('assistant', result.response);
    } catch (error) {
        appendMessage('error', 'Error: ' + error.message);
    } finally {
        enableSendButton();
    }
}

/**
 * Append message to chat
 * @param {string} role - Message role (user, assistant, system, error)
 * @param {string} content - Message content
 * @param {boolean} scroll - Whether to scroll to bottom
 */
function appendMessage(role, content, scroll = true) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${role}`;

    // Escape HTML for security
    const safeContent = escapeHtml(content);

    // Handle line breaks
    messageDiv.innerHTML = safeContent.replace(/\n/g, '<br>');

    chatMessages.appendChild(messageDiv);

    if (scroll) {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
}

/**
 * Disable send button
 */
function disableSendButton() {
    sendBtn.disabled = true;
    sendBtn.querySelector('.btn-text').style.display = 'none';
    sendBtn.querySelector('.btn-loading').style.display = 'inline';
}

/**
 * Enable send button
 */
function enableSendButton() {
    sendBtn.disabled = false;
    sendBtn.querySelector('.btn-text').style.display = 'inline';
    sendBtn.querySelector('.btn-loading').style.display = 'none';
}

// Event listeners
sendBtn.addEventListener('click', sendMessage);

chatInput.addEventListener('keydown', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});

// Initialize WebSocket connection
connectWebSocket();

// Send periodic ping to keep connection alive
setInterval(() => {
    if (ws && ws.readyState === WebSocket.OPEN) {
        ws.send(JSON.stringify({ type: 'ping' }));
    }
}, 30000);

console.log('Chat module initialized');
