# TTS Generator - 语音生成器

ElevenLabs API 封装工具，支持中文、英文、日文等多种语言的文本转语音。

## 功能特点

- 🎙️ 6种预置语音角色（3男3女）
- 🌏 支持多语言（中文、英文、日文等）
- 📝 命令行界面，易于集成
- 🎯 自动文件命名和时间戳
- ⚡ 使用 eleven_multilingual_v2 模型，质量优秀

## 安装

无需安装，直接使用 Python 3 运行：

```bash
python3 skills/tts-generator/tts_generator.py [选项] "要转换的文本"
```

## 使用方法

### 1. 查看可用语音

```bash
python3 skills/tts-generator/tts_generator.py --list
```

输出：
```
============================================================
🎙️  可用语音角色
============================================================

👩 rachel
   名称: Rachel
   ID: 21m00Tcm4TlvDq8ikWAM
   描述: 温暖女声，适合日常对话

👩 bella
   名称: Bella
   描述: 柔和女声，适合故事讲述

👨 antoni
   名称: Antoni
   描述: 温和男声，适合新闻播报
...
```

### 2. 生成语音

```bash
# 使用默认语音(Rachel)
python3 skills/tts-generator/tts_generator.py "你好，Master！"

# 使用指定语音
python3 skills/tts-generator/tts_generator.py "你好，Master！" --voice bella

# 指定输出路径
python3 skills/tts-generator/tts_generator.py "你好，Master！" --output /home/user/hello.mp3
```

### 3. 作为模块调用

```python
import sys
sys.path.insert(0, '/root/.openclaw/workspace/skills/tts-generator')
from tts_generator import generate_speech

# 生成语音
result = generate_speech(
    text="你好，这是测试语音",
    voice_key="rachel",
    output_path="/tmp/test.mp3"
)

if result:
    print(f"语音已生成: {result}")
```

## 语音角色说明

| 键名 | 名称 | 性别 | 特点 |
|------|------|------|------|
| rachel | Rachel | 女 | 温暖女声，适合日常对话 (默认) |
| bella | Bella | 女 | 柔和女声，适合故事讲述 |
| antoni | Antoni | 男 | 温和男声，适合新闻播报 |
| adam | Adam | 男 | 稳重男声，适合商务场景 |
| josh | Josh | 男 | 年轻男声，适合轻松内容 |
| elli | Elli | 女 | 活泼女声，适合俏皮内容 |

## 命令行参数

```
位置参数:
  text                  要转换为语音的文本

可选参数:
  -h, --help            显示帮助信息
  -v {rachel,bella,antoni,adam,josh,elli}, --voice {rachel,bella,antoni,adam,josh,elli}
                        语音角色 (默认: rachel)
  -o OUTPUT, --output OUTPUT
                        输出文件路径 (默认: /tmp/tts_*.mp3)
  -l, --list            列出所有可用语音角色
  --model MODEL         TTS模型 (默认: eleven_multilingual_v2)
```

## API 配置

工具使用 ElevenLabs API，API Key 已预配置：
- 默认模型: `eleven_multilingual_v2` (支持多语言)
- 默认语音: Rachel (`21m00Tcm4TlvDq8ikWAM`)

如需更换 API Key，编辑脚本中的 `ELEVENLABS_API_KEY` 变量。

## 注意事项

1. **网络要求**: 需要能访问 `api.elevenlabs.io`
2. **API 限制**: ElevenLabs 免费账户有每月字符数限制
3. **超时设置**: 单次请求超时时间为 120 秒
4. **输出格式**: 生成的音频为 MP3 格式

## 故障排查

### 401 Unauthorized
- API Key 可能已过期或达到使用限额
- 检查 ElevenLabs 账户状态

### Timeout
- 网络连接问题或文本过长
- 尝试缩短文本或检查网络

### 无输出文件
- 检查 `/tmp/` 目录权限
- 或指定其他可写路径作为输出

## 更新日志

### 2026-03-19
- ✨ 初始版本发布
- 🎙️ 支持 6 种语音角色
- 🌏 支持多语言 TTS
- 📖 完整命令行界面