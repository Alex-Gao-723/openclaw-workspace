# OpenClaw Workspace

本仓库用于备份和版本管理 OpenClaw AI Agent 的工作空间内容。

## 目录结构

| 目录 | 说明 |
|------|------|
| `memory/` | 每日记忆和长期笔记 |
| `录音卡笔记/` | 语音记录的分析和整理 |
| `reports/` | 各类分析报告和日报 |
| `notes/` | 零散笔记和知识整理 |
| `skills/` | 自定义技能文档（SKILL.md）|
| `crm-system/` | CRM 项目文档 |
| `jeju-trip/` | 旅行计划文档 |
| `design_assets/` | 设计资源说明 |

## 根目录核心文件

- `SOUL.md` — AI 人格定义
- `AGENTS.md` — 工作空间规则
- `TOOLS.md` — 工具配置和凭证引用
- `USER.md` — 用户信息
- `MEMORY.md` — 长期记忆
- `IDENTITY.md` — 身份设定
- `HEARTBEAT.md` — 定时任务配置
- `improvements.md` — 改进计划
- `next.md` — 下一步行动

## 安全说明

- 所有敏感凭证（Token、密码、API Key）均引用环境变量，不直接存储
- 仓库中不包含任何 node_modules 或依赖目录

## 自动同步

每周四 20:00 自动同步到 GitHub。
