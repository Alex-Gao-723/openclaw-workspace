// background.js - Service Worker
// 负责：截图捕获、DeepSeek AI 分析、IndexedDB 数据管理

// ============================================================
// 系统通知
// ============================================================

let lastNotificationId = null;

function notify(title, message, id = 'vn_' + Date.now()) {
  // 关闭上一条同类通知，避免堆积
  if (lastNotificationId) {
    chrome.notifications.clear(lastNotificationId);
  }
  chrome.notifications.create(id, {
    type: 'basic',
    iconUrl: 'icons/icon48.png',
    title,
    message,
    silent: true                   // 不播放系统提示音
  });
  lastNotificationId = id;

  // 4 秒后自动关闭
  setTimeout(() => chrome.notifications.clear(id), 4000);
}

// ============================================================
// IndexedDB 管理
// ============================================================

const DB_NAME = 'VideoNotesDB';
const DB_VERSION = 1;

function openDB() {
  return new Promise((resolve, reject) => {
    const request = indexedDB.open(DB_NAME, DB_VERSION);

    request.onupgradeneeded = (event) => {
      const db = event.target.result;

      if (!db.objectStoreNames.contains('notes')) {
        const notesStore = db.createObjectStore('notes', { keyPath: 'id' });
        notesStore.createIndex('videoUrl', 'videoUrl', { unique: false });
        notesStore.createIndex('updatedAt', 'updatedAt', { unique: false });
      }

      if (!db.objectStoreNames.contains('screenshots')) {
        const ssStore = db.createObjectStore('screenshots', { keyPath: 'id' });
        ssStore.createIndex('noteId', 'noteId', { unique: false });
      }
    };

    request.onsuccess = (event) => resolve(event.target.result);
    request.onerror = () => reject(request.error);
  });
}

// ============================================================
// DB 操作：笔记
// ============================================================

async function dbGetAllNotes() {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('notes', 'readonly');
    const req = tx.objectStore('notes').getAll();
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

async function dbGetNote(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('notes', 'readonly');
    const req = tx.objectStore('notes').get(id);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => reject(req.error);
  });
}

async function dbFindNoteByUrl(url) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('notes', 'readonly');
    const index = tx.objectStore('notes').index('videoUrl');
    const req = index.get(url);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => reject(req.error);
  });
}

async function dbSaveNote(note) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('notes', 'readwrite');
    tx.objectStore('notes').put(note);
    tx.oncomplete = () => resolve(note);
    tx.onerror = () => reject(tx.error);
  });
}

async function dbDeleteNote(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction(['notes', 'screenshots'], 'readwrite');
    tx.objectStore('notes').delete(id);

    // 同时删除关联的截图
    const index = tx.objectStore('screenshots').index('noteId');
    const req = index.openCursor(IDBKeyRange.only(id));
    req.onsuccess = (e) => {
      const cursor = e.target.result;
      if (cursor) {
        cursor.delete();
        cursor.continue();
      }
    };

    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

// ============================================================
// DB 操作：截图
// ============================================================

async function dbSaveScreenshot(screenshot) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('screenshots', 'readwrite');
    tx.objectStore('screenshots').add(screenshot);
    tx.oncomplete = () => resolve();
    tx.onerror = () => reject(tx.error);
  });
}

async function dbGetScreenshots(noteId) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('screenshots', 'readonly');
    const index = tx.objectStore('screenshots').index('noteId');
    const req = index.getAll(IDBKeyRange.only(noteId));
    req.onsuccess = () => resolve(req.result || []);
    req.onerror = () => reject(req.error);
  });
}

async function dbGetScreenshot(id) {
  const db = await openDB();
  return new Promise((resolve, reject) => {
    const tx = db.transaction('screenshots', 'readonly');
    const req = tx.objectStore('screenshots').get(id);
    req.onsuccess = () => resolve(req.result || null);
    req.onerror = () => reject(req.error);
  });
}

// ============================================================
// 工具函数
// ============================================================

async function getSettings() {
  return new Promise((resolve) => {
    chrome.storage.local.get(['apiKey', 'aiModel', 'aiPrompt'], (result) => {
      resolve({
        apiKey: result.apiKey || '',
        aiModel: result.aiModel || 'deepseek-v4-pro',
        aiPrompt: result.aiPrompt || ''
      });
    });
  });
}

