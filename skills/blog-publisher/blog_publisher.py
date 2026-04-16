#!/usr/bin/env python3
"""
博客发布工具 - 自动发布博客到 WordPress，支持一键生成配图
"""
import os
import sys
import argparse
from datetime import datetime

# WordPress XML-RPC
import xmlrpc.client


def get_wordpress_client():
    """获取 WordPress XML-RPC 客户端"""
    wp_url = os.environ.get("WP_URL", "http://blog.weme.uno/xmlrpc.php")
    wp_username = os.environ.get("WP_USERNAME", "Saber")
    wp_password = os.environ.get("WP_PASSWORD", "")
    
    if not wp_password:
        print("❌ 错误: WP_PASSWORD 环境变量未设置")
        print("💡 请在 OpenClaw 配置中设置 WP_PASSWORD")
        sys.exit(1)
    
    server = xmlrpc.client.ServerProxy(wp_url)
    return server, wp_username, wp_password


def extract_title_from_content(content):
    """从 Markdown 内容中提取标题"""
    lines = content.split('\n')
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            return line[2:].strip()
        elif line.startswith('## '):
            return line[3:].strip()
    return "Untitled"


def extract_summary(content, max_length=200):
    """提取文章摘要"""
    # 移除 Markdown 标记
    import re
    text = re.sub(r'[#*`_\[\]\(\)]', '', content)
    text = re.sub(r'\s+', ' ', text).strip()
    
    if len(text) <= max_length:
        return text
    return text[:max_length] + "..."


def detect_theme(title):
    """检测文章主题并返回图像提示词"""
    title_lower = title.lower()
    
    themes = {
        'ai': ['ai', '人工智能', '大模型', 'gpt', 'claude', 'llm', '神经网络'],
        'chip': ['芯片', 'gpu', '算力', '英伟达', 'nvidia', '晶体管'],
        'robot': ['机器人', '具身智能', '人形', 'robot'],
        'space': ['太空', '卫星', '宇宙', 'orbit', 'space'],
        'medical': ['医疗', '制药', 'dna', '医院', 'medicine'],
        'peace': ['战争', '军事', '冲突', '和平', 'war', 'peace'],
        'finance': ['资本', '投资', '万亿', 'ipo', 'finance', '估值'],
        'code': ['代码', '编程', '开发', '无代码', 'code', 'programming'],
        'art': ['艺术', '绘画', '创作', '设计', 'art', 'paint'],
        'token': ['token', '算力成本', 'api调用'],
        'control': ['控制', '桌面', 'automation', 'computer'],
    }
    
    prompt_templates = {
        'ai': 'futuristic AI technology with neural networks and glowing circuits, blue-purple gradient, digital art',
        'chip': 'advanced microchip with intricate circuits, silicon wafer close-up, futuristic technology',
        'robot': 'friendly humanoid robot with sleek design, soft lighting, futuristic but approachable',
        'space': 'satellite orbiting Earth, cosmic background, space technology, beautiful and awe-inspiring',
        'medical': 'medical technology with DNA helix, futuristic healthcare, clean and professional',
        'peace': 'digital peace dove with circuit patterns, technology for harmony, hopeful atmosphere',
        'finance': 'abstract financial growth visualization, digital economy, professional blue tones',
        'code': 'abstract code visualization, programming concepts, flowing data streams, developer theme',
        'art': 'AI art creation process, digital canvas, creative visualization, inspiring and colorful',
        'token': 'digital token network visualization, blockchain concept, interconnected nodes',
        'control': 'futuristic computer interface, holographic display, automation technology',
    }
    
    for theme, keywords in themes.items():
        for keyword in keywords:
            if keyword in title_lower:
                return prompt_templates[theme]
    
    return 'futuristic technology concept, abstract digital art, professional blog header style'


def generate_image_prompt(title):
    """生成配图提示词"""
    theme_prompt = detect_theme(title)
    base_prompt = f"Professional blog header illustration: {theme_prompt}. Clean modern design, soft lighting, digital art style, 16:9 wide format, high quality, no text, suitable for tech blog"
    return base_prompt


def generate_image(prompt, output_path=None, width=1024, height=576):
    """生成图像并保存"""
    try:
        import urllib.request
        import urllib.parse
        import json
        
        # 使用 Pollinations.ai API
        encoded_prompt = urllib.parse.quote(prompt)
        
        # 构建 API URL
        api_key = os.environ.get("POLLINATIONS_API_KEY", "")
        if api_key:
            url = f"https://gen.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42&api_key={api_key}"
        else:
            url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed=42"
        
        print(f"⏳ 正在生成图像...")
        print(f"   提示词: {prompt[:80]}...")
        
        # 下载图像
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=120) as response:
            image_data = response.read()
            
            # 确保目录存在
            if output_path:
                os.makedirs(os.path.dirname(output_path), exist_ok=True)
            else:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                output_dir = "/root/.openclaw/workspace/blog-images"
                os.makedirs(output_dir, exist_ok=True)
                output_path = f"{output_dir}/blog_image_{timestamp}.png"
            
            with open(output_path, 'wb') as f:
                f.write(image_data)
            
            print(f"✅ 图像已保存: {output_path}")
            return output_path
            
    except Exception as e:
        print(f"❌ 图像生成失败: {e}")
        return None


