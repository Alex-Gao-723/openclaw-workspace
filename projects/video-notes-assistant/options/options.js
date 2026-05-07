// options.js

const DEFAULT_PROMPT = '请分析这个视频截图的内容，用简洁的中文（3-5句话）描述截图中的主要信息和关键点。如有重要文字、公式、代码或图表，请重点提取和说明。输出格式：直接输出分析内容，不需要标题。';

// ============================================================
// 工具函数
// ============================================================

function showStatus(msg, type = 'success') {
  const el = document.getElementById('api-status');
  el.textContent = msg;
  el.className = `status-msg status-${type}`;
  el.style.display = 'block';
  setTimeout(() => { el.style.display = 'none'; }, 4000);
}

function sendMsg(type, payload = {}) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type, ...payload }, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      if (response && response.ok) resolve(response.data);
      else reject(new Error(response?.error || '未知错误'));
    });
  });
}

// ============================================================
// 加载设置
// ============================================================

function loadSettings() {
  chrome.storage.local.get(['apiKey', 'aiModel', 'aiPrompt'], (result) => {
    document.getElementById('api-key').value = result.apiKey || '';
    document.getElementById('ai-model').value = result.aiModel || 'deepseek-v4-pro';
    document.getElementById('ai-prompt').value = result.aiPrompt || DEFAULT_PROMPT;
  });
}

// ============================================================
// 保存设置
// ============================================================

function saveSettings() {
  const apiKey = document.getElementById('api-key').value.trim();
  const aiModel = document.getElementById('ai-model').value;
  const aiPrompt = document.getElementById('ai-prompt').value.trim();

  chrome.storage.local.set({ apiKey, aiModel, aiPrompt }, () => {
    showStatus('✅ 设置已保存');
  });
}

// ============================================================
// 测试 API 连接
// ============================================================

async function testApiConnection() {
  const apiKey = document.getElementById('api-key').value.trim();
  if (!apiKey) {
    showStatus('⚠️ 请先填写 API Key', 'error');
    return;
  }

  const btn = document.getElementById('btn-test-api');
  btn.disabled = true;
  btn.textContent = '测试中...';
  showStatus('正在连接 DeepSeek API...', 'success');

  try {
    const response = await fetch('https://api.deepseek.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Authorization': `Bearer ${apiKey}`,
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        model: document.getElementById('ai-model').value,
        max_tokens: 10,
        messages: [{ role: 'user', content: 'hi' }]
      })
    });

    if (response.ok) {
      showStatus('✅ API 连接成功！');
    } else {
      const err = await response.json().catch(() => ({}));
      showStatus(`❌ 连接失败：${err.error?.message || response.status}`, 'error');
    }
  } catch (e) {
    showStatus(`❌ 网络错误：${e.message}`, 'error');
  } finally {
    btn.disabled = false;
    btn.textContent = '测试连接';
  }
}

// ============================================================
// 加载统计数据
// ============================================================

async function loadStats() {
  try {
    const notes = await sendMsg('GET_NOTES') || [];
    document.getElementById('stat-notes').textContent = notes.length;

    let totalSS = 0;
    let totalSize = 0;

    for (const note of notes) {
      const ssCount = (note.content.match(/screenshot:\/\//g) || []).length;
      totalSS += ssCount;
      totalSize += note.content.length;
    }

    document.getElementById('stat-screenshots').textContent = totalSS;

    // 粗略估算（截图数据存在 IndexedDB，不计算）
    const sizeMB = (totalSize / 1024 / 1024).toFixed(1);
    document.getElementById('stat-storage').textContent = sizeMB + ' MB+';
  } catch (e) {
    document.getElementById('stat-notes').textContent = '?';
    document.getElementById('stat-screenshots').textContent = '?';
    document.getElementById('stat-storage').textContent = '?';
  }
}

// ============================================================
// 清除所有数据
// ============================================================

async function clearAllData() {
  if (!confirm('确定要清除所有笔记和截图数据吗？此操作不可撤销！')) return;

  // 删除 IndexedDB
  const DBDeleteReq = indexedDB.deleteDatabase('VideoNotesDB');
  DBDeleteReq.onsuccess = () => {
    alert('所有数据已清除。');
    loadStats();
  };
  DBDeleteReq.onerror = () => {
    alert('清除失败，请刷新后重试。');
  };
}

// ============================================================
// 初始化
// ============================================================

document.addEventListener('DOMContentLoaded', () => {
  loadSettings();
  loadStats();

  // 显示/隐藏 API Key
  const keyInput = document.getElementById('api-key');
  const toggleBtn = document.getElementById('btn-toggle-key');
  toggleBtn.addEventListener('click', () => {
    if (keyInput.type === 'password') {
      keyInput.type = 'text';
      toggleBtn.textContent = '隐藏';
    } else {
      keyInput.type = 'password';
      toggleBtn.textContent = '显示';
    }
  });

  document.getElementById('btn-save-api').addEventListener('click', saveSettings);
  document.getElementById('btn-test-api').addEventListener('click', testApiConnection);
  document.getElementById('btn-clear-all').addEventListener('click', clearAllData);

  // Ctrl+S 保存
  document.addEventListener('keydown', (e) => {
    if ((e.metaKey || e.ctrlKey) && e.key === 's') {
      e.preventDefault();
      saveSettings();
    }
  });
});
