// popup.js

let allNotes = [];
let currentNoteId = null;
let screenshotsCache = {};  // noteId -> { ssId: imageData }
let isEditMode = false;
let originalContent = '';

// ============================================================
// 与 background.js 通信
// ============================================================

function sendMsg(type, payload = {}) {
  return new Promise((resolve, reject) => {
    chrome.runtime.sendMessage({ type, ...payload }, (response) => {
      if (chrome.runtime.lastError) {
        reject(new Error(chrome.runtime.lastError.message));
        return;
      }
      if (response && response.ok) {
        resolve(response.data);
      } else {
        reject(new Error(response?.error || '未知错误'));
      }
    });
  });
}

// ============================================================
// Markdown 渲染
// ============================================================

function escapeHtml(str) {
  return String(str)
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;');
}

function renderInline(text, ssMap) {
  // 先处理截图引用，避免被其他规则破坏
  let result = '';
  let i = 0;

  // 逐字符扫描，处理 ![...](screenshot://...) 和 ![...](...)
  const imgRegex = /!\[([^\]]*)\]\((screenshot:\/\/[^)]+|[^)]+)\)/g;
  let lastIndex = 0;
  let match;

  // 先处理所有图片
  const processedImages = text.replace(/!\[([^\]]*)\]\(screenshot:\/\/([^)]+)\)/g, (m, alt, id) => {
    const imgData = ssMap && ssMap[id];
    if (imgData) {
      return `<img src="${imgData}" alt="${escapeHtml(alt || '截图')}" class="note-screenshot">`;
    }
    return `<span class="screenshot-loading">[截图加载中 ${id.slice(-6)}]</span>`;
  });

  return processedImages
    // 普通图片
    .replace(/!\[([^\]]*)\]\(([^)]+)\)/g, '<img src="$2" alt="$1" class="note-screenshot">')
    // 链接
    .replace(/\[([^\]]+)\]\(([^)]+)\)/g, '<a href="$2" target="_blank">$1</a>')
    // 粗体
    .replace(/\*\*([^*\n]+)\*\*/g, '<strong>$1</strong>')
    // 斜体
    .replace(/\*([^*\n]+)\*/g, '<em>$1</em>')
    // 行内代码
    .replace(/`([^`\n]+)`/g, '<code>$1</code>');
}

function renderMarkdown(md, ssMap) {
  if (!md) return '';

  const lines = md.split('\n');
  const parts = [];
  let i = 0;

  while (i < lines.length) {
    const line = lines[i];

    // 代码块
    if (line.startsWith('```')) {
      const lang = line.slice(3).trim();
      const codeLines = [];
      i++;
      while (i < lines.length && !lines[i].startsWith('```')) {
        codeLines.push(escapeHtml(lines[i]));
        i++;
      }
      parts.push(`<pre><code>${codeLines.join('\n')}</code></pre>`);
      i++;
      continue;
    }

    // 水平线
    if (/^-{3,}$/.test(line.trim())) {
      parts.push('<hr>');
      i++;
      continue;
    }

    // 标题
    const h1 = line.match(/^# (.+)/);
    const h2 = line.match(/^## (.+)/);
    const h3 = line.match(/^### (.+)/);

    if (h1) {
      parts.push(`<h1>${renderInline(escapeHtml(h1[1]), ssMap)}</h1>`);
      i++; continue;
    }
    if (h2) {
      parts.push(`<h2>${renderInline(escapeHtml(h2[1]), ssMap)}</h2>`);
      i++; continue;
    }
    if (h3) {
      parts.push(`<h3>${renderInline(escapeHtml(h3[1]), ssMap)}</h3>`);
      i++; continue;
    }

    // 引用块
    if (line.startsWith('>')) {
      const bqLines = [];
      while (i < lines.length && (lines[i].startsWith('>') || lines[i].trim() === '')) {
        bqLines.push(lines[i].startsWith('>') ? lines[i].slice(1).trim() : '');
        i++;
      }
      const inner = bqLines.map(l => renderInline(escapeHtml(l), ssMap)).join('<br>');
      parts.push(`<blockquote>${inner}</blockquote>`);
      continue;
    }

    // 图片行（单独一行的截图）
    if (/^!\[/.test(line.trim())) {
      parts.push('<p>' + renderInline(escapeHtml(line), ssMap) + '</p>');
      i++; continue;
    }

    // 空行
    if (line.trim() === '') {
      parts.push('<br>');
      i++; continue;
    }

    // 普通段落
    parts.push('<p>' + renderInline(escapeHtml(line), ssMap) + '</p>');
    i++;
  }

  return parts.join('\n');
}

// ============================================================
// 加载截图数据
// ============================================================

async function loadScreenshots(noteId) {
  if (screenshotsCache[noteId]) return screenshotsCache[noteId];

  try {
    const screenshots = await sendMsg('GET_SCREENSHOTS', { noteId });
    const map = {};
    for (const ss of screenshots) {
      map[ss.id] = ss.imageData;
    }
    screenshotsCache[noteId] = map;
    return map;
  } catch (e) {
    return {};
  }
}

// ============================================================
// 渲染笔记列表
// ============================================================

function countScreenshots(content) {
  return (content.match(/screenshot:\/\//g) || []).length;
}

function formatDate(iso) {
  const d = new Date(iso);
  const now = new Date();
  const diff = now - d;

  if (diff < 60000) return '刚刚';
  if (diff < 3600000) return `${Math.floor(diff / 60000)} 分钟前`;
  if (diff < 86400000) return `${Math.floor(diff / 3600000)} 小时前`;
  if (diff < 604800000) return `${Math.floor(diff / 86400000)} 天前`;

  return d.toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
}

function renderNoteList(notes, query = '') {
  const listEl = document.getElementById('notes-list');

  let filtered = notes;
  if (query) {
    const q = query.toLowerCase();
    filtered = notes.filter(n =>
      n.videoTitle.toLowerCase().includes(q) ||
      n.content.toLowerCase().includes(q)
    );
  }

  // 按更新时间降序排列
  filtered.sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));

  if (!filtered.length) {
    listEl.innerHTML = `<div class="empty-state">${query ? '没有匹配的笔记' : '还没有笔记\n在视频页面按 Alt+S 开始截图'}</div>`;
    return;
  }

  listEl.innerHTML = filtered.map(note => {
    const ssCount = countScreenshots(note.content);
    const isActive = note.id === currentNoteId;
    return `
      <div class="note-item ${isActive ? 'active' : ''}" data-id="${note.id}">
        <div class="note-item-title">${escapeHtml(note.videoTitle || '未知视频')}</div>
        <div class="note-item-meta">
          <span class="note-item-date">${formatDate(note.updatedAt)}</span>
          ${ssCount > 0 ? `<span class="note-item-count">📷 ${ssCount}</span>` : ''}
        </div>
      </div>
    `;
  }).join('');

  // 绑定点击事件
  listEl.querySelectorAll('.note-item').forEach(item => {
    item.addEventListener('click', () => {
      const id = item.dataset.id;
      selectNote(id);
    });
  });
}

// ============================================================
// 选择并显示笔记
// ============================================================

async function selectNote(id) {
  currentNoteId = id;

  // 先退出编辑模式
  if (isEditMode) exitEditMode(false);

  // 更新列表高亮
  document.querySelectorAll('.note-item').forEach(el => {
    el.classList.toggle('active', el.dataset.id === id);
  });

  const note = allNotes.find(n => n.id === id);
  if (!note) return;

  // 显示面板
  document.getElementById('panel-empty').style.display = 'none';
  document.getElementById('panel-note').style.display = 'flex';

  // 填充 header
  document.getElementById('note-title').textContent = note.videoTitle || '未知视频';
  const urlEl = document.getElementById('note-url');
  if (note.videoUrl) {
    urlEl.textContent = note.videoUrl;
    urlEl.href = note.videoUrl;
  } else {
    urlEl.textContent = '';
    urlEl.href = '#';
  }

  // 渲染内容（先展示加载占位）
  const renderedEl = document.getElementById('note-rendered');
  renderedEl.innerHTML = '<span style="color:var(--text3)">加载中...</span>';

  // 加载截图并渲染
  const ssMap = await loadScreenshots(id);
  renderedEl.innerHTML = renderMarkdown(note.content, ssMap);
}

// ============================================================
// 编辑模式
// ============================================================

function enterEditMode() {
  const note = allNotes.find(n => n.id === currentNoteId);
  if (!note) return;

  isEditMode = true;
  originalContent = note.content;

  document.getElementById('note-editor').value = note.content;
  document.getElementById('view-mode').style.display = 'none';
  document.getElementById('edit-mode').style.display = 'flex';
  document.getElementById('btn-edit').style.display = 'none';
  document.getElementById('btn-save').style.display = '';
  document.getElementById('btn-cancel').style.display = '';
  document.getElementById('btn-export').style.display = 'none';
  document.getElementById('btn-delete').style.display = 'none';
}

async function saveEditMode() {
  const note = allNotes.find(n => n.id === currentNoteId);
  if (!note) return;

  const newContent = document.getElementById('note-editor').value;
  note.content = newContent;

  try {
    await sendMsg('SAVE_NOTE', { note });
    exitEditMode(true);
  } catch (e) {
    alert('保存失败：' + e.message);
  }
}

function exitEditMode(keepChanges) {
  if (!keepChanges) {
    const note = allNotes.find(n => n.id === currentNoteId);
    if (note) note.content = originalContent;
  }

  isEditMode = false;
  document.getElementById('view-mode').style.display = '';
  document.getElementById('edit-mode').style.display = 'none';
  document.getElementById('btn-edit').style.display = '';
  document.getElementById('btn-save').style.display = 'none';
  document.getElementById('btn-cancel').style.display = 'none';
  document.getElementById('btn-export').style.display = '';
  document.getElementById('btn-delete').style.display = '';

  // 重新渲染
  if (currentNoteId) selectNote(currentNoteId);
}

// ============================================================
// 导出笔记
// ============================================================

async function exportNote() {
  const note = allNotes.find(n => n.id === currentNoteId);
  if (!note) return;

  // 获取所有截图，嵌入 base64
  const ssMap = await loadScreenshots(note.id);

  // 替换 screenshot:// 链接为 base64 data URL
  let exportContent = note.content.replace(
    /screenshot:\/\/([^\s)]+)/g,
    (m, id) => ssMap[id] || m
  );

  const blob = new Blob([exportContent], { type: 'text/markdown;charset=utf-8' });
  const url = URL.createObjectURL(blob);
  const filename = (note.videoTitle || '视频笔记').replace(/[/\\?%*:|"<>]/g, '_') + '.md';

  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  a.click();
  URL.revokeObjectURL(url);
}

// ============================================================
// 删除笔记
// ============================================================

function showDeleteModal() {
  document.getElementById('modal-delete').style.display = 'flex';
}

function hideDeleteModal() {
  document.getElementById('modal-delete').style.display = 'none';
}

async function deleteCurrentNote() {
  if (!currentNoteId) return;

  try {
    await sendMsg('DELETE_NOTE', { id: currentNoteId });
    allNotes = allNotes.filter(n => n.id !== currentNoteId);
    delete screenshotsCache[currentNoteId];
    currentNoteId = null;

    document.getElementById('panel-empty').style.display = '';
    document.getElementById('panel-note').style.display = 'none';

    renderNoteList(allNotes);
  } catch (e) {
    alert('删除失败：' + e.message);
  }

  hideDeleteModal();
}

// ============================================================
// 新建笔记
// ============================================================

function showNewNoteModal() {
  document.getElementById('modal-new').style.display = 'flex';
  document.getElementById('new-title').value = '';
  document.getElementById('new-url').value = '';
  setTimeout(() => document.getElementById('new-title').focus(), 50);
}

function hideNewNoteModal() {
  document.getElementById('modal-new').style.display = 'none';
}

async function createNewNote() {
  const title = document.getElementById('new-title').value.trim();
  const url = document.getElementById('new-url').value.trim();

  if (!title) {
    document.getElementById('new-title').focus();
    return;
  }

  try {
    const newNote = await sendMsg('CREATE_NOTE', {
      data: { videoTitle: title, videoUrl: url }
    });
    allNotes.push(newNote);
    renderNoteList(allNotes);
    selectNote(newNote.id);
    hideNewNoteModal();
  } catch (e) {
    alert('创建失败：' + e.message);
  }
}

// ============================================================
// 主初始化
// ============================================================

async function init() {
  // 加载笔记列表
  try {
    allNotes = await sendMsg('GET_NOTES') || [];
  } catch (e) {
    allNotes = [];
  }

  renderNoteList(allNotes);

  // 搜索
  document.getElementById('search-input').addEventListener('input', (e) => {
    renderNoteList(allNotes, e.target.value.trim());
  });

  // 工具栏按钮
  document.getElementById('btn-edit').addEventListener('click', enterEditMode);
  document.getElementById('btn-save').addEventListener('click', saveEditMode);
  document.getElementById('btn-cancel').addEventListener('click', () => exitEditMode(false));
  document.getElementById('btn-export').addEventListener('click', exportNote);
  document.getElementById('btn-delete').addEventListener('click', showDeleteModal);

  // 新建
  document.getElementById('btn-new-note').addEventListener('click', showNewNoteModal);
  document.getElementById('btn-modal-cancel').addEventListener('click', hideNewNoteModal);
  document.getElementById('btn-modal-create').addEventListener('click', createNewNote);
  document.getElementById('new-title').addEventListener('keydown', (e) => {
    if (e.key === 'Enter') createNewNote();
    if (e.key === 'Escape') hideNewNoteModal();
  });

  // 删除确认
  document.getElementById('btn-delete-cancel').addEventListener('click', hideDeleteModal);
  document.getElementById('btn-delete-confirm').addEventListener('click', deleteCurrentNote);

  // 设置页
  document.getElementById('btn-settings').addEventListener('click', () => {
    chrome.runtime.openOptionsPage();
  });

  // 编辑器快捷键
  document.getElementById('note-editor').addEventListener('keydown', (e) => {
    if (e.key === 's' && (e.metaKey || e.ctrlKey)) {
      e.preventDefault();
      saveEditMode();
    }
    if (e.key === 'Escape') {
      exitEditMode(false);
    }
  });

  // 点击模态框背景关闭
  document.getElementById('modal-new').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) hideNewNoteModal();
  });
  document.getElementById('modal-delete').addEventListener('click', (e) => {
    if (e.target === e.currentTarget) hideDeleteModal();
  });

  // 如果有笔记，自动选中第一条
  if (allNotes.length > 0) {
    const sorted = [...allNotes].sort((a, b) => new Date(b.updatedAt) - new Date(a.updatedAt));
    selectNote(sorted[0].id);
  }
}

document.addEventListener('DOMContentLoaded', init);