function generateId(prefix) {
  return `${prefix}_${Date.now()}_${Math.random().toString(36).slice(2, 7)}`;
}

// ============================================================
// DeepSeek AI 分析
// ============================================================

const DEFAULT_PROMPT = '请分析这个视频截图的内容，用简洁的中文（3-5句话）描述截图中的主要信息和关键点。如有重要文字、公式、代码或图表，请重点提取和说明。输出格式：直接输出分析内容，不需要标题。';

// 压缩图片：缩放到 maxWidth 并转为低质量 JPEG，减少 token 消耗
async function compressImage(dataUrl, maxWidth = 800) {
  try {
    const res  = await fetch(dataUrl);
    const blob = await res.blob();
    const bmp  = await createImageBitmap(blob);

    const scale  = Math.min(1, maxWidth / bmp.width);
    const w = Math.round(bmp.width  * scale);
    const h = Math.round(bmp.height * scale);

    const canvas = new OffscreenCanvas(w, h);
    canvas.getContext('2d').drawImage(bmp, 0, 0, w, h);

    const outBlob = await canvas.convertToBlob({ type: 'image/jpeg', quality: 0.65 });

    return new Promise((resolve, reject) => {
      const reader = new FileReader();
      reader.onload  = () => resolve(reader.result);
      reader.onerror = reject;
      reader.readAsDataURL(outBlob);
    });
  } catch (e) {
    // 压缩失败就用原图
    return dataUrl;
  }
}

async function callDeepSeek(apiKey, model, messages) {
  const res = await fetch('https://api.deepseek.com/v1/chat/completions', {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${apiKey}`, 'Content-Type': 'application/json' },
    body: JSON.stringify({ model, max_tokens: 600, messages })
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error?.message || `HTTP ${res.status}`);
  return json.choices[0].message.content;
}

async function analyzeScreenshot(imageDataUrl, apiKey, model, customPrompt) {
  const prompt = customPrompt || DEFAULT_PROMPT;
  // 先压缩图片，再拼入文本发送
  const compressed = await compressImage(imageDataUrl);
  return await callDeepSeek(apiKey, model, [{
    role: 'user',
    content: `${prompt}\n\n图片内容：${compressed}`
  }]);
}

// ============================================================
// AI 任务串行队列（防止多张截图并发写库时互相覆盖）
// ============================================================

const aiQueue = [];
let aiRunning = false;

function enqueueAI(task) {
  aiQueue.push(task);
  if (!aiRunning) drainAIQueue();
}

async function drainAIQueue() {
  aiRunning = true;
  while (aiQueue.length > 0) {
    const task = aiQueue.shift();
    try { await task(); } catch (e) { console.error('[AI queue]', e); }
  }
  aiRunning = false;
}

// ============================================================
// 核心：截图捕获流程
// ============================================================

async function handleCapture(tab, data = {}) {
  const { videoTime = '', videoTitle = tab.title || '未知视频' } = data;

  // 1. 截取当前标签页截图
  const imageDataUrl = await chrome.tabs.captureVisibleTab(tab.windowId, {
    format: 'jpeg',
    quality: 85
  });

  // 2. 查找或创建笔记
  const cleanUrl = tab.url.split('#')[0]; // 去掉 hash，便于归类
  let note = await dbFindNoteByUrl(cleanUrl);

  if (!note) {
    const title = videoTitle.slice(0, 80);
    note = {
      id: generateId('note'),
      videoTitle: title,
      videoUrl: cleanUrl,
      createdAt: new Date().toISOString(),
      updatedAt: new Date().toISOString(),
      content: `# ${title}\n\n**来源**: [${cleanUrl}](${cleanUrl})\n\n`
    };
  }

  // 3. 保存截图到 IndexedDB
  const screenshotId = generateId('ss');
  await dbSaveScreenshot({
    id: screenshotId,
    noteId: note.id,
    videoTime,
    timestamp: new Date().toISOString(),
    imageData: imageDataUrl
  });

  // 4. 先保存截图占位符到笔记（立即可见）
  // 占位符含唯一 screenshotId，多张截图时精确替换，不互相干扰
  const PENDING_TAG = `⏳_${screenshotId}`;
  const timeLabel = videoTime ? ` \`${videoTime}\`` : '';
  const dateLabel = new Date().toLocaleString('zh-CN', { hour12: false });
  const placeholder = [
    '',
    '---',
    '',
    `## 截图${timeLabel} — ${dateLabel}`,
    '',
    `![截图](screenshot://${screenshotId})`,
    '',
    '**AI 分析**：',
    '',
    `> ${PENDING_TAG}`,
    '',
    '**我的笔记**：',
    '',
    ''
  ].join('\n');

  note.content += placeholder;
  note.updatedAt = new Date().toISOString();
  await dbSaveNote(note);

  // 5. 通知：截图已保存
  const notifyLabel = videoTime ? ` [${videoTime}]` : '';
  notify('📸 截图已保存', `${videoTitle}${notifyLabel}\nAI 正在分析内容...`);
  notifyTab(tab.id, { type: 'SCREENSHOT_SAVED' });

  // 6. 加入 AI 串行队列（保证多张截图顺序处理，不并发写库）
  enqueueAI(async () => {
    let aiText = '';
    try {
      const { apiKey, aiModel, aiPrompt } = await getSettings();
      if (!apiKey) {
        aiText = '请在扩展设置中配置 DeepSeek API Key 以启用 AI 分析。';
      } else {
        aiText = await analyzeScreenshot(imageDataUrl, apiKey, aiModel, aiPrompt);
      }
    } catch (err) {
      aiText = `AI 分析失败：${err.message}`;
    }

    // 用唯一 TAG 精确替换当前截图的占位符
    const freshNote = await dbGetNote(note.id);
    if (freshNote && freshNote.content.includes(PENDING_TAG)) {
      freshNote.content = freshNote.content.replace(
        `> ${PENDING_TAG}`,
        aiText.split('\n').map(l => `> ${l}`).join('\n')
      );
      freshNote.updatedAt = new Date().toISOString();
      await dbSaveNote(freshNote);
    }

    notifyTab(tab.id, { type: 'AI_ANALYSIS_DONE', noteId: note.id });
  });

  return { noteId: note.id, screenshotId };
}

