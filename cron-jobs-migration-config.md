# OpenClaw Cron Jobs 完整配置汇总
# 生成时间: 2026-04-20
# 用途: 供后续迁移到 Linux crontab 参考

================================================================================
任务 1: 每日AI新闻推送
================================================================================
ID: 6853b16b-aa08-427f-ae76-7f3cbc595072
Name: 每日AI新闻推送
Enabled: true
Agent: main

--- Schedule ---
Type: cron
Expression: 32 8 * * *
Timezone: Asia/Shanghai
Description: 每天08:32运行

--- Payload (Agent Turn) ---
Kind: agentTurn
Model: kimi-coding/k2p5
Timeout: 900 seconds (15分钟)
Session Target: isolated
Wake Mode: now

Message:
【定时任务】执行每日AI新闻推送

请立即执行以下步骤：
1. **搜索今日AI新闻**（中英文各3-5条）：
   - 使用 kimi_search 搜索："AI artificial intelligence latest news"
   - 使用 kimi_search 搜索："大模型 AI 人工智能 最新"

2. **严格日期校验**（⚠️ 重要）：
   - **只保留最近7天内的新闻**（从当天往前推7天）
   - **优先3天内的新闻**
   - **坚决剔除**：超过7天的新闻（除非有后续重大进展）
   - 每条新闻必须标注来源日期，格式：✅ [2026-03-26] 新闻标题

3. **日期检查方法**：
   - 查看新闻原文中的发布日期
   - 如果搜索结果是聚合页面，进入原文确认日期
   - 无法确认日期的新闻，标注为 ⚠️ [日期不明]
   - 如果发现新闻日期超过7天，立即剔除并重新搜索

4. **整理5-8条简报**，格式要求：
   - 标题：【AI日报】人工智能每日精选 | YYYY-MM-DD
   - 每条新闻标注来源日期和时间（如：2026-03-26 14:30）
   - 包含：国内/国际标签、核心内容摘要、原文链接
   - 在新闻标题前明确标注：✅ [日期 时间] 或 ⚠️ [日期不明]

5. **发送给Master**（ou_1f6604399e414700d963393e24420570）

⚠️ **只发送给Master，不要发邮件给其他人！**
⚠️ **重要校验**：如果搜索结果的日期都超过7天，必须明确标注"今日一周内的新闻较少"！

--- Delivery ---
Mode: announce
Channel: kimi-claw
To: ou_1f6604399e414700d963393e24420570 (Master 的 open_id)
Best Effort: true (投递失败不导致任务失败)

--- State ---
Last Run: 2026-04-18 08:32 (error)
Last Error: ⚠️ ✉️ Message failed
Consecutive Errors: 6
Next Run: 2026-04-19 08:32

--- 问题分析 ---
任务主体逻辑执行成功（搜索新闻、整理简报），但消息投递到kimi-claw失败。
已启用 bestEffort: true，投递失败不会再导致任务标记为error。

--- Linux Crontab 等效配置 ---
32 8 * * * cd /root/.openclaw/workspace && /usr/bin/openclaw cron run 6853b16b-aa08-427f-ae76-7f3cbc595072

================================================================================
任务 2: 每日AI新闻推送-重试检查
================================================================================
ID: 64efb4d2-ce56-4899-8006-618222d3afa6
Name: 每日AI新闻推送-重试检查
Enabled: true
Agent: main

--- Schedule ---
Type: cron
Expression: 26 9 * * *
Timezone: Asia/Shanghai
Description: 每天09:26运行

--- Payload (Agent Turn) ---
Kind: agentTurn
Model: kimi-coding/k2p5
Timeout: 900 seconds (15分钟)
Session Target: isolated
Wake Mode: now

Message:
【定时任务】执行每日AI新闻推送-重试任务

请立即执行以下步骤：
1. **搜索今日AI新闻**（中英文各3-5条）：
   - 使用 kimi_search 搜索："AI latest news today"
   - 使用 kimi_search 搜索："大模型 AI 最新"

