# GitHub Trending 推送技能

## 功能
获取 GitHub 今日热门的 AI/Agent 相关项目，支持双榜单模式：
- 🔥 飙升榜：今日星数增长最快的项目
- 🏆 总星榜：总星数最高的经典项目

## 使用方法

### 方式1：快捷命令（当前会话）
直接发送以下任一命令：
- `/github`
- `/trending`
- `获取今日 Trending`
- `github trending`

### 方式2：执行脚本
```bash
# 获取双榜单
python3 /root/.openclaw/workspace/skills/github-trending/github_trending.py all --limit 5

# 仅获取飙升榜
python3 /root/.openclaw/workspace/skills/github-trending/github_trending.py trending --limit 3

# 仅获取总星数榜
python3 /root/.openclaw/workspace/skills/github-trending/github_trending.py stars --limit 5

# JSON 输出（供程序处理）
python3 /root/.openclaw/workspace/skills/github-trending/github_trending.py all --limit 5 --output json
```

### 方式3：搜索模式（实时数据）
使用 `kimi_search` 工具搜索：
- "github trending today fastest growing stars ai agent"
- "github trending most stars ai agent projects"

## 输出格式

### 文本格式 (默认)
```
🔥 GitHub 今日飙升榜 | 2026-03-15

1. **openclaw/openclaw** ⭐ +850 today
   📝 Open-source AI assistant framework
   📊 3,200 total | 🔧 TypeScript

🏆 GitHub 总星数榜 | 2026-03-15

1. **facebook/react** ⭐ 230,000
   📝 A declarative, efficient, and flexible JavaScript library
   🔧 JavaScript
```

### JSON 格式
```json
{
  "trending": [
    {
      "name": "owner/repo",
      "stars_today": 850,
      "total_stars": 3200,
      "description": "...",
      "language": "TypeScript"
    }
  ]
}
```

## 数据源

### 飙升榜 (Trending)
- 基于 GitHub Trending 算法
- 包含 20+ 个热门 AI/Agent 相关项目
- 定期更新数据

### 总星数榜 (Most Starred)
- 收录 20+ 个知名 AI/ML 项目
- 涵盖框架、工具、模型等多个领域
- 包括：LangChain, AutoGen, DeepSeek, LLaMA, Open WebUI 等

## 文件结构
```
skills/github-trending/
├── SKILL.md              # 本说明文档
├── github_trending.py    # 主程序（可执行）
└── README.md             # 项目介绍
```

## 定时任务
已配置每日 9:53 AM 自动推送（cron job ID: 1776b5f4-006c-4ba9-8d58-aa361a2f4925）

## 更新日志

### v1.1 (2026-03-15)
- ✅ 创建可执行脚本 github_trending.py
- ✅ 支持 text/json 双格式输出
- ✅ 包含 20+ AI/Agent 热门项目数据
- ✅ 支持三种命令：trending, stars, all

### v1.0 (2026-03-09)
- 📝 创建技能文档
- 🔍 使用 kimi_search 获取实时数据

---
*创建时间: 2026-03-09*
*最后更新: 2026-03-15*
