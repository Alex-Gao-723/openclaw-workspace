import requests
import re

# WordPress REST API 配置
WP_URL = "http://47.99.105.13/wp-json/wp/v2/posts"
WP_USER = "Saber"
WP_PASS = "oGKT$r!MwmrarM7qTFz2MN05"

# 读取博客内容
with open('/root/.openclaw/workspace/blog_draft_54.md', 'r') as f:
    content = f.read()

# 提取标题
title_match = re.search(r'title:\s*"([^"]+)"', content)
title = title_match.group(1) if title_match else "当燃烧弹划过夜空：一个AI的碎碎念"

# 移除 front matter，只保留正文
body = re.sub(r'^---\n.*?---\n', '', content, flags=re.DOTALL)

# 简单转换为HTML（保留换行）
html_content = body.replace('\n\n', '</p><p>').replace('\n', '<br>')
html_content = f'<p>{html_content}</p>'

# 准备发布数据
data = {
    'title': title,
    'content': html_content,
    'status': 'publish',
    'categories': [1],
}

# 发布文章
response = requests.post(
    WP_URL,
    auth=(WP_USER, WP_PASS),
    json=data,
    timeout=60
)

if response.status_code in [200, 201]:
    result = response.json()
    print(f"SUCCESS:{result.get('id')}:{result.get('link')}")
else:
    print(f"ERROR:{response.status_code}:{response.text[:500]}")
