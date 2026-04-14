# Workspace Cleanup Tool - 工作空间清理工具

自动清理临时文件、旧日志、Python 缓存，保持工作空间整洁健康。

## 功能特性

- 🧹 **智能扫描**: 自动识别各类可清理文件
- 📊 **空间统计**: 计算可释放的磁盘空间
- 🛡️ **安全预览**: 默认 dry-run 模式，先预览再执行
- 🗂️  **分类清理**: 按文件类型设置不同保留策略
- 📈 **JSON 输出**: 支持程序化集成

## 安装

无需额外安装，直接使用：

```bash
# 复制到 skills 目录
cp -r workspace-cleanup ~/.openclaw/workspace/skills/
```

## 使用方法

### 1. 预览模式（默认）

查看哪些文件会被清理，不实际删除：

```bash
python3 /root/.openclaw/workspace/skills/workspace-cleanup/workspace_cleanup.py
```

### 2. 执行清理

确认无误后，执行实际清理：

```bash
python3 /root/.openclaw/workspace/skills/workspace-cleanup/workspace_cleanup.py --execute
```

### 3. JSON 格式输出

便于与其他工具集成：

```bash
python3 /root/.openclaw/workspace/skills/workspace-cleanup/workspace_cleanup.py --json
python3 /root/.openclaw/workspace/skills/workspace-cleanup/workspace_cleanup.py --execute --json
```

## 清理策略

| 类别 | 保留时间 | 说明 |
|------|----------|------|
| temp | 1 天 | /tmp/openclaw/*, *.tmp |
| logs | 7 天 | *.log, logs/* |
| cache | 3 天 | __pycache__, .pyc, .pytest_cache |
| drafts | 30 天 | blog_*_draft*.md |
| backups | 14 天 | backup/* |

## 报告示例

```
============================================================
🧹 工作空间清理报告
生成时间: 2026-04-14 05:50:00
============================================================

📋 模式: 预览 (dry-run)

📊 扫描结果:
   待清理文件: 45 个
   待清理目录: 12 个
   可释放空间: 156.3 MB

📁 待清理文件示例 (前10个):
   • temp_12345.jpg (2.5天, 1.2 MB)
   • debug.log (8.3天, 45 KB)
   • __pycache__/module.cpython-311.pyc (5.1天, 12 KB)
   ...
```

## 集成到定时任务

建议每周运行一次自动清理：

```bash
# 添加到 cron
openclaw cron add \
  --name="Weekly Workspace Cleanup" \
  --schedule="0 3 * * 0" \
  --command="python3 /root/.openclaw/workspace/skills/workspace-cleanup/workspace_cleanup.py --execute --json"
```

## Python 模块调用

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/workspace-cleanup')
from workspace_cleanup import CleanupResult, scan_workspace, execute_cleanup, generate_report

# 扫描
result = CleanupResult()
scan_workspace(result)

# 查看结果
print(f"可释放空间: {result.space_to_free} bytes")
print(f"待清理文件: {len(result.files_to_delete)} 个")

# 执行清理
execute_cleanup(result, dry_run=False)
print(f"已释放: {result.freed_space} bytes")
```

## 安全说明

- ✅ 默认 dry-run 模式，不会意外删除文件
- ✅ 按文件年龄智能判断，不会删除新文件
- ✅ 仅清理明确配置的目录和文件类型
- ⚠️ 执行前务必先预览确认

## 更新日志

### 2026-04-14
- ✅ 初始版本发布
- ✅ 支持5类文件清理策略
- ✅ 安全预览模式
- ✅ JSON 输出支持
- ✅ Python 模块调用支持

---
*Created by Saber on 2026-04-14*
