// test_api.js - DeepSeek API 测试脚本
// 运行方式：node test_api.js

import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

// 读取 .env
const __dir = dirname(fileURLToPath(import.meta.url));
const env = Object.fromEntries(
  readFileSync(join(__dir, '.env'), 'utf-8')
    .split('\n')
    .filter(l => l.includes('=') && !l.startsWith('#'))
    .map(l => l.trim().split('='))
);

const API_KEY = env.DEEPSEEK_API_KEY;
const MODEL   = env.DEEPSEEK_MODEL || 'deepseek-v4-pro';
const BASE    = env.DEEPSEEK_API_BASE || 'https://api.deepseek.com/v1';

const RESET = '\x1b[0m', GREEN = '\x1b[32m', RED = '\x1b[31m', CYAN = '\x1b[36m', GRAY = '\x1b[90m', YELLOW = '\x1b[33m';
const ok   = msg => console.log(`${GREEN}✅ ${msg}${RESET}`);
const fail = msg => console.log(`${RED}❌ ${msg}${RESET}`);
const info = msg => console.log(`${CYAN}▶ ${msg}${RESET}`);
const warn = msg => console.log(`${YELLOW}⚠️  ${msg}${RESET}`);

async function post(path, body) {
  const res = await fetch(`${BASE}${path}`, {
    method: 'POST',
    headers: { 'Authorization': `Bearer ${API_KEY}`, 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  const json = await res.json();
  if (!res.ok) throw new Error(json.error?.message || `HTTP ${res.status}`);
  return json;
}

// ── 测试 1：鉴权 + 文本对话 ──────────────────────────────
async function testText() {
  info('测试 1：文本对话（鉴权验证）');
  const data = await post('/chat/completions', {
    model: MODEL,
    max_tokens: 30,
    messages: [{ role: 'user', content: '用一句话介绍你自己。' }]
  });
  const reply = data.choices[0].message.content;
  ok(`鉴权通过，模型：${data.model}`);
  console.log(`${GRAY}   回复：${reply}${RESET}`);
  console.log(`${GRAY}   tokens 消耗：${data.usage?.total_tokens ?? '?'}${RESET}`);
}

// ── 测试 2：视觉能力探测 ─────────────────────────────────
async function testVision() {
  info('测试 2：视觉能力探测');
  const tiny = 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg==';
  try {
    const data = await post('/chat/completions', {
      model: MODEL,
      max_tokens: 30,
      messages: [{
        role: 'user',
        content: [
          { type: 'image_url', image_url: { url: tiny } },
          { type: 'text', text: '这张图片是什么颜色？' }
        ]
      }]
    });
    ok(`视觉模式可用！回复：${data.choices[0].message.content}`);
    return true;
  } catch (e) {
    warn(`视觉模式不支持（${e.message.slice(0, 60)}）`);
    warn('将使用文本降级模式（基于视频标题生成笔记框架）');
    return false;
  }
}

// ── 测试 3：文本降级模式（核心功能验证）────────────────
async function testTextFallback() {
  info('测试 3：文本降级模式（截图后实际调用的逻辑）');
  const videoTitle = '【Vue3 源码解析】响应式原理 Proxy 与 Effect 深度剖析';
  const videoUrl   = 'https://www.bilibili.com/video/BV1example';
  const videoTime  = '08:42';

  const prompt = `我正在观看一个视频，现在暂停在 ${videoTime} 处，想记录当前内容要点。\n视频标题：${videoTitle}\n视频链接：${videoUrl}\n\n请根据视频标题推测这个时间段可能涉及的内容，给出一个通用的笔记框架（3-5行要点），帮助我在此基础上补充具体内容。`;

  const data = await post('/chat/completions', {
    model: MODEL,
    max_tokens: 300,
    messages: [{ role: 'user', content: prompt }]
  });
  const reply = data.choices[0].message.content;
  ok(`文本降级分析成功`);
  console.log(`${GRAY}   生成内容预览：\n${reply.split('\n').slice(0, 5).map(l => '   ' + l).join('\n')}${RESET}`);
  console.log(`${GRAY}   tokens 消耗：${data.usage?.total_tokens ?? '?'}${RESET}`);
}

// ── 主流程 ───────────────────────────────────────────────
console.log('\n' + '─'.repeat(50));
console.log('  DeepSeek API 测试');
console.log(`  Key：${API_KEY.slice(0, 8)}...${API_KEY.slice(-4)}`);
console.log(`  模型：${MODEL}  |  端点：${BASE}`);
console.log('─'.repeat(50) + '\n');

let passed = 0, failed = 0;

// 测试 1：文本对话
try { await testText(); passed++; } catch (e) { fail(`文本对话失败：${e.message}`); failed++; }
console.log();

// 测试 2：视觉探测（失败不计入 failed，仅提示）
const visionOk = await testVision();
console.log();

// 测试 3：文本降级（始终测试，这是实际会走的路径）
try { await testTextFallback(); passed++; } catch (e) { fail(`文本降级失败：${e.message}`); failed++; }
console.log();

console.log('─'.repeat(50));
console.log(`  结果：${GREEN}${passed} 通过${RESET}  ${failed > 0 ? RED + failed + ' 失败' + RESET : ''}  ${visionOk ? GREEN + '视觉 ✓' + RESET : YELLOW + '视觉降级模式' + RESET}`);
console.log('─'.repeat(50) + '\n');

if (failed > 0) process.exit(1);
