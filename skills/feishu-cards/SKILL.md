# Feishu Card Template Library

飞书卡片模板库 - 快速生成常用飞书消息卡片

## Overview

为 OpenClaw 提供标准化的飞书卡片生成功能，包含 8 种常用卡片模板，支持命令行和模块调用两种方式。

## Installation

无需安装，直接使用:
```bash
python3 skills/feishu-cards/feishu_cards.py [template] [options]
```

或作为模块导入:
```python
from skills.feishu-cards.feishu_cards import get_template, template_success
```

## Templates

### 1. Success Card (success)
操作成功通知

```bash
python3 skills/feishu-cards/feishu_cards.py success \
  --message "部署成功" \
  --details "版本 v1.2.3 已上线" \
  --pretty
```

### 2. Error Card (error)
错误警告

```bash
python3 skills/feishu-cards/feishu_cards.py error \
  --message "任务执行失败" \
  --details "连接超时" \
  --pretty
```

### 3. Warning Card (warning)
注意事项提醒

```bash
python3 skills/feishu-cards/feishu_cards.py warning \
  --message "磁盘空间不足" \
  --pretty
```

### 4. Info Card (info)
一般信息展示

```bash
python3 skills/feishu-cards/feishu_cards.py info \
  --title "系统通知" \
  --message "今日维护窗口: 02:00-04:00" \
  --pretty
```

### 5. Task Status Card (task)
任务状态更新

```bash
python3 skills/feishu-cards/feishu_cards.py task --pretty
# 输出示例任务状态卡片
```

### 6. Report Card (report)
报告类信息（多章节）

```bash
python3 skills/feishu-cards/feishu_cards.py report --pretty
```

### 7. List Card (list)
列表展示

```bash
python3 skills/feishu-cards/feishu_cards.py list --pretty
```

### 8. Comparison Card (comparison)
左右对比

```bash
python3 skills/feishu-cards/feishu_cards.py comparison --pretty
```

## Programmatic Usage

### Basic Example

```python
import json
from skills.feishu-cards.feishu_cards import template_success

# Generate card
card = template_success(
    message="备份完成",
    details="共备份 128 个文件，耗时 45 秒",
    action_text="查看详情",
    action_url="https://example.com/backup"
)

# Use in API call
card_json = json.dumps(card, ensure_ascii=False)
```

### Template Functions

```python
from skills.feishu-cards.feishu_cards import (
    template_success,
    template_error,
    template_warning,
    template_info,
    template_task_status,
    template_report,
    template_list,
    template_comparison,
    get_template  # Generic getter
)

# Direct function call
card = template_success(message="Done!")

# Or use generic getter
card = get_template("success", message="Done!")
```

## Card Builder API

Build cards programmatically:

```python
from skills.feishu-cards.feishu_cards import (
    create_base_card,
    add_text_section,
    add_note,
    add_divider,
    add_button
)

card = create_base_card("自定义卡片", "purple")
card = add_text_section(card, "**标题**\n正文内容")
card = add_divider(card)
card = add_button(card, "点击访问", "https://example.com")
card = add_note(card, "备注信息")
```

## Integration with Feishu API

Send generated cards via Feishu API:

```python
import requests
import json
from skills.feishu-cards.feishu_cards import template_success

# Generate card
card = template_success(message="Hello from Template Library!")

# Get Feishu token
token = "your_tenant_access_token"

# Send message
requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages",
    headers={"Authorization": f"Bearer {token}"},
    params={"receive_id_type": "open_id"},
    json={
        "receive_id": "user_open_id",
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
)
```

## Color Reference

| Template | Color | Usage |
|----------|-------|-------|
| success | green | Success notifications |
| error | red | Error alerts |
| warning | orange | Warnings |
| info | blue | General information |
| task (pending) | blue | Pending tasks |
| task (running) | turquoise | Running tasks |
| task (success) | green | Completed tasks |
| task (failed) | red | Failed tasks |
| report | purple | Reports |
| comparison | turquoise | Comparisons |

## File Structure

```
skills/feishu-cards/
├── feishu_cards.py    # Main script (9KB)
├── SKILL.md           # This documentation
└── examples/          # Usage examples (optional)
```

## Notes

- All templates support `wide_screen_mode` (enabled by default)
- Markdown support in text sections via `lark_md` tag
- Timestamps automatically added to success/error cards
- Module path: `skills.feishu-cards.feishu_cards`

## Changelog

- **2026-04-08**: Initial release with 8 templates
