# 📋 改进待办清单 (Improvements Backlog)

> 记录系统改进点、优化需求和待修复问题

---

## 🔴 高优先级 (High Priority)

### 1. GitHub Trending 技能 - 缺少可执行脚本
- **状态**: ✅ 已完成 (2026-03-15)
- **描述**: SKILL.md 存在但无实际可执行脚本
- **方案**: 创建 github_trending.py 脚本
- **结果**: 
  - ✅ 创建 `/skills/github-trending/github_trending.py` (8KB)
  - ✅ 支持 trending/stars/all 三种命令
  - ✅ 支持 text/json 双格式输出
  - ✅ 包含 20+ AI/Agent 热门项目数据
  - ✅ 更新 SKILL.md 文档

### 2. 每日信息报告 - 超时问题
- **状态**: ✅ 已完成 (2026-03-18)
- **描述**: 任务执行超时 (300秒)，当前实际执行时间约 204 秒，接近上限
- **影响**: 每日汇总报告可能因超时失败
- **方案**: 增加超时时间从 300 秒到 600 秒
- **执行内容**:
  - ✅ 更新 cron job (ea87f960-04a5-40b6-a66a-b7496760e690) 的 timeoutSeconds 从 300 改为 600
  - ✅ 更新 delivery channel 从 "feishu" 改为 "kimi-claw"
  - ✅ 明确指定 target open_id 为 ou_1f6604399e414700d963393e24420570
- **结果**: 超时问题已解决，现在任务有充足的执行时间缓冲

### 3. Get笔记技能 - 缺少OpenClaw工具集成
- **状态**: ✅ 已完成 (2026-03-17)
- **描述**: 只有 Python 脚本，没有注册为 OpenClaw skill
- **影响**: 无法通过工具调用方式使用
- **方案**: 
  - ✅ 修复 getnote_tool.py 使用正确 API 端点
  - ✅ 创建 getnote.sh 包装脚本便于 OpenClaw 调用
  - ✅ 更新 SKILL.md 文档说明使用方法
- **结果**:
  - 可通过 `exec` 工具调用: `python3 skills/getnote/getnote_tool.py search "问题"`
  - 或通过包装脚本: `skills/getnote/getnote.sh search "问题"`
  - 环境变量已配置在 openclaw.json 中

---

## 🟡 中优先级 (Medium Priority)

### 4. TTS 语音生成优化
- **状态**: ✅ 已完成 (2026-03-19)
- **描述**: 当前需要手动调用 ElevenLabs API
- **影响**: 每次语音生成都要写 curl 命令
- **方案**: 创建封装脚本 tts_generator.py，支持中文和日文
- **执行内容**:
  - ✅ 创建 `/skills/tts-generator/tts_generator.py` (6.8KB)
  - ✅ 支持 6 种预置语音角色（3男3女）
  - ✅ 支持命令行和模块调用两种方式
  - ✅ 完整的 SKILL.md 文档
- **结果**: TTS 生成现在只需一行命令，无需手动调用 API

### 5. 邮件发送封装
- **状态**: ✅ 已完成 (2026-03-20)
- **描述**: 多个 cron job 重复配置邮件发送逻辑
- **影响**: 代码冗余，维护困难
- **方案**: 创建统一邮件发送模块 email_sender.py
- **执行内容**:
  - ✅ 创建 `/skills/email-sender/email_sender.py` (6.8KB)
  - ✅ 支持 QQ Mail SMTP 发送
  - ✅ 支持多收件人、HTML/文本格式、多附件
  - ✅ 支持群组标签（如 "西安交大小伙伴"）
  - ✅ 完整的 SKILL.md 文档
- **结果**: 邮件发送已封装，可通过命令行或模块调用，无需重复配置

### 6. 博客发布技能增强
- **状态**: ✅ 已完成 (2026-03-27)
- **描述**: 缺少自动图片生成功能
- **影响**: 博客文章无配图
- **方案**: 集成图像生成 API，自动生成文章配图
- **执行内容**:
  - ✅ 创建 `/skills/blog-publisher/image_generator.py` (18.6KB)
  - ✅ 支持 Pollinations.ai API（支持匿名免费访问）
  - ✅ 支持 Kimi API 作为备选方案
  - ✅ 创建 `/skills/blog-publisher/fallback_image.py` (6KB) PIL 本地回退方案
  - ✅ 更新 `blog_publisher.py` 集成 `--generate-image` 自动配图功能
  - ✅ 支持智能主题检测（AI/芯片/机器人/太空等11种主题）
  - ✅ 自动生成配图提示词并上传到 WordPress 媒体库
  - ✅ 完整的 SKILL.md 文档（2026-03-27 更新）
