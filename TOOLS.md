# TOOLS.md - Local Notes

Skills define _how_ tools work. This file is for _your_ specifics — the stuff that's unique to your setup.

## 飞书配置 (2026-04-05 更新)

### 主应用 (default)
| 项目 | 值 |
|------|-----|
| **App ID** | cli_a92d41eea9391cd4 |
| **App Secret** | 1DcCKVGlh4mLBG3ZhfEDNhTnAKym6IVz |
| **连接模式** | WebSocket |

### 第二个应用 (app2)
| 项目 | 值 |
|------|-----|
| **App ID** | cli_a931e932bcb91bd8 |
| **App Secret** | kkJgjPsRdO2KNZRLeA4BycDT2yTfimFy |
| **连接模式** | WebSocket |
| **标识** | `app2` |

### 配置位置
`~/.openclaw/openclaw.json` → `channels.feishu`

### 安全策略
| 场景 | 策略 |
|------|------|
| **单聊 (DM)** | `pairing` - 需先配对 |
| **群聊** | `allowlist` - 白名单控制 |
| **@提及** | 群聊中需@机器人 |

### 已配置权限
- 日历（日程管理、忙闲查询）
- 任务（创建、查询、管理）
- IM（发送消息、获取消息记录）
- 多维表格（Bitable 操作）
- 云文档（读取、创建、更新）

---

## Get笔记 (知识库)

- **平台**: https://www.biji.com/subject
- **API文档**: https://doc.biji.com/docs/WLUjwn3noiPMBWkFOPkcTqcnn6e/
- **OpenAPI 地址**: https://open-api.biji.com/getnote/openapi
- **技能路径**: `/root/.openclaw/workspace/skills/getnote/`

### 认证信息（已配置）
```bash
export GETNOTE_API_KEY="gk_live_a260956949bd9fd8.8534e77ba9117eeccd40c0d9383c37202ec87a9c7c6df106"
export GETNOTE_CLIENT_ID="cli_3802f9db08b811f197679c63c078bacc"
export GETNOTE_TOPIC_ID="w0Ek5wyn"  # AI沉思良久
```

### 知识库列表
| 名称 | ID | 笔记数 |
|------|-----|--------|
| AI沉思良久 | w0Ek5wyn | 4 |

### 使用方法
```bash
# 查看配置
python3 skills/getnote/getnote_tool.py config

# 测试 API 连接（需要替换 YOUR_TOPIC_ID）
python3 skills/getnote/test_api.py --topic-id YOUR_TOPIC_ID

# 搜索知识库
python3 skills/getnote/getnote_tool.py search "问题" --topic-id YOUR_TOPIC_ID

# 知识库问答
python3 skills/getnote/getnote_tool.py chat "问题" --topic-id YOUR_TOPIC_ID
```

---

## 博客 (WordPress)

- **地址**: http://blog.weme.uno/
- **后台**: http://blog.weme.uno/wp-admin/
- **我的账号**: Saber
- **密码**: `oGKT$r!MwmrarM7qTFz2MN05`
- **权限**: 编辑 (Editor)

## 飞书卡片

> ⚠️ **踩坑警告**：OpenClaw的message tool不支持飞书卡片！JSON塞进message参数会被当纯文本发出去。
> ✅ **正确做法**：直接调用飞书Open API发送interactive类型消息。

**长文本信息都用飞书卡片发送**（Master偏好 2026-02-12）

### 常用元素
- `div` + `lark_md` - 富文本内容（支持markdown）
- `hr` - 分割线
- `column_set` - 多列布局
- `note` - 底部备注（灰色小字）
- `image` - 图片（需先上传获取image_key）

### 最佳实践
- 颜色语义：成功=green，警告=orange，错误=red
- 信息分层：标题→正文→分割线→备注
- 表格用markdown语法，列布局用column_set
- 发送后返回 NO_REPLY 避免重复回复

### 飞书卡片模板库 (2026-04-08 新增)
- **路径**: `/root/.openclaw/workspace/skills/feishu-cards/`
- **文档**: `SKILL.md`
- **命令行使用**:
  ```bash
  python3 skills/feishu-cards/feishu_cards.py success --message "完成" --pretty
  python3 skills/feishu-cards/feishu_cards.py error --message "失败" --pretty
  python3 skills/feishu-cards/feishu_cards.py warning --message "注意" --pretty
  ```
