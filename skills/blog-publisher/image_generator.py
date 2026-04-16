#!/usr/bin/env python3
"""
独立图像生成模块 - 用于博客配图生成
支持 Pollinations.ai API 和本地 Fallback
"""
import os
import sys
import argparse
import urllib.request
import urllib.parse
from datetime import datetime


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


def extract_prompt_from_draft(draft_file):
    """从博客草稿提取标题和图像提示词"""
    if not os.path.exists(draft_file):
        raise FileNotFoundError(f"草稿文件不存在: {draft_file}")
    
    with open(draft_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 提取标题
    lines = content.split('\n')
    title = "Untitled"
    for line in lines:
        line = line.strip()
        if line.startswith('# '):
            title = line[2:].strip()
            break
        elif line.startswith('## '):
            title = line[3:].strip()
            break
    
    # 生成提示词
    theme_prompt = detect_theme(title)
    full_prompt = f"Professional blog header illustration: {theme_prompt}. Clean modern design, soft lighting, digital art style, 16:9 wide format, high quality, no text, suitable for tech blog"
    
    return title, full_prompt


def generate_image_url(prompt, width=1024, height=576, seed=42):
    """
    生成图像 URL（不下载）
    返回可直接访问的图像 URL
    """
    encoded_prompt = urllib.parse.quote(prompt)
    
    # 优先使用 gen.pollinations.ai (需要 API Key)
    api_key = os.environ.get("POLLINATIONS_API_KEY", "")
    if api_key:
        url = f"https://gen.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}&api_key={api_key}"
    else:
        # 免费版使用 image.pollinations.ai
        url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width={width}&height={height}&nologo=true&seed={seed}"
    
    return url


def download_image(url, output_path, timeout=120):
    """从 URL 下载图像到本地"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.0'
        }
        request = urllib.request.Request(url, headers=headers)
        
        with urllib.request.urlopen(request, timeout=timeout) as response:
            image_data = response.read()
            
            # 确保目录存在
            os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
            
            with open(output_path, 'wb') as f:
                f.write(image_data)
            
            return True
            
    except Exception as e:
        print(f"❌ 下载图像失败: {e}")
        return False


def generate_image(prompt, output_path=None, width=1024, height=576):
    """
    生成图像并保存到本地
    
    Args:
        prompt: 图像生成提示词
        output_path: 输出路径（可选）
        width: 图像宽度
        height: 图像高度
    
    Returns:
        成功返回文件路径，失败返回 None
    """
    try:
        print(f"⏳ 正在生成图像...")
        print(f"   提示词: {prompt[:80]}...")
        
        # 生成 URL
        url = generate_image_url(prompt, width, height)
        
        # 生成默认输出路径
        if not output_path:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            output_dir = "/root/.openclaw/workspace/blog-images"
            os.makedirs(output_dir, exist_ok=True)
            output_path = f"{output_dir}/blog_image_{timestamp}.png"
        
        # 下载图像
        if download_image(url, output_path):
            print(f"✅ 图像已保存: {output_path}")
            return output_path
        else:
            return None
            
    except Exception as e:
        print(f"❌ 图像生成失败: {e}")
        return None


def generate_from_draft(draft_file, output_dir=None):
    """
    从博客草稿生成配图
    
    Args:
        draft_file: 草稿文件路径
        output_dir: 输出目录（可选）
    
    Returns:
        成功返回文件路径，失败返回 None
    """
    try:
        # 提取标题和提示词
        title, prompt = extract_prompt_from_draft(draft_file)
        
        print(f"📝 文章标题: {title}")
        print(f"🎨 生成提示词: {prompt[:80]}...")
        
        # 生成输出路径
        if not output_dir:
            output_dir = "/root/.openclaw/workspace/blog-images"
        
        timestamp = datetime.now().strftime("%Y%m%d")
        safe_title = "".join(c for c in title[:20] if c.isalnum() or c in (' ', '-', '_')).strip()
        output_path = f"{output_dir}/blog_image_{timestamp}_{safe_title}.png"
        
        # 生成图像
        result = generate_image(prompt, output_path)
        
        if result:
            print(f"\n✅ 博客配图已生成!")
            print(f"📁 文件路径: {result}")
        
        return result
        
    except Exception as e:
        print(f"❌ 生成配图失败: {e}")
        return None


def create_fallback_image(output_path, title="Blog Post"):
    """
    创建本地 Fallback 图像（当 API 不可用时）
    使用 PIL 生成简单的占位图
    """
    try:
        from PIL import Image, ImageDraw, ImageFont
        
        # 创建图像
        width, height = 1024, 576
        img = Image.new('RGB', (width, height), color='#1a1a2e')
        draw = ImageDraw.Draw(img)
        
        # 绘制渐变背景
        for y in range(height):
            r = int(26 + (y / height) * 20)
            g = int(26 + (y / height) * 40)
            b = int(46 + (y / height) * 60)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        # 绘制装饰线条
        draw.line([(50, height//2), (width-50, height//2)], fill='#4a4a6a', width=2)
        
        # 添加文字
        try:
            font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 48)
            small_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 24)
        except:
            font = ImageFont.load_default()
            small_font = ImageFont.load_default()
        
        # 居中文字
        text = title[:30]  # 限制长度
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = (width - text_width) // 2
        
        draw.text((text_x, height//2 - 60), text, fill='#ffffff', font=font)
        draw.text((width//2 - 100, height//2 + 20), "AI Generated Blog Image", fill='#aaaaaa', font=small_font)
        
        # 保存
        os.makedirs(os.path.dirname(output_path) or '.', exist_ok=True)
        img.save(output_path)
        
        print(f"✅ Fallback 图像已创建: {output_path}")
        return output_path
        
    except ImportError:
        print("❌ PIL 未安装，无法创建 Fallback 图像")
        return None
    except Exception as e:
        print(f"❌ 创建 Fallback 图像失败: {e}")
        return None


def main():
    parser = argparse.ArgumentParser(description='博客配图生成工具')
    subparsers = parser.add_subparsers(dest='command', help='可用命令')
    
    # generate 命令 - 根据提示词生成
    gen_parser = subparsers.add_parser('generate', help='根据提示词生成图像')
    gen_parser.add_argument('prompt', help='图像生成提示词')
    gen_parser.add_argument('--output', '-o', help='输出路径')
    gen_parser.add_argument('--width', type=int, default=1024, help='图像宽度')
    gen_parser.add_argument('--height', type=int, default=576, help='图像高度')
    
    # generate-from-draft 命令 - 根据草稿生成
    draft_parser = subparsers.add_parser('generate-from-draft', help='根据博客草稿生成配图')
    draft_parser.add_argument('draft_file', help='博客草稿文件路径')
    draft_parser.add_argument('--output-dir', '-d', help='输出目录')
    
    # fallback 命令 - 创建本地占位图
    fallback_parser = subparsers.add_parser('fallback', help='创建本地占位图（当 API 不可用时）')
    fallback_parser.add_argument('--title', default='Blog Post', help='博客标题')
    fallback_parser.add_argument('--output', '-o', required=True, help='输出路径')
    
    args = parser.parse_args()
    
    if args.command == 'generate':
        generate_image(args.prompt, args.output, args.width, args.height)
    elif args.command == 'generate-from-draft':
        generate_from_draft(args.draft_file, args.output_dir)
    elif args.command == 'fallback':
        create_fallback_image(args.output, args.title)
    else:
        parser.print_help()


if __name__ == '__main__':
    main()
