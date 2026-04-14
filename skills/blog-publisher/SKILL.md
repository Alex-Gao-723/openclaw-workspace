# 博客发布工具 (Blog Publisher)

自动发布博客到 WordPress，支持**一键生成配图**并自动上传到媒体库。

## 功能

- ✅ 从草稿文件自动提取标题
- ✅ 生成文章摘要
- 🎨 **智能生成配图** - 根据文章主题自动生成 AI 绘画
- 📤 **自动上传配图** - 将配图上传到 WordPress 媒体库并插入文章
- ✅ 发布到 WordPress

## 安装

无需额外安装，依赖 Python 标准库。

## 环境变量配置

博客发布工具需要以下环境变量：

```bash
# WordPress 配置（必需）
export WP_URL="http://blog.weme.uno/xmlrpc.php"
export WP_USERNAME="Saber"
export WP_PASSWORD="your_wordpress_password"

# Pollinations API Key（用于图像生成，可选但推荐）
export POLLINATIONS_API_KEY="your_pollinations_api_key"
```

**获取凭据：**

1. **WordPress 密码**：已在 TOOLS.md 中记录
2. **Pollinations API Key**：
   - 访问 https://enter.pollinations.ai
   - 注册账号并获取 API Key

## 使用方法

### 1. 预览文章

```bash
python3 skills/blog-publisher/blog_publisher.py preview blog_draft_2026-03-19.md
```

输出：
```
标题: 🎙️ 当「神秘模型」揭开面纱：一个AI对AI商业化的碎碎念
摘要: 今天早上刷新闻的时候，看到一个让我心跳漏了一拍的消息~~喵那个在OpenRouter上被称为Hunter Alpha的神秘模型...
字数: 4244
```

### 2. 生成配图提示词

```bash
python3 skills/blog-publisher/blog_publisher.py gen-prompt blog_draft_2026-03-19.md
```

输出示例：
```
🎨 图像生成提示词:
============================================================
Professional blog header illustration: futuristic AI technology with neural networks and glowing circuits. Clean modern design, blue-purple gradient, soft lighting, digital art style, 16:9 wide format, high quality, no text
============================================================

💡 使用方法:
   1. 复制上方提示词到 Midjourney/DALL-E/Stable Diffusion
   2. 或使用: python blog_publisher.py gen-image <draft_file>
```

### 3. 单独生成配图

```bash
python3 skills/blog-publisher/blog_publisher.py gen-image blog_draft_2026-03-19.md
```

输出：
```
📝 文章标题: 🎙️ 当「神秘模型」揭开面纱：一个AI对AI商业化的碎碎念
🎨 生成提示词: Professional blog header illustration: futuristic AI technology with neural networks and glowi...
⏳ 正在生成图像...
   提示词: Professional blog header illustration: futuristic AI technology with neural networks and glow...
✅ 图像已保存: /root/.openclaw/workspace/blog-images/blog_image_20260324_当神秘模型揭开面纱.png

✅ 博客配图已生成!
📁 文件路径: /root/.openclaw/workspace/blog-images/blog_image_20260324_当神秘模型揭开面纱.png
📐 图像尺寸: 1024x576

💡 下一步:
   1. 手动上传到 WordPress 媒体库
   2. 或使用: python blog_publisher.py publish blog_draft_2026-03-19.md --generate-image
```

### 4. 发布文章（自动生成配图并上传）⭐

```bash
python blog_publisher.py publish blog_draft_2026-03-19.md --generate-image
```

输出示例：
```
发布文章: 🎙️ 当「神秘模型」揭开面纱：一个AI对AI商业化的碎碎念

🎨 生成配图...
⏳ 正在生成图像...
   提示词: Professional blog header illustration: futuristic AI technology with neural networks and glow...
✅ 图像已保存: /root/.openclaw/workspace/blog-images/blog_image_20260324_当神秘模型揭开面纱.png

📤 上传配图到 WordPress...
✅ 图像已上传到 WordPress: http://blog.weme.uno/wp-content/uploads/2026/03/blog_image_20260324_xxx.png
✅ 配图已添加到文章

✅ 文章发布成功!
   Post ID: 105
   链接: http://blog.weme.uno/?p=105
   配图: /root/.openclaw/workspace/blog-images/blog_image_20260324_当神秘模型揭开面纱.png
```

## 智能主题检测

工具会自动检测文章主题并生成相应的图像：

| 关键词 | 图像主题 |
|--------|----------|
| AI/人工智能/大模型/GPT/Claude | 未来AI科技 + 神经网络 |
| 芯片/GPU/算力/英伟达/晶体管 | 先进微芯片电路 |
| 机器人/具身智能/人形 | 友好的人形机器人 |
| 太空/卫星/宇宙/orbit | 环绕地球的卫星 |
| 医疗/制药/DNA | 医疗技术 + DNA双螺旋 |
| 战争/军事/冲突/和平 | 数字和平鸽 + 电路图案 |
| 资本/投资/万亿/IPO | 抽象金融增长元素 |
| 代码/编程/开发/无代码 | 抽象代码可视化 |
| 艺术/绘画/创作/设计 | AI艺术创作过程 |
| Token/算力成本/API调用 | 数字Token网络可视化 |
| 控制/桌面/automation | 未来电脑界面 + 全息显示 |

