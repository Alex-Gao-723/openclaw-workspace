# Message Delivery Wrapper

飞书/IM 消息发送的健壮封装，解决 cron job 中 "⚠️ ✉️ Message failed" 错误问题。

## 问题背景

多个定时任务（AI日报、每日汇总、录音卡分析等）频繁报告 `⚠️ ✉️ Message failed` 错误，即使消息实际已送达。此包装器提供：

- ✅ 自动重试机制（默认3次）
- ✅ 智能错误检测（区分真错误和误报）
- ✅ 超时保护（30秒上限）
- ✅ 详细的执行结果返回

## 使用方法

### 命令行

```bash
# 基本用法
python3 skills/message-wrapper/message_wrapper.py \
  "ou_1f6604399e414700d963393e24420570" \
  "消息内容" \
  --channel kimi-claw

# 从文件读取消息
python3 skills/message-wrapper/message_wrapper.py \
  "ou_1f6604399e414700d963393e24420570" \
  "@/path/to/message.txt" \
  --channel kimi-claw

# 增加重试次数
python3 skills/message-wrapper/message_wrapper.py \
  "ou_1f6604399e414700d963393e24420570" \
  "重要消息" \
  --retries 5

# 测试模式（不实际发送）
python3 skills/message-wrapper/message_wrapper.py \
  "ou_1f6604399e414700d963393e24420570" \
  "测试消息" \
  --dry-run
```

### Python 模块调用

```python
from skills.message-wrapper.message_wrapper import send_message, send_to_master

# 发送给指定用户
result = send_message(
    target="ou_1f6604399e414700d963393e24420570",
    message="Hello Master!",
    channel="kimi-claw",
    retries=3
)

if result["success"]:
    print(f"发送成功！尝试次数: {result['attempts']}")
else:
    print(f"发送失败: {result['error']}")

# 快捷发送给 Master
result = send_to_master("每日报告已生成~~喵 ⚔️")
```

## 返回值格式

```json
{
  "success": true,
  "message_id": "om_xxxxx",
  "error": null,
  "attempts": 1
}
```

## 在 Cron Job 中使用

替换原有的 `message` 工具调用：

```python
# 旧方式（易报错）
message(action="send", target="...", message="...")

# 新方式（健壮）
import subprocess
result = subprocess.run([
    "python3", 
    "/root/.openclaw/workspace/skills/message-wrapper/message_wrapper.py",
    "ou_1f6604399e414700d963393e24420570",
    "消息内容"
], capture_output=True, text=True)
```

## 技术细节

### 错误检测逻辑

包装器通过以下指标判断消息是否成功：

- ✅ 输出包含 "messageId"
- ✅ 输出包含 "delivered"（不区分大小写）
- ✅ 输出包含 "success"（不区分大小写）
- ✅ 返回码为 0

### 不重试的致命错误

以下情况不会重试：
- 用户 not found
- 参数 invalid
- 配置文件错误

## 更新日志

### 2026-04-18
- 初始版本
- 解决 5+ cron job 的 Message failed 问题
- 支持 kimi-claw 通道

## 相关任务

- 每日AI新闻推送 (6853b16b-aa08-427f-ae76-7f3cbc595072)
- 每日信息报告汇总 (ea87f960-04a5-40b6-a66a-b7496760e690)
- 每日录音卡笔记认知分析 (ceb993fa-76a0-443a-b597-176412efebb2)
- 每日自我改进任务 (09f529ab-a502-4dfd-8b80-ba912be2933c)