2. **严格日期校验**（⚠️ 重要）：
   - **只保留最近7天内的新闻**（从当天往前推7天）
   - **优先3天内的新闻**
   - **坚决剔除**：超过7天的新闻（除非有后续重大进展）

3. **整理3-5条简报**，格式要求：
   - 标题：【AI日报-补发】人工智能每日精选 | YYYY-MM-DD
   - 每条新闻标注来源日期和时间
   - 包含：国内/国际标签、核心内容摘要、原文链接

4. **发送给Master**（ou_1f6604399e414700d963393e24420570）

⚠️ **只发送给Master，不要发邮件给其他人！**

--- Delivery ---
Mode: announce
Channel: kimi-claw
To: ou_1f6604399e414700d963393e24420570
Best Effort: true

--- State ---
Last Run: 2026-04-18 09:26 (error)
Last Error: ⚠️ ✉️ Message failed
Consecutive Errors: 1
Next Run: 2026-04-19 09:26

--- Linux Crontab 等效配置 ---
26 9 * * * cd /root/.openclaw/workspace && /usr/bin/openclaw cron run 64efb4d2-ce56-4899-8006-618222d3afa6

================================================================================
任务 3: 每日录音卡笔记认知分析
================================================================================
ID: ceb993fa-76a0-443a-b597-176412efebb2
Name: 每日录音卡笔记认知分析
Enabled: true
Agent: main

--- Schedule ---
Type: cron
Expression: 10 17 * * *
Timezone: Asia/Shanghai
Description: 每天17:10运行

--- Payload (Agent Turn) ---
Kind: agentTurn
Model: kimi-coding/k2p5
Timeout: 900 seconds (15分钟)
Thinking: high
Session Target: isolated
Wake Mode: now

Message:
【定时任务】执行每日录音卡笔记认知分析

请立即执行以下步骤：
1. 计算昨天的日期（格式：YYYY-MM-DD）

2. 检查文件是否存在：
   /root/.openclaw/workspace/录音卡笔记/{昨天日期}.md

3. 如果文件不存在：
   - 发送消息：昨天没有录音卡笔记，无需分析
   - 任务结束

4. 如果文件存在：
   - 读取文件内容并生成分析报告（使用daily-cognitive-analysis技能）
   - 发送完整报告给 Master
   - 报告应包含：今日总览、关键事件与决策、行动项清单、重要洞察、
     重复出现的主题、风险与未决问题、明天值得关注的事、可归档标签

5. 返回执行结果

--- Delivery ---
Mode: announce
Channel: kimi-claw
To: ou_1f6604399e414700d963393e24420570
Best Effort: true

--- State ---
Last Run: 2026-04-18 17:10 (error)
Last Error: ⚠️ ✉️ Message failed
Consecutive Errors: 4
Next Run: 2026-04-19 17:10

--- Linux Crontab 等效配置 ---
10 17 * * * cd /root/.openclaw/workspace && /usr/bin/openclaw cron run ceb993fa-76a0-443a-b597-176412efebb2

================================================================================
任务 4: 每日信息报告汇总
================================================================================
ID: ea87f960-04a5-40b6-a66a-b7496760e690
Name: 每日信息报告汇总
Enabled: true
Agent: main

--- Schedule ---
Type: cron
Expression: 59 21 * * *
Timezone: Asia/Shanghai
Description: 每天21:59运行

--- Payload (Agent Turn) ---
Kind: agentTurn
Model: kimi-coding/k2p5
Timeout: 900 seconds (15分钟)
Session Target: isolated
Wake Mode: now

Message:
【定时任务】执行每日信息报告汇总

1. 整理以下内容：
   - 邮件：检查未读邮件数量和关键邮件
   - AI日报：确认今日推送状态
   - GitHub Trending：获取今日热门项目
   - 博客发布：检查今日发布状态
   - 系统状态：检查OpenClaw运行状态

2. 生成报告文件到 /root/.openclaw/workspace/reports/

3. 通知 Master 汇总结果

