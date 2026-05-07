// test_vision_formats.js - 探测 deepseek-v4-pro 接受的图片格式
import { readFileSync } from 'fs';
import { fileURLToPath } from 'url';
import { dirname, join } from 'path';

const __dir = dirname(fileURLToPath(import.meta.url));
const env = Object.fromEntries(
  readFileSync(join(__dir, '.env'), 'utf-8')
    .split('\n').filter(l => l.includes('=') && !l.startsWith('#'))
    .map(l => l.trim().split('='))
);

const API_KEY = env.DEEPSEEK_API_KEY;
const BASE    = env.DEEPSEEK_API_BASE || 'https://api.deepseek.com/v1';
const MODEL   = 'deepseek-v4-pro';

// 1×1 红色像素 PNG
const TINY_PNG_B64 = 'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwADhQGAWjR9awAAAABJRU5ErkJggg==';
const DATA_URL     = `data:image/png;base64,${TINY_PNG_B64}`;

const GREEN = '\x1b[32m', RED = '\x1b[31m', CYAN = '\x1b[36m', GRAY = '\x1b[90m', RESET = '\x1b[0m';

async function tryFormat(name, messages) {
  process.stdout.write(`${CYAN}▶ ${name}${RESET} ... `);
  try {
    const res = await fetch(`${BASE}/chat/completions`, {
      method: 'POST',
      headers: { 'Authorization': `Bearer ${API_KEY}`, 'Content-Type': 'application/json' },
      body: JSON.stringify({ model: MODEL, max_tokens: 30, messages })
    });
    const json = await res.json();
    if (!res.ok) {
      console.log(`${RED}✗ ${json.error?.message?.slice(0, 80)}${RESET}`);
      return false;
    }
    const reply = json.choices[0].message.content;
    console.log(`${GREEN}✅ 成功！回复：${reply.slice(0, 60)}${RESET}`);
    return true;
  } catch (e) {
    console.log(`${RED}✗ ${e.message}${RESET}`);
    return false;
  }
}

console.log(`\n${'─'.repeat(55)}`);
console.log(`  测试模型：${MODEL}  图片格式探测`);
console.log(`${'─'.repeat(55)}\n`);

const formats = [
  // 格式 A：OpenAI 标准 image_url + data URL
  ['A: image_url + data URL', [{
    role: 'user',
    content: [
      { type: 'image_url', image_url: { url: DATA_URL } },
      { type: 'text', text: '这是什么颜色？' }
    ]
  }]],

  // 格式 B：OpenAI image_url + detail
  ['B: image_url + detail:low', [{
    role: 'user',
    content: [
      { type: 'image_url', image_url: { url: DATA_URL, detail: 'low' } },
      { type: 'text', text: '这是什么颜色？' }
    ]
  }]],

  // 格式 C：Anthropic 风格 base64
  ['C: image source base64 (Anthropic style)', [{
    role: 'user',
    content: [
      { type: 'image', source: { type: 'base64', media_type: 'image/png', data: TINY_PNG_B64 } },
      { type: 'text', text: '这是什么颜色？' }
    ]
  }]],

  // 格式 D：image_url 放文本内
  ['D: 文本内嵌 base64 URL', [{
    role: 'user',
    content: `请描述这张图片：${DATA_URL}`
  }]],

  // 格式 E：image_url 单独放 content（不加 text）
  ['E: 仅 image_url 无 text', [{
    role: 'user',
    content: [
      { type: 'image_url', image_url: { url: DATA_URL } }
    ]
  }]],

  // 格式 F：text 在前，image_url 在后
  ['F: text 在前，image_url 在后', [{
    role: 'user',
    content: [
      { type: 'text', text: '这是什么颜色？' },
      { type: 'image_url', image_url: { url: DATA_URL } }
    ]
  }]],
];

let found = null;
for (const [name, messages] of formats) {
  const ok = await tryFormat(name, messages);
  if (ok && !found) { found = name; }
  await new Promise(r => setTimeout(r, 300)); // 避免限速
}

console.log(`\n${'─'.repeat(55)}`);
if (found) {
  console.log(`${GREEN}✅ 可用格式：${found}${RESET}`);
} else {
  console.log(`${RED}❌ 所有格式均不支持图片输入${RESET}`);
}
console.log(`${'─'.repeat(55)}\n`);
