# Memory Archive Skill

自动检测并归档过大的记忆文件，基于文件大小和时间双维度触发。

## 功能特性

- 📊 **智能检测**: 监控 MEMORY.md 和每日记忆文件大小
- 🗂️ **自动归档**: 按月归档历史记忆文件
- 📈 **阈值配置**: 可自定义归档触发阈值
- 📝 **详细报告**: JSON 格式报告，便于集成
- 🧪 **安全测试**: 支持 dry-run 模式，先预览再执行

## 安装

```bash
# 确保脚本可执行
chmod +x /root/.openclaw/workspace/skills/memory-archive/memory_archive.py
```

## 使用方法

### 1. 快速检查（默认）

显示当前记忆文件状态和建议：

```bash
python3 skills/memory-archive/memory_archive.py
```

### 2. 生成详细报告

```bash
python3 skills/memory-archive/memory_archive.py --report
# 或
python3 skills/memory-archive/memory_archive.py --check
```

### 3. 自动归档（Dry Run）

预览哪些月份会被归档：

```bash
python3 skills/memory-archive/memory_archive.py --auto
```

### 4. 实际执行归档

```bash
python3 skills/memory-archive/memory_archive.py --auto --execute
```

### 5. 归档指定月份

```bash
# Dry run
python3 skills/memory-archive/memory_archive.py --archive 2026-03

# 实际执行
python3 skills/memory-archive/memory_archive.py --archive 2026-03 --execute
```

## 配置阈值

编辑脚本中的配置常量：

```python
MEMORY_MD_THRESHOLD = 20 * 1024      # MEMORY.md 超过20KB建议归档
DAILY_TOTAL_THRESHOLD = 50 * 1024    # 单月每日记忆超过50KB自动归档
ARCHIVE_AGE_DAYS = 30                # 超过30天的文件考虑归档
```

## 输出示例

### 快速检查模式

```
📊 Memory Archive Report
========================

📄 MEMORY.md Status:
   大小: 26.4KB ⚠️ 需要关注
   阈值: 20.0KB

📁 Monthly Daily Files:
   2026-03: 35.2KB (15 files) ⚠️ 建议归档
   2026-04: 12.8KB (8 files) ✅ (当前月)

💡 Recommendations:
   🔴 MEMORY.md (26.4KB) 超过阈值 (20.0KB)，建议手动整理归档
   🟡 2026-03 月每日记忆 (35.2KB) 超过阈值，建议归档 (15 个文件)
```

### JSON 报告模式

```json
{
  "timestamp": "2026-04-09T05:55:00",
  "memory_md": {
    "file": "/root/.openclaw/workspace/MEMORY.md",
    "size": 26984,
    "formatted_size": "26.4KB",
    "needs_archive": true,
    "threshold": 20480
  },
  "monthly_files": [...],
  "recommendations": [...]
}
```

## 归档结构

归档后文件结构：

```
memory/
├── 2026-04-08.md          # 当前月文件保留
├── 2026-04-09.md
├── archives/
│   └── 2026-03/           # 按月归档
│       ├── 2026-03-05.md
│       ├── 2026-03-07.md
│       └── _archive_index.json
└── archive_state.json     # 归档状态记录
```

## 集成到 Heartbeat

在 `HEARTBEAT.md` 中添加：

```markdown
## 每周任务（周一执行）

- [ ] 检查记忆归档状态
  ```bash
  python3 skills/memory-archive/memory_archive.py --auto --execute
  ```
```

## 注意事项

1. **当前月文件**: 不会自动归档当前月的文件，即使超过阈值
2. **dry-run 默认**: 所有命令默认 dry-run，需加 `--execute` 才实际执行
3. **归档索引**: 每个归档目录包含 `_archive_index.json` 索引文件
4. **状态记录**: `archive_state.json` 记录归档历史

## 更新日志

- **2026-04-09**: 初始版本，支持大小检测和自动归档
