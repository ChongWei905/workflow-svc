/**
 * Logs/audit module
 * Handles display and refresh of audit logs
 */

// DOM Elements
const logsList = document.getElementById('logs-list');
const refreshLogsBtn = document.getElementById('refresh-logs');
const logsLimitSelect = document.getElementById('logs-limit');

let currentLogs = [];
let autoRefreshInterval = null;

/**
 * Load logs from API
 * @param {number} limit - Number of logs to fetch
 */
async function loadLogs(limit = null) {
    try {
        if (!limit) {
            limit = parseInt(logsLimitSelect.value, 10);
        }

        logsList.innerHTML = '<div class="loading">加载中...</div>';

        const logs = await api(`/audit/logs?limit=${limit}`);
        currentLogs = logs;

        displayLogs(logs);
    } catch (error) {
        console.error('Failed to load logs:', error);
        logsList.innerHTML = `
            <div class="error-state">
                <p>加载失败: ${error.message}</p>
            </div>
        `;
        showNotification('加载日志失败', 'error');
    }
}

/**
 * Display logs
 * @param {Array} logs - Logs data
 */
function displayLogs(logs) {
    if (!logs || logs.length === 0) {
        logsList.innerHTML = `
            <div class="empty-state">
                <div class="empty-icon">📋</div>
                <p>暂无审计日志</p>
            </div>
        `;
        return;
    }

    logsList.innerHTML = '';

    // Display in reverse order (newest first)
    [...logs].reverse().forEach(log => {
        const entry = document.createElement('div');

        // Determine log entry class based on event type
        let entryClass = 'log-entry';
        if (log.event_type === 'access_denied') {
            entryClass += ' error';
        }

        entry.className = entryClass;

        // Build log details HTML
        let detailsHtml = '';

        if (log.details) {
            const details = log.details;
            if (details.resource_type) {
                detailsHtml += `<div><strong>资源类型:</strong> ${escapeHtml(details.resource_type)}</div>`;
            }
            if (details.resource_name) {
                detailsHtml += `<div><strong>资源名称:</strong> ${escapeHtml(details.resource_name)}</div>`;
            }
            if (details.reason) {
                detailsHtml += `<div><strong>原因:</strong> ${escapeHtml(details.reason)}</div>`;
            }
            if (details.script_count) {
                detailsHtml += `<div><strong>脚本数量:</strong> ${details.script_count}</div>`;
            }
        }

        entry.innerHTML = `
            <div class="log-time">${formatTimestamp(log.timestamp)}</div>
            <div class="log-type">${formatEventType(log.event_type)}</div>
            ${log.skill_name ? `<div><strong>Skill:</strong> ${escapeHtml(log.skill_name)}</div>` : ''}
            ${log.script_name ? `<div><strong>脚本:</strong> ${escapeHtml(log.script_name)}</div>` : ''}
            ${log.file_path ? `<div><strong>路径:</strong> <code>${escapeHtml(log.file_path)}</code></div>` : ''}
            ${log.exit_code !== undefined && log.exit_code !== null ? `<div><strong>退出码:</strong> ${log.exit_code}</div>` : ''}
            ${log.execution_time ? `<div><strong>执行时间:</strong> ${formatExecutionTime(log.execution_time)}</div>` : ''}
            ${log.output_size ? `<div><strong>输出大小:</strong> ${formatBytes(log.output_size)}</div>` : ''}
            ${detailsHtml ? `<div class="log-details">${detailsHtml}</div>` : ''}
        `;

        logsList.appendChild(entry);
    });
}

/**
 * Format event type for display
 * @param {string} eventType - Event type
 * @returns {string} Formatted event type
 */
function formatEventType(eventType) {
    const eventTypes = {
        'script_executed': '✅ 脚本已执行',
        'access_denied': '🚫 访问被拒绝',
        'file_read': '📄 文件已读取',
        'skill_loaded': '📦 Skill 已加载'
    };
    return eventTypes[eventType] || eventType;
}

/**
 * Format bytes for display
 * @param {number} bytes - Number of bytes
 * @returns {string} Formatted bytes
 */
function formatBytes(bytes) {
    if (bytes === 0) return '0 B';
    const k = 1024;
    const sizes = ['B', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round((bytes / Math.pow(k, i)) * 100) / 100 + ' ' + sizes[i];
}

/**
 * Toggle auto-refresh
 * @param {boolean} enabled - Whether auto-refresh is enabled
 */
function toggleAutoRefresh(enabled) {
    if (autoRefreshInterval) {
        clearInterval(autoRefreshInterval);
        autoRefreshInterval = null;
    }

    if (enabled) {
        autoRefreshInterval = setInterval(() => {
            loadLogs();
        }, 10000); // Refresh every 10 seconds
    }
}

// Event listeners
refreshLogsBtn.addEventListener('click', () => {
    loadLogs();
    showNotification('正在刷新日志...', 'info');
});

logsLimitSelect.addEventListener('change', () => {
    loadLogs();
});

console.log('Logs module initialized');