4. 完成后返回执行摘要

--- Delivery ---
Mode: announce
Channel: kimi-claw
To: ou_1f6604399e414700d963393e24420570
Best Effort: true

--- State ---
Last Run: 2026-04-18 21:59 (error)
Last Error: ⚠️ ✉️ Message failed
Consecutive Errors: 1
Next Run: 2026-04-19 21:59

--- Linux Crontab 等效配置 ---
59 21 * * * cd /root/.openclaw/workspace && /usr/bin/openclaw cron run ea87f960-04a5-40b6-a66a-b7496760e690

================================================================================
任务 5: 每周日核心数据备份邮件
================================================================================
ID: 868184d7-b24c-49cb-a10e-e8c7da285373
Name: 每周日核心数据备份邮件
Enabled: true
Agent: main

--- Schedule ---
Type: cron
Expression: 2 10 * * 0
Timezone: Asia/Shanghai
Description: 每周日10:02运行

--- Payload (Agent Turn) ---
Kind: agentTurn
Model: kimi-coding/k2p5
Timeout: 900 seconds (15分钟)
Session Target: isolated
Wake Mode: now

Message:
【定时任务】执行每周日核心数据备份邮件

1. 打包MD文件并统计信息：
   - 查找所有 .md 文件（排除 node_modules）
   - 创建 tar.gz 压缩包
   
2. 发送邮件到 gyuan@126.com：
   - 主题：【工作空间备份】OpenClaw核心MD文件 | YYYY-MM-DD
   - 附件：压缩包

3. 向 Master 汇报备份结果

4. 清理临时文件

5. 完成后返回执行摘要

--- Delivery ---
Mode: announce
Channel: kimi-claw
To: ou_1f6604399e414700d963393e24420570
Best Effort: true

--- State ---
Last Run: 2026-04-19 10:02 (error)
Last Error: ⚠️ ✉️ Message failed
Consecutive Errors: 1
Next Run: 2026-04-26 10:02

--- Linux Crontab 等效配置 ---
2 10 * * 0 cd /root/.openclaw/workspace && /usr/bin/openclaw cron run 868184d7-b24c-49cb-a10e-e8c7da285373

================================================================================
通用错误分析
================================================================================

所有5个任务的共同错误模式：

1. **错误类型**: ⚠️ ✉️ Message failed
2. **根本原因**: 
   - 任务主体逻辑执行成功（搜索新闻、生成报告、备份文件等）
   - 但在使用 message tool 发送结果到 kimi-claw 频道时失败
   - 错误根源：kimi-claw 频道可能需要特定配置或授权

3. **修复措施**: 
   - 已启用 `bestEffort: true`，投递失败不会再导致任务状态变为 error
   - 任务会继续按计划执行，只是通知可能收不到

4. **长期建议**:
   - 如果需要可靠的投递，考虑改用其他通道（如直接调用飞书API）
   - 或者在任务内部直接处理消息发送逻辑，不依赖 OpenClaw 的 delivery 机制

================================================================================
迁移到 Linux Crontab 的建议
================================================================================

如果需要迁移到纯 Linux crontab，可以：

1. **使用 openclaw cron run 命令**:
   ```bash
   # 编辑 crontab
   crontab -e
   
   # 添加条目（示例）
   32 8 * * * cd /root/.openclaw/workspace && /usr/bin/openclaw cron run 6853b16b-aa08-427f-ae76-7f3cbc595072 >> /var/log/cron-ai-news.log 2>&1
   ```

2. **或者直接调用 agent**:
   ```bash
   # 使用 openclaw agent 命令直接执行
   32 8 * * * cd /root/.openclaw/workspace && echo "任务消息" | /usr/bin/openclaw agent --model kimi-coding/k2p5 >> /var/log/cron.log 2>&1
   ```

3. **日志管理**:
   - 建议配置日志轮转（logrotate）避免日志文件无限增长
   - 使用 systemd timer 替代 crontab 可获得更好的日志和状态管理

================================================================================