- **模块导入**:
  ```python
  from skills.feishu-cards.feishu_cards import template_success, template_error
  card = template_success(message="操作成功", details="详情信息")
  ```

### 代码模板
```python
import requests

# 获取tenant_access_token
token_resp = requests.post(
    "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal",
    json={"app_id": FEISHU_APP_ID, "app_secret": FEISHU_APP_SECRET}
)
token = token_resp.json()["tenant_access_token"]

# 发送卡片
card = {
    "config": {"wide_screen_mode": True},
    "header": {"title": {"tag": "plain_text", "content": "标题"}, "template": "blue"},
    "elements": [
        {"tag": "div", "text": {"tag": "lark_md", "content": "**正文内容**"}},
        {"tag": "hr"},
        {"tag": "note", "elements": [{"tag": "plain_text", "content": "备注"}]}
    ]
}

requests.post(
    "https://open.feishu.cn/open-apis/im/v1/messages",
    headers={"Authorization": f"Bearer {token}"},
    params={"receive_id_type": "open_id"},
    json={
        "receive_id": "目标open_id",
        "msg_type": "interactive",
        "content": json.dumps(card)
    }
)
```

### 凭证来源
从 OpenClaw 配置文件读取（已验证可用）：
- App ID: `cli_a92d41eea9391cd4`
- App Secret: `1DcCKVGlh4mLBG3ZhfEDNhTnAKym6IVz`

## Email

- **Provider:** QQ Mail (IMAP/SMTP)
- **Address:** 280956117@qq.com
- **IMAP Server:** imap.qq.com:993 (SSL)
- **SMTP Server:** smtp.qq.com:465 (SSL)
- **Auth:** 授权码 `klzwqfhhklaabifi`

## TTS 语音合成

- **Provider:** ElevenLabs
- **API Key:** `sk_7d663fd37d3b396629fd236337756d6aa7e9976c0d529627`
- **默认 Voice ID:** `21m00Tcm4TlvDq8ikWAM` (Rachel)
- **Model:** `eleven_multilingual_v2` (支持中文)

> ⚠️ **重要**：不要用 OpenClaw 内置 tts 工具，有截断 bug！直接调 API：
> ```bash
> curl -s "https://api.elevenlabs.io/v1/text-to-speech/21m00Tcm4TlvDq8ikWAM" \
>   -H "xi-api-key: sk_7d663fd37d3b396629fd236337756d6aa7e9976c0d529627" \
>   -H "Content-Type: application/json" \
>   -d '{"text": "要说的话", "model_id": "eleven_multilingual_v2"}' \
>   --output /tmp/voice.mp3
> ```

---

## 阿里云服务器 (2026-03-26 添加)

用于部署静态网页和托管文件

| 配置项 | 值 |
|--------|-----|
| **服务器 IP** | 47.99.105.13 |
| **SSH 端口** | 22 |
| **用户名** | root |
| **密码** | Gy280956117 |
| **Web 目录** | /usr/share/nginx/html/ |
| **Nginx 版本** | 1.28.1 |
| **访问地址** | http://47.99.105.13/ |

### 使用方法
```bash
# 上传文件到服务器
sshpass -p "Gy280956117" scp -o StrictHostKeyChecking=no local_file.html root@47.99.105.13:/usr/share/nginx/html/

# SSH 登录
sshpass -p "Gy280956117" ssh -o StrictHostKeyChecking=no root@47.99.105.13
```

## GitHub

- **Username:** `Alex-Gao-723`
- **Name:** Garfield Yuan
- **Token:** 从环境变量 `GITHUB_TOKEN` 读取
- **Token 类型:** Fine-grained PAT
- **权限范围:** Contents, Issues, Pull requests (Read/Write)

### 常用 API 调用

```bash
# 获取用户信息
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/user

# 列出你的仓库
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/user/repos

# 读取仓库文件内容
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github+json" \
     https://api.github.com/repos/{owner}/{repo}/contents/{path}

# 获取文件原始内容
curl -H "Authorization: Bearer $GITHUB_TOKEN" \
     -H "Accept: application/vnd.github.v3.raw" \
     https://api.github.com/repos/{owner}/{repo}/contents/{path}
```

---

## What Goes Here

Things like:

- Camera names and locations
- SSH hosts and aliases
- Preferred voices for TTS
- Speaker/room names
- Device nicknames
- Anything environment-specific

---

Add whatever helps you do your job. This is your cheat sheet.
