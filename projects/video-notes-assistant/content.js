// content.js - 注入到所有页面
// 负责：快捷键截图通知、视频信息提取

(function () {
  'use strict';

  if (window.__videoNotesInjected) return;
  window.__videoNotesInjected = true;

  // ============================================================
  // 视频信息提取
  // ============================================================

  function getVideoElement() {
    const videos = Array.from(document.querySelectorAll('video'));
    return videos.find(v => !v.paused && v.readyState > 0) || videos[0] || null;
  }

  function formatTime(seconds) {
    if (!seconds || isNaN(seconds)) return '';
    const h = Math.floor(seconds / 3600);
    const m = Math.floor((seconds % 3600) / 60);
    const s = Math.floor(seconds % 60);
    if (h > 0) return `${h}:${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
    return `${String(m).padStart(2, '0')}:${String(s).padStart(2, '0')}`;
  }

  function getVideoTime() {
    const video = getVideoElement();
    return video ? formatTime(video.currentTime) : '';
  }

  function getVideoTitle() {
    const selectors = [
      'h1.ytd-watch-metadata yt-formatted-string',
      'h1.ytd-watch-metadata',
      '.video-title-cont h1',
      '#viewbox_report .tit',
      'h1[class*="title"]',
      '.title-text',
      'h1'
    ];
    for (const sel of selectors) {
      const text = document.querySelector(sel)?.textContent?.trim();
      if (text && text.length > 1) return text.slice(0, 100);
    }
    return document.title.slice(0, 100);
  }

  // ============================================================
  // Toast 通知
  // ============================================================

  function showToast(message, type = 'success') {
    const existing = document.getElementById('__vn_toast__');
    if (existing) {
      try { existing.hidePopover(); } catch (_) {}
      existing.remove();
    }

    const colors = { success: '#22c55e', error: '#ef4444', info: '#3b82f6', warning: '#f59e0b' };

    const toast = document.createElement('div');
    toast.id = '__vn_toast__';
    // all:initial 清除继承样式，!important 覆盖 [popover] UA 默认的
    // inset:0 / margin:auto，确保 bottom/right 定位生效
    toast.style.cssText = `
      all: initial !important;
      position: fixed !important;
      bottom: 24px !important;
      right: 24px !important;
      inset: auto !important;
      margin: 0 !important;
      border: none !important;
      padding: 10px 16px !important;
      background: ${colors[type] || colors.info} !important;
      color: white !important;
      border-radius: 10px !important;
      font-size: 13px !important;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif !important;
      z-index: 2147483647 !important;
      box-shadow: 0 4px 16px rgba(0,0,0,0.3) !important;
      max-width: 300px !important;
      line-height: 1.4 !important;
      opacity: 1 !important;
      transition: opacity 0.4s ease !important;
      pointer-events: none !important;
      white-space: pre-line !important;
    `;
    toast.textContent = message;

    const usePopover = typeof toast.showPopover === 'function';
    if (usePopover) toast.setAttribute('popover', 'manual');

    document.documentElement.appendChild(toast);
    if (usePopover) toast.showPopover();

    setTimeout(() => {
      toast.style.setProperty('opacity', '0', 'important');
      setTimeout(() => {
        try { if (usePopover) toast.hidePopover(); } catch (_) {}
        toast.remove();
      }, 400);
    }, 3000);
  }

  // ============================================================
  // 消息监听（来自 background.js）
  // ============================================================

  chrome.runtime.onMessage.addListener((message, _sender, sendResponse) => {
    if (message.type === 'GET_VIDEO_INFO') {
      sendResponse({ videoTime: getVideoTime(), videoTitle: getVideoTitle() });
      return true;
    }
    if (message.type === 'SCREENSHOT_SAVED') {
      showToast('✅ 截图已保存，AI 分析中...', 'success');
    }
    if (message.type === 'AI_ANALYSIS_DONE') {
      showToast('🤖 AI 分析完成', 'success');
    }
  });

})();
