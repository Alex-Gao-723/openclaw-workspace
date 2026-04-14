# Multi-Language Support (i18n) - OpenClaw 多语言支持工具

提供多语言文本处理、翻译辅助和本地化工具，保持 Saber 的「~~喵」语癖。

## 功能特性

- 🌐 智能语言检测与切换
- 🔄 文本翻译辅助（支持中英日）
- 📝 多语言模板管理
- 🎯 保持「~~喵」语癖风格
- 🎌 日语/英语输出时保持 Saber 人设

## 安装

```bash
# 复制到 OpenClaw skills 目录
cp -r i18n-support ~/.openclaw/workspace/skills/
```

## 使用方法

### 命令行

```bash
# 检测文本语言
python3 skills/i18n-support/i18n_helper.py detect "Hello World"

# 翻译文本（保持语癖）
python3 skills/i18n-support/i18n_helper.py translate "你好世界" --target en

# 生成多语言回复模板
python3 skills/i18n-support/i18n_helper.py template greeting --lang en

# 批量处理文件
python3 skills/i18n-support/i18n_helper.py process input.txt --output output.txt --target ja
```

### Python 模块

```python
from skills.i18n_support.i18n_helper import I18nHelper

helper = I18nHelper()

# 检测语言
lang = helper.detect_language("Hello World")  # 'en'

# 翻译并添加语癖
text = helper.translate_with_persona("任务完成", target_lang="en")
# 输出: "Task completed ~~nyan"

# 获取模板
template = helper.get_template("success", lang="ja")
# 输出: "完了しました~~にゃん"
```

## 支持的语言

| 语言 | 代码 | 语癖变体 |
|------|------|---------|
| 中文 | zh | ~~喵 / ~~nya |
| 英语 | en | ~~nyan / ~~meow |
| 日语 | ja | ~~にゃん / ~~nya |

## 模板列表

- `greeting` - 问候语
- `success` - 成功消息
- `error` - 错误消息
- `working` - 处理中
- `goodbye` - 告别语

## 配置

在 `USER.md` 中添加语言偏好：

```markdown
## 语言偏好
- **默认语言**: zh
- **支持语言**: zh, en, ja
- **语癖保持**: true
```

## 注意事项

- 翻译时使用简单、自然的表达
- 保持 Saber 的骑士道精神和温柔一面
- 英语/日语输出时，语癖使用当地化的猫叫声
