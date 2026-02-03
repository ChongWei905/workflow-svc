/**
 * Skills management module
 * Handles skills list, detail view, and script execution
 */

// DOM Elements
const skillsList = document.getElementById('skills-list');
const skillDetail = document.getElementById('skill-detail');
const refreshSkillsBtn = document.getElementById('refresh-skills');

let currentSkills = [];
let currentSkill = null;

/**
 * Load skills list from API
 */
async function loadSkills() {
    try {
        skillsList.innerHTML = '<div class="loading">加载中...</div>';

        const skills = await api('/skills');
        currentSkills = skills;

        displaySkillsList(skills);
    } catch (error) {
        console.error('Failed to load skills:', error);
        skillsList.innerHTML = `
            <div class="error-state">
                <p>加载失败: ${error.message}</p>
            </div>
        `;
        showNotification('加载 Skills 失败', 'error');
    }
}

/**
 * Display skills list
 * @param {Array} skills - Skills data
 */
function displaySkillsList(skills) {
    if (!skills || skills.length === 0) {
        skillsList.innerHTML = `
            <div class="empty-state">
                <p>没有找到 Skills</p>
            </div>
        `;
        return;
    }

    skillsList.innerHTML = '';

    skills.forEach(skill => {
        const item = document.createElement('div');
        item.className = 'skill-item';
        item.dataset.skillName = skill.name;

        const description = skill.description.length > 50
            ? skill.description.substring(0, 50) + '...'
            : skill.description;

        item.innerHTML = `
            <strong>${escapeHtml(skill.name)}</strong>
            <p>${escapeHtml(description)}</p>
            <small>${skill.scripts_count} 个脚本</small>
        `;

        item.addEventListener('click', () => {
            // Remove active class from all items
            document.querySelectorAll('.skill-item').forEach(i => i.classList.remove('active'));
            // Add active class to clicked item
            item.classList.add('active');
            // Load skill detail
            loadSkillDetail(skill.name);
        });

        skillsList.appendChild(item);
    });
}

/**
 * Load skill detail from API
 * @param {string} name - Skill name
 */
async function loadSkillDetail(name) {
    try {
        skillDetail.innerHTML = '<div class="loading">加载中...</div>';

        const skill = await api(`/skills/${encodeURIComponent(name)}`);
        currentSkill = skill;

        displaySkillDetail(skill);
    } catch (error) {
        console.error('Failed to load skill detail:', error);
        skillDetail.innerHTML = `
            <div class="error-state">
                <p>加载失败: ${error.message}</p>
            </div>
        `;
        showNotification('加载 Skill 详情失败', 'error');
    }
}

/**
 * Display skill detail
 * @param {object} skill - Skill data
 */
function displaySkillDetail(skill) {
    const scriptsHtml = skill.scripts && skill.scripts.length > 0
        ? skill.scripts.map(script => `
            <div class="script-item">
                <div>
                    <strong>${escapeHtml(script.name)}</strong>
                    <small>(${escapeHtml(script.language)})</small>
                    ${script.description ? `<p>${escapeHtml(script.description)}</p>` : ''}
                </div>
                <button class="script-btn" onclick="executeScript('${escapeHtml(skill.name)}', '${escapeHtml(script.name)}')">
                    执行
                </button>
            </div>
        `).join('')
        : '<p style="color: var(--text-muted);">该 Skill 没有脚本</p>';

    skillDetail.innerHTML = `
        <h2>${escapeHtml(skill.name)}</h2>
        <p><strong>描述:</strong> ${escapeHtml(skill.description)}</p>
        <p><strong>路径:</strong> <code>${escapeHtml(skill.path)}</code></p>

        <div class="skill-content">
            <h3>文档内容</h3>
            <pre>${escapeHtml(skill.content)}</pre>
        </div>

        <div class="skill-scripts">
            <h3>脚本列表 (${skill.scripts ? skill.scripts.length : 0})</h3>
            ${scriptsHtml}
        </div>
    `;
}

/**
 * Execute a script
 * @param {string} skillName - Skill name
 * @param {string} scriptName - Script name
 */
async function executeScript(skillName, scriptName) {
    const argsInput = prompt('输入脚本参数（逗号分隔，留空表示无参数）：');

    if (argsInput === null) {
        return; // User cancelled
    }

    const arguments = argsInput
        ? argsInput.split(',').map(a => a.trim()).filter(a => a)
        : [];

    try {
        showNotification('正在执行脚本...', 'info');

        const result = await api(
            `/skills/${encodeURIComponent(skillName)}/scripts/${encodeURIComponent(scriptName)}`,
            {
                method: 'POST',
                body: JSON.stringify({ arguments })
            }
        );

        // Show result in a nice format
        const resultHtml = `
            <h4>执行结果</h4>
            <p><strong>Skill:</strong> ${escapeHtml(skillName)}</p>
            <p><strong>脚本:</strong> ${escapeHtml(scriptName)}</p>
            ${arguments.length > 0 ? `<p><strong>参数:</strong> ${arguments.map(escapeHtml).join(', ')}</p>` : ''}
            <pre style="background: var(--bg-tertiary); padding: 12px; border-radius: 8px; overflow-x: auto; max-height: 400px;">${escapeHtml(result.result)}</pre>
        `;

        // Create modal or show in chat
        showResultModal(resultHtml);
        showNotification('脚本执行完成', 'success');

    } catch (error) {
        console.error('Script execution failed:', error);
        showNotification('执行失败: ' + error.message, 'error');
    }
}

/**
 * Show result in a modal
 * @param {string} html - Result HTML
 */
function showResultModal(html) {
    // Create modal overlay
    const overlay = document.createElement('div');
    overlay.style.cssText = `
        position: fixed;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background: rgba(0,0,0,0.5);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
    `;

    // Create modal content
    const modal = document.createElement('div');
    modal.style.cssText = `
        background: white;
        padding: 24px;
        border-radius: 12px;
        max-width: 800px;
        max-height: 80vh;
        overflow-y: auto;
        box-shadow: 0 10px 40px rgba(0,0,0,0.2);
    `;
    modal.innerHTML = `
        ${html}
        <button style="margin-top: 20px; padding: 10px 20px; background: var(--primary-color); color: white; border: none; border-radius: 8px; cursor: pointer; font-size: 14px;">关闭</button>
    `;

    // Close button handler
    modal.querySelector('button').addEventListener('click', () => {
        document.body.removeChild(overlay);
    });

    // Close on overlay click
    overlay.addEventListener('click', (e) => {
        if (e.target === overlay) {
            document.body.removeChild(overlay);
        }
    });

    overlay.appendChild(modal);
    document.body.appendChild(overlay);
}

// Event listener for refresh button
refreshSkillsBtn.addEventListener('click', () => {
    loadSkills();
    showNotification('正在刷新...', 'info');
});

console.log('Skills module initialized');
