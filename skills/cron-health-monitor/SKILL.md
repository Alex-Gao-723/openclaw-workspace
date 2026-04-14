# Cron Job Health Monitor

定时任务健康监控系统 - 实时监控 OpenClaw cron jobs 运行状态，及时发现并告警失败任务。

## 功能特性

- ✅ **实时监控**: 检查所有 cron job 的运行状态
- 🔴 **失败告警**: 检测连续失败的 job（默认3次）
- ⏰ **超时检测**: 检测长时间未运行的 job（默认25小时）
- 📧 **投递监控**: 监控消息投递失败情况
- 📊 **多格式输出**: 支持文本/JSON 格式报告
- 🔧 **修复建议**: 提供常见问题修复方案

## 安装

无需额外安装，Python 标准库即可运行。

## 使用方法

### 1. 查看完整健康报告

```bash
python3 /root/.openclaw/workspace/skills/cron-health-monitor/cron_health_monitor.py
```

输出示例：
```
============================================================
⏰ Cron Job 健康监控报告
生成时间: 2026-04-10 05:53:00
============================================================

📊 摘要:
   总任务数: 16
   ✅ 健康: 13
   ⚠️ 异常: 2
   🚫 禁用: 1

🔴 异常任务 (2个):

   [Daily Self-Improvement]
   ID: 09f529ab-a502-4dfd-8b80-ba912be2933c
   上次运行: 2026-04-09 13:53
   状态: error
   连续错误: 14 次
   🔴 [ERROR] 连续失败 14 次

💡 建议操作:
   • 检查 [Daily Self-Improvement] 的任务逻辑和超时设置
```

### 2. 仅告警模式（用于自动化脚本）

```bash
python3 /root/.openclaw/workspace/skills/cron-health-monitor/cron_health_monitor.py --alert
```

仅在有异常时输出，返回非零退出码。

### 3. JSON 格式输出

```bash
python3 /root/.openclaw/workspace/skills/cron-health-monitor/cron_health_monitor.py --json
```

便于与其他系统集成。

### 4. 查看修复建议

```bash
python3 /root/.openclaw/workspace/skills/cron-health-monitor/cron_health_monitor.py --fix-delivery
```

## 告警规则

| 规则 | 阈值 | 级别 |
|------|------|------|
| 连续失败 | ≥3 次 | ERROR |
| 长时间未运行 | >25 小时 | WARNING |
| 消息投递失败 | - | WARNING |
| Job 已禁用 | - | INFO |

## 作为 Python 模块使用

```python
from skills.cron-health-monitor.cron_health_monitor import (
    get_cron_jobs, analyze_job, generate_report
)

# 获取所有 jobs
jobs = get_cron_jobs()

# 分析单个 job
for job in jobs:
    analysis = analyze_job(job)
    if not analysis["is_healthy"]:
        print(f"Job {analysis['name']} 有异常!")
        for alert in analysis["alerts"]:
            print(f"  - {alert['message']}")

# 生成报告
report = generate_report([analyze_job(j) for j in jobs])
print(report)
```

## 集成到监控体系

### 方式1: 作为独立 cron job 定时检查

```bash
# 添加每小时检查一次
openclaw cron add \
  --name="Cron Health Check" \
  --schedule="0 * * * *" \
  --command="python3 /root/.openclaw/workspace/skills/cron-health-monitor/cron_health_monitor.py --alert"
```

### 方式2: 在每日报告任务中集成

在 `每日信息报告汇总` 任务中添加：

```python
import subprocess

# 运行健康检查
result = subprocess.run(
    ["python3", "/root/.openclaw/workspace/skills/cron-health-monitor/cron_health_monitor.py", "--alert"],
    capture_output=True,
    text=True
)

if result.returncode != 0:
    # 有异常，添加到报告中
    report += "\n\n⚠️ **定时任务告警**\n"
    report += result.stdout
```

## 故障排查

### Q: 为什么检测不到 cron jobs?
A: 确保 `openclaw cron list` 命令可以正常执行，且当前用户有权限。

### Q: 连续错误次数为什么不准确?
A: 依赖 OpenClaw 的 `consecutiveErrors` 字段，需要 OpenClaw 版本支持。

### Q: 如何修改告警阈值?
A: 修改脚本中的 `ALERT_CONSECUTIVE_ERRORS` 和 `ALERT_LAST_RUN_HOURS` 常量。

## 更新日志

### 2026-04-10
- ✅ 初始版本发布
- ✅ 支持基本健康检查
- ✅ 支持连续失败/超时/投递失败检测
- ✅ 支持文本/JSON 双格式输出

## 待办

- [ ] 支持自动修复常见配置问题
- [ ] 支持历史趋势分析
- [ ] 支持自定义告警规则
- [ ] 支持 Webhook 告警通知

---
*Created by Saber on 2026-04-10*
