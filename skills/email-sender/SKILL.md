# Email Sender - 邮件发送模块

统一邮件发送模块，支持 QQ Mail SMTP，可发送给多人、HTML 内容、附件，支持群组标签快捷发送。

## 功能特点

- 📧 支持 QQ Mail SMTP 发送
- 👥 支持多收件人（逗号分隔）
- 🏷️ 支持群组标签（如 "西安交大小伙伴"）
- 📝 支持纯文本和 HTML 格式
- 📎 支持多附件
- 📋 支持抄送（CC）
- 🔒 SSL 加密传输

## 安装

无需安装，直接使用 Python 3 运行：

```bash
python3 skills/email-sender/email_sender.py [选项]
```

## 使用方法

### 1. 发送简单邮件

```bash
python3 skills/email-sender/email_sender.py \
  -t "recipient@example.com" \
  -s "邮件主题" \
  -b "这是邮件正文内容"
```

### 2. 发送给多人

```bash
python3 skills/email-sender/email_sender.py \
  -t "user1@qq.com,user2@gmail.com,user3@163.com" \
  -s "通知" \
  -b "大家好，这是群发邮件"
```

### 3. 发送 HTML 邮件

```bash
python3 skills/email-sender/email_sender.py \
  -t "recipient@example.com" \
  -s "HTML 邮件测试" \
  -b "<h1>Hello</h1><p>这是一封 <b>HTML</b> 邮件</p>" \
  --html
```

### 4. 发送带附件的邮件

```bash
python3 skills/email-sender/email_sender.py \
  -t "recipient@example.com" \
  -s "附件测试" \
  -b "请查收附件" \
  -a /path/to/document.pdf /path/to/image.png
```

### 5. 发送给群组

```bash
# 发送给 "西安交大小伙伴" 群组
python3 skills/email-sender/email_sender.py \
  -t "西安交大小伙伴" \
  -s "交大校友通知" \
  -b "大家好，这是一封群发邮件"
```

### 6. 查看可用群组

```bash
python3 skills/email-sender/email_sender.py --list-groups
```

输出：
```
============================================================
📋 可用联系人群组
============================================================

👥 西安交大小伙伴
   包含 4 个邮箱:
      • long.jin@audi.com.cn
      • pengjiang.shi@faw-vw.com
      • leiyy@oriza.com
      • wyd9836@163.com
```

## 作为模块调用

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/email-sender')
from email_sender import send_email, resolve_recipients

# 发送简单邮件
success, message = send_email(
    to_addresses="recipient@example.com",
    subject="测试邮件",
    body="这是邮件正文",
    body_type="plain"
)

# 发送 HTML 邮件
success, message = send_email(
    to_addresses=["user1@qq.com", "user2@gmail.com"],
    subject="HTML 测试",
    body="<h1>标题</h1><p>内容</p>",
    body_type="html",
    attachments=["/path/to/file.pdf"]
)

# 使用群组标签
recipients = resolve_recipients("西安交大小伙伴")
success, message = send_email(
    to_addresses=recipients,
    subject="群组邮件",
    body="大家好！"
)
```

## 命令行参数

```
必需参数:
  -t, --to        收件人地址（多个用逗号分隔，支持群组标签）
  -s, --subject   邮件主题
  -b, --body      邮件正文

可选参数:
  -h, --help      显示帮助信息
  --html          正文为 HTML 格式
  -a, --attach    附件路径（可指定多个）
  -c, --cc        抄送地址（多个用逗号分隔）
  --from-name     发件人显示名称（默认: Saber）
  --list-groups   列出所有可用联系人群组
```

## 邮件配置

当前配置（QQ Mail）：
- **SMTP 服务器**: smtp.qq.com:465 (SSL)
- **发件人邮箱**: 280956117@qq.com
- **认证方式**: 授权码

## 联系人群组

### 西安交大小伙伴
包含 4 个邮箱：
| 邮箱 | 备注 |
|------|------|
| long.jin@audi.com.cn | 奥迪 |
| pengjiang.shi@faw-vw.com | 一汽大众 |
| leiyy@oriza.com | - |
| wyd9836@163.com | - |

使用方式：`-t "西安交大小伙伴"`

## 故障排查

### SMTP 认证失败
- 检查授权码是否正确
- QQ Mail 需要使用授权码而非登录密码

### 收件人地址被拒绝
- 检查邮箱地址格式是否正确
- 确认收件人地址存在且可接收邮件

### 附件发送失败
- 检查文件路径是否正确
- 确认文件存在且有读取权限
- 单附件大小不能超过邮件服务商限制（QQ Mail 约 50MB）

## 更新日志

### 2026-03-20
- ✨ 初始版本发布
- 📧 支持 QQ Mail SMTP 发送
- 👥 支持群组标签快捷发送
- 📝 支持 HTML/纯文本双格式
- 📎 支持多附件上传