function notifyTab(tabId, message) {
  chrome.tabs.sendMessage(tabId, message).catch(() => {});
}

// ============================================================
// 命令：键盘快捷键
// ============================================================

chrome.commands.onCommand.addListener(async (command) => {
  if (command !== 'capture-screenshot') return;

  const [tab] = await chrome.tabs.query({ active: true, currentWindow: true });
  if (!tab) return;

  try {
    // 向 content script 获取视频信息
    const info = await chrome.tabs.sendMessage(tab.id, { type: 'GET_VIDEO_INFO' });
    await handleCapture(tab, info || {});
  } catch (err) {
    // content script 未注入时直接截图
    await handleCapture(tab, {}).catch(console.error);
  }
});

// ============================================================
// 消息处理：来自 content.js 和 popup.js
// ============================================================

chrome.runtime.onMessage.addListener((message, sender, sendResponse) => {
  const respond = (promise) => {
    promise
      .then((data) => sendResponse({ ok: true, data }))
      .catch((err) => sendResponse({ ok: false, error: err.message }));
    return true; // 保持通道异步
  };

  switch (message.type) {
    // content.js 触发截图
    case 'CAPTURE_SCREENSHOT':
      return respond(handleCapture(sender.tab, message.data || {}));

    // popup.js 查询
    case 'GET_NOTES':
      return respond(dbGetAllNotes());

    case 'GET_NOTE':
      return respond(dbGetNote(message.id));

    case 'GET_SCREENSHOTS':
      return respond(dbGetScreenshots(message.noteId));

    case 'GET_SCREENSHOT':
      return respond(dbGetScreenshot(message.id));

    case 'SAVE_NOTE':
      return respond(dbSaveNote({ ...message.note, updatedAt: new Date().toISOString() }));

    case 'DELETE_NOTE':
      return respond(dbDeleteNote(message.id));

    case 'CREATE_NOTE': {
      const newNote = {
        id: generateId('note'),
        videoTitle: message.data.videoTitle || '新笔记',
        videoUrl: message.data.videoUrl || '',
        createdAt: new Date().toISOString(),
        updatedAt: new Date().toISOString(),
        content: message.data.content || `# ${message.data.videoTitle || '新笔记'}\n\n`
      };
      return respond(dbSaveNote(newNote));
    }

    default:
      return false;
  }
});
