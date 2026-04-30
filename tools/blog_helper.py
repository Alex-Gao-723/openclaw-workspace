#!/usr/bin/env python3
"""
博客发布辅助脚本 - 处理博客编号管理和发布记录
避免直接编辑 MEMORY.md 导致的并发冲突
"""
import os
import json
import re
from datetime import datetime
from pathlib import Path

WORKSPACE = Path("/root/.openclaw/workspace")
BLOG_RECORD_FILE = WORKSPACE / "tools" / "blog_records.json"
MEMORY_FILE = WORKSPACE / "MEMORY.md"

def load_blog_records():
    """加载博客发布记录"""
    if BLOG_RECORD_FILE.exists():
        with open(BLOG_RECORD_FILE, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"blogs": [], "last_number": 0}

def save_blog_records(records):
    """保存博客发布记录"""
    with open(BLOG_RECORD_FILE, 'w', encoding='utf-8') as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

def get_next_blog_number():
    """获取下一个博客编号"""
    records = load_blog_records()
    return records["last_number"] + 1

def add_blog_record(title, url, summary, source_date=None):
    """
    添加博客发布记录
    返回博客编号
    """
    records = load_blog_records()
    blog_number = records["last_number"] + 1
    
    blog_entry = {
        "number": blog_number,
        "title": title,
        "url": url,
        "summary": summary,
        "published_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source_date": source_date or datetime.now().strftime("%Y-%m-%d")
    }
    
    records["blogs"].append(blog_entry)
    records["last_number"] = blog_number
    
    save_blog_records(records)
    
    # 尝试更新 MEMORY.md，但失败不报错
    try_update_memory_md(blog_entry)
    
    return blog_number

def try_update_memory_md(blog_entry):
    """
    尝试更新 MEMORY.md 中的博客列表
    使用更安全的方式，避免并发冲突
    """
    try:
        if not MEMORY_FILE.exists():
            return False
        
        with open(MEMORY_FILE, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 查找博客列表部分
        blog_pattern = r'(##\s*博客发布记录.*?\n)(.*?)(?=\n##\s|$)'
        match = re.search(blog_pattern, content, re.DOTALL)
        
        if match:
            # 在列表开头添加新记录
            new_entry = f"- 第{blog_entry['number']}篇: [{blog_entry['title']}]({blog_entry['url']}) ({blog_entry['source_date']})\n"
            
            # 找到列表开始的位置
            list_start = match.start(2)
            new_content = content[:list_start] + new_entry + content[list_start:]
            
            with open(MEMORY_FILE, 'w', encoding='utf-8') as f:
                f.write(new_content)
            
            return True
    except Exception as e:
        print(f"[WARNING] 更新 MEMORY.md 失败（非致命）: {e}")
    
    return False

def get_recent_blogs(count=5):
    """获取最近发布的博客列表"""
    records = load_blog_records()
    return records["blogs"][-count:]

def get_blog_stats():
    """获取博客统计信息"""
    records = load_blog_records()
    return {
        "total_count": len(records["blogs"]),
        "last_number": records["last_number"],
        "last_published": records["blogs"][-1]["published_at"] if records["blogs"] else None
    }

if __name__ == "__main__":
    import sys
    
    if len(sys.argv) < 2:
        print("Usage:")
        print("  python3 blog_helper.py next-number")
        print("  python3 blog_helper.py add <title> <url> <summary> [source_date]")
        print("  python3 blog_helper.py recent [count]")
        print("  python3 blog_helper.py stats")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "next-number":
        print(get_next_blog_number())
    
    elif command == "add":
        if len(sys.argv) < 5:
            print("Usage: python3 blog_helper.py add <title> <url> <summary> [source_date]")
            sys.exit(1)
        
        title = sys.argv[2]
        url = sys.argv[3]
        summary = sys.argv[4]
        source_date = sys.argv[5] if len(sys.argv) > 5 else None
        
        number = add_blog_record(title, url, summary, source_date)
        print(f"✅ 博客记录已添加: 第{number}篇")
        print(json.dumps(get_blog_stats(), ensure_ascii=False, indent=2))
    
    elif command == "recent":
        count = int(sys.argv[2]) if len(sys.argv) > 2 else 5
        blogs = get_recent_blogs(count)
        print(json.dumps(blogs, ensure_ascii=False, indent=2))
    
    elif command == "stats":
        stats = get_blog_stats()
        print(json.dumps(stats, ensure_ascii=False, indent=2))
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)
