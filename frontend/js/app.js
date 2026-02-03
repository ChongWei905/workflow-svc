/**
 * Main application logic
 * Global configuration and utilities
 */

// Global configuration
const API_BASE = '/api';
const WS_BASE = `ws://${window.location.host}/ws/chat`;

// API Key management
let API_KEY = localStorage.getItem('apiKey') || '';

// DOM Elements
const apiKeyInput = document.getElementById('apiKey');
const setApiKeyBtn = document.getElementById('setApiKey');
const apiKeyStatus = document.getElementById('apiKeyStatus');

// Initialize API Key from localStorage
if (API_KEY) {
    apiKeyInput.value = API_KEY;
    apiKeyStatus.textContent = '✓ 已设置';
    apiKeyStatus.classList.add('set');
}

// Set API Key handler
setApiKeyBtn.addEventListener('click', () => {
    const key = apiKeyInput.value.trim();
    if (key) {
        API_KEY = key;
        localStorage.setItem('apiKey', key);
        apiKeyStatus.textContent = '✓ 已设置';
        apiKeyStatus.classList.add('set');
        showNotification('API Key 已保存', 'success');
    } else {
        API_KEY = '';
        localStorage.removeItem('apiKey');
        apiKeyStatus.textContent = '';
        apiKeyStatus.classList.remove('set');
        showNotification('API Key 已清除', 'info');
    }
});

/**
 * Make API request with authentication
 * @param {string} url - API endpoint path
 * @param {object} options - Fetch options
 * @returns {Promise<object>} Response data
 */
async function api(url, options = {}) {
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };

    // Add API Key if set
    if (API_KEY) {
        headers['X-API-Key'] = API_KEY;
    }

    const response = await fetch(API_BASE + url, {
        ...options,
        headers
    });

    // Handle 401 Unauthorized
    if (response.status === 401) {
        throw new Error('需要 API Key，请在页面顶部设置');
    }

    // Handle 403 Forbidden
    if (response.status === 403) {
        throw new Error('API Key 无效');
    }

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
        throw new Error(error.detail || `API Error: ${response.status}`);
    }

    return response.json();
}

/**
 * Show notification message
 * @param {string} message - Message to display
 * @param {string} type - Notification type (success, error, info)
 */
function showNotification(message, type = 'info') {
    // Create notification element
    const notification = document.createElement('div');
    notification.className = `notification notification-${type}`;
    notification.textContent = message;
    notification.style.cssText = `
        position: fixed;
        top: 20px;
        right: 20px;
        padding: 12px 20px;
        background: ${type === 'success' ? '#28a745' : type === 'error' ? '#dc3545' : '#007bff'};
        color: white;
        border-radius: 8px;
        box-shadow: 0 4px 6px rgba(0,0,0,0.1);
        z-index: 10000;
        animation: slideIn 0.3s ease-out;
    `;

    document.body.appendChild(notification);

    // Remove after 3 seconds
    setTimeout(() => {
        notification.style.animation = 'slideOut 0.3s ease-in';
        setTimeout(() => {
            document.body.removeChild(notification);
        }, 300);
    }, 3000);
}

// Add animations
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from {
            transform: translateX(100%);
            opacity: 0;
        }
        to {
            transform: translateX(0);
            opacity: 1;
        }
    }

    @keyframes slideOut {
        from {
            transform: translateX(0);
            opacity: 1;
        }
        to {
            transform: translateX(100%);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);

/**
 * Format timestamp
 * @param {string} isoString - ISO format timestamp
 * @returns {string} Formatted timestamp
 */
function formatTimestamp(isoString) {
    const date = new Date(isoString);
    return date.toLocaleString('zh-CN', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit'
    });
}

/**
 * Format execution time
 * @param {number} seconds - Execution time in seconds
 * @returns {string} Formatted time
 */
function formatExecutionTime(seconds) {
    if (seconds === null || seconds === undefined) {
        return 'N/A';
    }
    if (seconds < 1) {
        return `${(seconds * 1000).toFixed(0)}ms`;
    }
    return `${seconds.toFixed(2)}s`;
}

/**
 * Escape HTML to prevent XSS
 * @param {string} text - Text to escape
 * @returns {string} Escaped text
 */
function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// Tab switching
document.querySelectorAll('.tab').forEach(tab => {
    tab.addEventListener('click', () => {
        // Remove active class from all tabs
        document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
        document.querySelectorAll('.tab-content').forEach(c => c.classList.remove('active'));

        // Add active class to current tab
        tab.classList.add('active');
        const tabName = tab.dataset.tab;
        document.getElementById(`${tabName}-tab`).classList.add('active');

        // Load corresponding data
        if (tabName === 'skills') {
            loadSkills();
        } else if (tabName === 'logs') {
            loadLogs();
        }
    });
});

// Log when app is ready
console.log('Skill Executor App initialized');
