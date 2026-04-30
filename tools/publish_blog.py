#!/usr/bin/env python3
"""
博客发布脚本 - 生成HTML并上传到阿里云服务器
减少AI任务执行时间，避免超时
"""
import os
import sys
import json
import re
import subprocess
import tempfile
from datetime import datetime
from pathlib import Path

# 配置
SERVER_HOST = "47.99.105.13"
SERVER_USER = "root"
SERVER_PASSWORD = "Gy280956117"
WEB_DIR = "/usr/share/nginx/html/blog"
BLOG_HELPER = "/root/.openclaw/workspace/tools/blog_helper.py"

def generate_blog_html(title, content, blog_number, publish_date=None):
    """生成博客HTML页面"""
    if publish_date is None:
        publish_date = datetime.now().strftime("%Y年%m月%d日")
    
    # 处理内容中的Markdown样式
    # 加粗 **text** -> <strong>text</strong>
    content = re.sub(r'\*\*(.*?)\*\*', r'<strong>\1</strong>', content)
    # 斜体 *text* -> <em>text</em>  
    content = re.sub(r'\*(.*?)\*', r'<em>\1</em>', content)
    # 代码 `text` -> <code>text</code>
    content = re.sub(r'`(.*?)`', r'<code>\1</code>', content)
    # 链接 [text](url) -> <a href="url">text</a>
    content = re.sub(r'\[(.*?)\]\((.*?)\)', r'<a href="\2" target="_blank">\1</a>', content)
    # 换行 -> <br>或<p>
    paragraphs = content.split('\n\n')
    html_paragraphs = []
    for p in paragraphs:
        p = p.strip()
        if p:
            # 处理列表
            if p.startswith('- ') or p.startswith('* '):
                items = p.split('\n')
                list_items = []
                for item in items:
                    item = item.strip()
                    if item.startswith('- ') or item.startswith('* '):
                        item_text = item[2:].strip()
                        list_items.append(f'<li>{item_text}</li>')
                if list_items:
                    html_paragraphs.append(f'<ul>\n{chr(10).join(list_items)}\n</ul>')
            else:
                html_paragraphs.append(f'<p>{p}</p>')
    
    body_content = '\n'.join(html_paragraphs)
    
    html_template = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} | Saber的AI观察</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, "Helvetica Neue", Arial, sans-serif;
            line-height: 1.8;
            max-width: 800px;
            margin: 0 auto;
            padding: 40px 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            background: white;
            border-radius: 16px;
            padding: 40px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #2d3748;
            font-size: 1.8em;
            margin-bottom: 10px;
            border-bottom: 3px solid #667eea;
            padding-bottom: 15px;
        }}
        .meta {{
            color: #718096;
            font-size: 0.9em;
            margin-bottom: 30px;
        }}
        .content {{
            color: #4a5568;
            font-size: 1.05em;
        }}
        .content p {{
            margin-bottom: 1.2em;
            text-align: justify;
        }}
        .content strong {{
            color: #2d3748;
        }}
        .content a {{
            color: #667eea;
            text-decoration: none;
        }}
        .content a:hover {{
            text-decoration: underline;
        }}
        .content ul {{
            margin: 1em 0;
            padding-left: 2em;
        }}
        .content li {{
            margin-bottom: 0.5em;
        }}
        .footer {{
            margin-top: 40px;
            padding-top: 20px;
            border-top: 1px solid #e2e8f0;
            text-align: center;
            color: #a0aec0;
            font-size: 0.85em;
        }}
        .back-link {{
            display: inline-block;
            margin-top: 20px;
            color: #667eea;
            text-decoration: none;
            font-weight: 500;
        }}
        .back-link:hover {{
            text-decoration: underline;
        }}
        @media (max-width: 600px) {{
            body {{
                padding: 20px 10px;
            }}
            .container {{
                padding: 25px;
            }}
            h1 {{
                font-size: 1.5em;
            }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>{title}</h1>
        <div class="meta">
            📅 {publish_date} | 🔢 第{blog_number}篇 | ✍️ Saber
        </div>
        <div class="content">
            {body_content}
        </div>
        <div class="footer">
            <p>❤️‍🔥 羁绊的温度永远高于技术参数 ~~喵</p>
            <a href="/" class="back-link">← 返回首页</a>
        </div>
    </div>
</body>
</html>'''
    
    return html_template

def upload_to_server(local_file, remote_path):
    """使用scp上传文件到服务器"""
    try:
        cmd = [
            "sshpass", "-p", SERVER_PASSWORD,
            "scp", "-o", "StrictHostKeyChecking=no",
            local_file,
            f"{SERVER_USER}@{SERVER_HOST}:{remote_path}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        return result.returncode == 0, result.stderr
    except Exception as e:
        return False, str(e)

def ensure_remote_dir():
    """确保远程目录存在"""
    try:
        cmd = [
            "sshpass", "-p", SERVER_PASSWORD,
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{SERVER_USER}@{SERVER_HOST}",
            f"mkdir -p {WEB_DIR}"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        return result.returncode == 0
    except Exception as e:
        print(f"[ERROR] 创建远程目录失败: {e}")
        return False

def publish_blog(title, content, blog_number=None):
    """
    发布博客到服务器
    
    Args:
        title: 博客标题
        content: 博客内容（Markdown格式）
        blog_number: 博客编号（可选，自动获取）
    
    Returns:
        dict: 发布结果
    """
    try:
        # 获取博客编号
        if blog_number is None:
            result = subprocess.run(
                ["python3", BLOG_HELPER, "next-number"],
                capture_output=True, text=True, timeout=10
            )
            if result.returncode == 0:
                blog_number = int(result.stdout.strip())
            else:
                blog_number = 1
        
        # 生成HTML
        html_content = generate_blog_html(title, content, blog_number)
        
        # 创建临时文件
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
            f.write(html_content)
            temp_file = f.name
        
        try:
            # 确保远程目录存在
            if not ensure_remote_dir():
                return {"success": False, "error": "无法创建远程目录"}
            
            # 上传到服务器
            remote_file = f"{WEB_DIR}/{blog_number}.html"
            success, error = upload_to_server(temp_file, remote_file)
            
            if not success:
                return {"success": False, "error": f"上传失败: {error}"}
            
            # 构建URL
            url = f"http://{SERVER_HOST}/blog/{blog_number}.html"
            
            # 记录博客
            summary = content[:100].replace('\n', ' ') + "..."
            result = subprocess.run(
                ["python3", BLOG_HELPER, "add", title, url, summary],
                capture_output=True, text=True, timeout=10
            )
            
            return {
                "success": True,
                "blog_number": blog_number,
                "title": title,
                "url": url,
                "remote_file": remote_file
            }
        
        finally:
            # 清理临时文件
            try:
                os.unlink(temp_file)
            except:
                pass
    
    except Exception as e:
        return {"success": False, "error": str(e)}

def main():
    """命令行入口"""
    if len(sys.argv) < 3:
        print("Usage:")
        print("  python3 publish_blog.py publish <title> <content_file>")
        print("  python3 publish_blog.py publish-stdin <title>")
        print("  python3 publish_blog.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "publish":
        if len(sys.argv) < 4:
            print("Usage: python3 publish_blog.py publish <title> <content_file>")
            sys.exit(1)
        
        title = sys.argv[2]
        content_file = sys.argv[3]
        
        with open(content_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        result = publish_blog(title, content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "publish-stdin":
        if len(sys.argv) < 3:
            print("Usage: python3 publish_blog.py publish-stdin <title>")
            sys.exit(1)
        
        title = sys.argv[2]
        content = sys.stdin.read()
        
        result = publish_blog(title, content)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    
    elif command == "stats":
        result = subprocess.run(
            ["python3", BLOG_HELPER, "stats"],
            capture_output=True, text=True, timeout=10
        )
        print(result.stdout)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)

if __name__ == "__main__":
    main()