def upload_image_to_wordpress(image_path):
    """上传图像到 WordPress 媒体库"""
    try:
        server, wp_username, wp_password = get_wordpress_client()
        
        # 读取图像文件
        with open(image_path, 'rb') as f:
            image_data = f.read()
        
        # 构建上传数据
        filename = os.path.basename(image_path)
        filetype = 'image/png'
        
        media = {
            'name': filename,
            'type': filetype,
            'bits': xmlrpc.client.Binary(image_data),
        }
        
        # 上传
        result = server.wp.uploadFile(0, wp_username, wp_password, media)
        print(f"✅ 图像已上传到 WordPress: {result['url']}")
        return result['id'], result['url']
        
    except Exception as e:
        print(f"❌ 上传图像失败: {e}")
        return None, None


def publish_post(title, content, featured_image_id=None):
    """发布文章到 WordPress"""
    try:
        server, wp_username, wp_password = get_wordpress_client()
        
        # 构建发布数据
        post = {
            'post_title': title,
            'post_content': content,
            'post_status': 'publish',
            'post_type': 'post',
        }
        
        if featured_image_id:
            post['post_thumbnail'] = featured_image_id
        
        # 发布
        post_id = server.wp.newPost(0, wp_username, wp_password, post)
        
        # 获取文章链接
        post_info = server.wp.getPost(0, wp_username, wp_password, post_id)
        post_url = post_info.get('link', f"http://blog.weme.uno/?p={post_id}")
        
        return post_id, post_url
        
    except Exception as e:
        print(f"❌ 发布失败: {e}")
        return None, None


def preview_draft(draft_file):
    """预览草稿"""
    if not os.path.exists(draft_file):
        print(f"❌ 文件不存在: {draft_file}")
        return
    
    with open(draft_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = extract_title_from_content(content)
    summary = extract_summary(content)
    word_count = len(content)
    
    print(f"标题: {title}")
    print(f"摘要: {summary}")
    print(f"字数: {word_count}")


def gen_prompt(draft_file):
    """生成配图提示词"""
    if not os.path.exists(draft_file):
        print(f"❌ 文件不存在: {draft_file}")
        return
    
    with open(draft_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = extract_title_from_content(content)
    prompt = generate_image_prompt(title)
    
    print(f"🎨 图像生成提示词:")
    print(f"{'='*60}")
    print(prompt)
    print(f"{'='*60}")


def gen_image(draft_file):
    """生成配图"""
    if not os.path.exists(draft_file):
        print(f"❌ 文件不存在: {draft_file}")
        return
    
    with open(draft_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = extract_title_from_content(content)
    prompt = generate_image_prompt(title)
    
    # 生成文件名
    timestamp = datetime.now().strftime("%Y%m%d")
    safe_title = "".join(c for c in title[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
    output_dir = "/root/.openclaw/workspace/blog-images"
    os.makedirs(output_dir, exist_ok=True)
    output_path = f"{output_dir}/blog_image_{timestamp}_{safe_title}.png"
    
    print(f"📝 文章标题: {title}")
    print(f"🎨 生成提示词: {prompt[:80]}...")
    
    image_path = generate_image(prompt, output_path)
    
    if image_path:
        print(f"\n✅ 博客配图已生成!")
        print(f"📁 文件路径: {image_path}")
    
    return image_path


def publish(draft_file, generate_image_flag=False):
    """发布文章"""
    if not os.path.exists(draft_file):
        print(f"❌ 文件不存在: {draft_file}")
        return
    
    with open(draft_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    title = extract_title_from_content(content)
    print(f"发布文章: {title}\n")
    
    featured_image_id = None
    image_path = None
    
    # 生成配图
    if generate_image_flag:
        print("🎨 生成配图...")
        image_path = gen_image(draft_file)
        
        if image_path:
            print("\n📤 上传配图到 WordPress...")
            featured_image_id, image_url = upload_image_to_wordpress(image_path)
            if featured_image_id:
                print("✅ 配图已添加到文章")
    
    # 发布文章
    print("\n📝 发布文章...")
    post_id, post_url = publish_post(title, content, featured_image_id)
    
    if post_id:
        print(f"\n✅ 文章发布成功!")
        print(f"   Post ID: {post_id}")
        print(f"   链接: {post_url}")
        if image_path:
            print(f"   配图: {image_path}")
        return post_id, post_url
    else:
        print("\n❌ 文章发布失败")
        return None, None


def main():
    parser = argparse.ArgumentParser(description='博客发布工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # preview 命令
    preview_parser = subparsers.add_parser('preview', help='预览文章')
    preview_parser.add_argument('draft_file', help='草稿文件路径')
    
    # gen-prompt 命令
    prompt_parser = subparsers.add_parser('gen-prompt', help='生成配图提示词')
    prompt_parser.add_argument('draft_file', help='草稿文件路径')
    
    # gen-image 命令
    image_parser = subparsers.add_parser('gen-image', help='生成配图')
    image_parser.add_argument('draft_file', help='草稿文件路径')
    
    # publish 命令
    publish_parser = subparsers.add_parser('publish', help='发布文章')
    publish_parser.add_argument('draft_file', help='草稿文件路径')
    publish_parser.add_argument('--generate-image', action='store_true', help='自动生成配图')
    
    args = parser.parse_args()
    
    if args.command == 'preview':
        preview_draft(args.draft_file)
    elif args.command == 'gen-prompt':
        gen_prompt(args.draft_file)
    elif args.command == 'gen-image':
        gen_image(args.draft_file)
    elif args.command == 'publish':
        publish(args.draft_file, args.generate_image)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