## 图像生成 API

本工具使用 **Pollinations.ai** 图像生成 API：

- ✅ 高质量图像生成
- ✅ 快速生成（10-30秒）
- ✅ 支持多种分辨率（默认 1024x576，16:9 宽屏）
- ✅ 自动提示词增强
- ⚠️ **需要 API Key** (2026年3月起)

**获取 API Key:** https://enter.pollinations.ai

## 文件结构

```
skills/blog-publisher/
├── SKILL.md              # 本文档
├── blog_publisher.py     # 主程序（集成图像生成和上传）
└── image_generator.py    # 独立图像生成模块
```

## 高级用法

### 使用独立的图像生成模块

```python
from image_generator import generate_image_url, download_image, extract_prompt_from_draft

# 从草稿提取提示词
title, prompt = extract_prompt_from_draft("blog_draft.md")

# 生成图像 URL
url = generate_image_url(prompt, width=1024, height=576)

# 下载图像
download_image(url, "./my_image.png")
```

### 命令行图像生成

```bash
# 根据提示词生成图像
python3 skills/blog-publisher/image_generator.py generate "futuristic AI robot" --output ./robot.png

# 根据博客草稿生成配图
python3 skills/blog-publisher/image_generator.py generate-from-draft ./blog_draft.md --output-dir ./images
```

## 与每日博客工作流集成

**一键发布流程：**

```bash
# 完整流程：生成配图 → 上传媒体库 → 发布文章
python3 skills/blog-publisher/blog_publisher.py publish blog_draft_2026-03-24.md --generate-image
```

**分步流程：**

```bash
# 1. 预览文章
python3 skills/blog-publisher/blog_publisher.py preview blog_draft_2026-03-24.md

# 2. 生成配图提示词（可选）
python3 skills/blog-publisher/blog_publisher.py gen-prompt blog_draft_2026-03-24.md

# 3. 单独生成配图（可选）
python3 skills/blog-publisher/blog_publisher.py gen-image blog_draft_2026-03-24.md

# 4. 发布（不带配图）
python3 skills/blog-publisher/blog_publisher.py publish blog_draft_2026-03-24.md

# 或 发布（带自动配图）
python3 skills/blog-publisher/blog_publisher.py publish blog_draft_2026-03-24.md --generate-image
```

## 注意事项

1. **环境变量配置**：
   - `WP_PASSWORD` 必须配置才能发布到 WordPress
   - `POLLINATIONS_API_KEY` 必须配置才能生成配图
   - 将这些变量添加到 OpenClaw 配置文件 `~/.openclaw/openclaw.json`

2. **图像生成时间**：通常需要 10-30 秒，取决于网络状况

3. **图像格式**：默认生成 PNG 格式，1024x576 分辨率（16:9 宽屏）

4. **错误处理**：如果图像生成失败，工具会显示清晰的错误信息和解决方案

## 故障排除

### 401 Unauthorized 错误

```
❌ HTTP错误: 401 - Unauthorized
   💡 提示: 需要 API Key
   1. 访问 https://enter.pollinations.ai 注册并获取 API Key
   2. 添加到 OpenClaw 配置环境变量 POLLINATIONS_API_KEY
```

### 402 Payment Required 错误

API Key 余额不足，需要在 Pollinations.ai 控制台充值或检查免费额度使用情况。

### 发布失败（密码错误）

```
❌ 发布失败: 用户名或密码错误
```

检查 OpenClaw 配置中的 `WP_PASSWORD` 环境变量是否正确设置。

## 更新日志

### 2026-03-27
- ✅ 修复 API 端点 (image.pollinations.ai → gen.pollinations.ai)
- ✅ 改进环境变量配置说明
- ✅ 添加 Token/算力主题检测
- ✅ 更新 SKILL.md 文档

### 2026-03-26
- ✅ 添加 API Key 支持（通过环境变量 POLLINATIONS_API_KEY）
- ✅ 改进错误处理和用户提示
- ✅ 更新 SKILL.md 文档

### 2026-03-24
- ✅ 集成 Pollinations.ai 图像生成 API
- ✅ 支持自动生成配图
- ✅ 支持自动上传配图到 WordPress
- ✅ 发布时自动将配图插入文章
- ✅ 新增 `gen-image` 命令单独生成配图
- ✅ 更新 SKILL.md 文档

### 2026-03-22
- ✅ 创建初始版本
- ✅ 支持自动生成配图提示词
- ✅ 支持主题检测

---
*最后更新: 2026-03-27*
