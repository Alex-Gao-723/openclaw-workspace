#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
每日录音卡笔记导出脚本
从Get笔记获取前一天的录音卡笔记并保存为Markdown
"""

import os
import json
import requests
from datetime import datetime, timedelta
from pathlib import Path

# Get笔记API配置
API_KEY = "gk_live_a260956949bd9fd8.8534e77ba9117eeccd40c0d9383c37202ec87a9c7c6df106"
CLIENT_ID = "cli_3802f9db08b811f197679c63c078bacc"
BASE_URL = "https://openapi.biji.com/open/api/v1"

def get_yesterday_date():
    """获取昨天的日期"""
    yesterday = datetime.now() - timedelta(days=1)
    return yesterday.strftime("%Y-%m-%d")

def fetch_notes():
    """从Get笔记获取所有笔记"""
    url = f"{BASE_URL}/resource/note/list"
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "X-Client-ID": CLIENT_ID,
        "Content-Type": "application/json"
    }
    params = {
        "since_id": 0
    }
    
    response = requests.get(url, headers=headers, params=params)
    if response.status_code == 200:
        data = response.json()
        if data.get("success"):
            return data.get("data", {}).get("notes", [])
    return []

def filter_recorder_notes(notes, target_date):
    """筛选指定日期的录音卡笔记"""
    recorder_notes = []
    for note in notes:
        # 检查是否为录音卡笔记
        note_type = note.get("note_type", "")
        if note_type != "recorder_flash_audio":
            continue
            
        # 检查日期
        created_at = note.get("created_at", "")
        if created_at.startswith(target_date):
            recorder_notes.append(note)
    
    return recorder_notes

def format_note_to_markdown(note):
    """将笔记格式化为Markdown"""
    title = note.get("title", "无标题")
    content = note.get("content", "")
    created_at = note.get("created_at", "")
    tags = note.get("tags", [])
    
    # 提取标签名称
    tag_names = [tag.get("name", "") for tag in tags if tag.get("name")]
    tags_str = ", ".join(tag_names) if tag_names else "无标签"
    
    md = f"""## {title}

**创建时间**: {created_at}

**标签**: {tags_str}

**内容**:

{content}

---

"""
    return md

def main():
    """主函数"""
    # 获取昨天日期
    yesterday = get_yesterday_date()
    print(f"📅 正在导出 {yesterday} 的录音卡笔记...")
    
    # 获取所有笔记
    notes = fetch_notes()
    print(f"📚 共获取 {len(notes)} 条笔记")
    
    # 筛选录音卡笔记
    recorder_notes = filter_recorder_notes(notes, yesterday)
    print(f"🎙️ 找到 {len(recorder_notes)} 条录音卡笔记")
    
    if not recorder_notes:
        print("ℹ️ 没有录音卡笔记")
        return
    
    # 创建输出目录
    output_dir = Path("/root/.openclaw/workspace/录音卡笔记")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # 生成Markdown内容
    md_content = f"""# 录音卡笔记 - {yesterday}

导出时间: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

共导出 {len(recorder_notes)} 条录音卡笔记

---

"""
    
    for note in recorder_notes:
        md_content += format_note_to_markdown(note)
    
    # 保存文件
    output_file = output_dir / f"{yesterday}.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    print(f"✅ 已保存到: {output_file}")
    print(f"📊 导出完成: {len(recorder_notes)} 条笔记")

if __name__ == "__main__":
    main()