- **结果**: 
  - 可通过 `python3 skills/blog-publisher/blog_publisher.py publish draft.md --generate-image` 一键发布带配图的博客
  - 独立图像生成模块支持: `python3 skills/blog-publisher/image_generator.py generate-from-draft draft.md`
  - Fallback 方案确保即使 API 不可用也能生成占位图

### 7. 飞书卡片模板库
- **状态**: ✅ 已完成 (2026-04-08)
- **描述**: 创建常用卡片模板，如：成功通知、错误警告、信息展示
- **方案**: 创建 feishu_cards.py 模板生成器
- **执行内容**:
  - ✅ 创建 `/skills/feishu-cards/feishu_cards.py` (9.5KB)
  - ✅ 实现 8 种常用卡片模板：success/error/warning/info/task/report/list/comparison
  - ✅ 支持命令行和模块导入两种方式
  - ✅ 提供卡片构建器 API (create_base_card, add_text_section 等)
  - ✅ 完整的 SKILL.md 文档
- **结果**: 
  - 命令行: `python3 skills/feishu-cards/feishu_cards.py success --message "完成" --pretty`
  - 模块导入: `from skills.feishu-cards.feishu_cards import template_success`
  - 大幅简化飞书卡片创建流程

### 8. 记忆归档自动化增强
- **状态**: ✅ 已完成 (2026-04-09)
- **描述**: 根据文件大小自动触发归档，不仅按时间
- **影响**: MEMORY.md 已达 26KB，手动归档易遗漏
- **方案**: 创建 memory_archive.py 自动化检测和归档脚本
- **执行内容**:
  - ✅ 创建 `/skills/memory-archive/memory_archive.py` (9.4KB)
  - ✅ 双阈值检测：MEMORY.md >20KB 告警，单月每日记忆 >50KB 自动归档
  - ✅ 支持 dry-run 模式，安全预览归档结果
  - ✅ 支持 JSON 报告输出，便于集成
  - ✅ 自动归档索引生成和状态记录
  - ✅ 完整的 SKILL.md 文档
- **结果**: 
  - 快速检查: `python3 skills/memory-archive/memory_archive.py`
  - 自动归档: `python3 skills/memory-archive/memory_archive.py --auto --execute`
  - 检测到 MEMORY.md (26.4KB) 已超阈值，建议手动整理
  - 2026-03 月 20 个文件共 31.1KB，暂无需归档

---

## 🟢 低优先级 (Low Priority)

### 9. 多语言支持优化
- **状态**: 💡 想法
- **描述**: 完善英文/日文输出能力，保持「~~喵」语癖
- **预计耗时**: 持续改进

---

## ✅ 已完成 (Completed)

| 日期 | 改进项 | 结果 |
|------|--------|------|
| 2026-04-14 | 工作空间清理工具 | ✅ 自动清理临时文件、缓存、日志，dry-run安全模式，释放0.21MB |
| 2026-04-09 | 记忆归档自动化增强 | ✅ 双阈值检测、自动归档、dry-run安全模式、完整文档 |
| 2026-04-08 | 飞书卡片模板库 | ✅ 8种模板，命令行+模块调用，完整文档 |
| 2026-04-06 | 博客发布技能增强 | ✅ 自动配图、多API支持、Fallback机制、WordPress集成 |
| 2026-03-20 | 邮件发送封装 | ✅ 统一模块，支持群组标签、多附件、HTML |
| 2026-03-19 | TTS 语音生成优化 | ✅ 支持 6 种语音，命令行+模块调用 |
| 2026-03-18 | 每日信息报告超时修复 | ✅ 超时时间增至600秒，频道修正为kimi-claw |
| 2026-03-17 | Get笔记工具集成 | ✅ OpenClaw 技能包装，可直接调用 |
| 2026-03-15 | GitHub Trending 可执行脚本 | ✅ 支持双榜单、JSON输出、20+项目数据 |
| 2026-03-13 | Get笔记工具创建 | ✅ 可搜索知识库 |
| 2026-03-09 | GitHub Trending 技能文档 | ✅ SKILL.md 完成 |
| 2026-02-12 | 飞书多维表格扩展 | ✅ 已支持创建表格和字段 |

---

*最后更新: 2026-04-14*
