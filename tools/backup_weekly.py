#!/usr/bin/env python3
"""
每周核心数据备份脚本
打包工作空间核心 .md 文件并生成备份摘要

用法:
    python3 backup_weekly.py
"""

import os
import sys
import tarfile
import datetime
import json
from pathlib import Path

# 配置
WORKSPACE = "/root/.openclaw/workspace"
BACKUP_DIR = "/tmp/openclaw-backups"
INCLUDE_PATTERNS = [
    "*.md",
    "memory/*.md",
    "tools/*.py",
    "skills/*/*.md",
    "skills/*/*.py",
    "scripts/*.sh",
]
EXCLUDE_PATTERNS = [
    "node_modules",
    ".git",
    "__pycache__",
    "*.tmp",
    "*.log",
]

def get_file_size_str(size_bytes):
    """将字节转换为人类可读格式"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024:
            return f"{size_bytes:.1f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.1f} TB"

def collect_files():
    """收集需要备份的文件"""
    workspace_path = Path(WORKSPACE)
    files_to_backup = []
    total_size = 0
    
    for pattern in INCLUDE_PATTERNS:
        for file_path in workspace_path.glob(pattern):
            # 检查排除模式
            should_exclude = False
            for exclude in EXCLUDE_PATTERNS:
                if exclude in str(file_path):
                    should_exclude = True
                    break
            
            if should_exclude:
                continue
                
            if file_path.is_file():
                rel_path = file_path.relative_to(workspace_path)
                size = file_path.stat().st_size
                files_to_backup.append({
                    'path': str(rel_path),
                    'full_path': str(file_path),
                    'size': size
                })
                total_size += size
    
    return files_to_backup, total_size

def create_backup(files_to_backup):
    """创建 tar.gz 备份包"""
    os.makedirs(BACKUP_DIR, exist_ok=True)
    
    date_str = datetime.datetime.now().strftime("%Y%m%d")
    backup_filename = f"openclaw-backup-{date_str}.tar.gz"
    backup_path = os.path.join(BACKUP_DIR, backup_filename)
    
    with tarfile.open(backup_path, "w:gz") as tar:
        for file_info in files_to_backup:
            tar.add(file_info['full_path'], arcname=file_info['path'])
    
    backup_size = os.path.getsize(backup_path)
    return backup_path, backup_size

def generate_summary(files_to_backup, total_size, backup_path, backup_size):
    """生成备份摘要"""
    # 统计文件类型
    type_counts = {}
    for f in files_to_backup:
        ext = os.path.splitext(f['path'])[1] or 'no_ext'
        type_counts[ext] = type_counts.get(ext, 0) + 1
    
    # 获取最大的10个文件
    top_files = sorted(files_to_backup, key=lambda x: x['size'], reverse=True)[:10]
    
    summary = {
        'backup_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        'total_files': len(files_to_backup),
        'total_size_raw': total_size,
        'total_size_human': get_file_size_str(total_size),
        'backup_file': os.path.basename(backup_path),
        'backup_size_raw': backup_size,
        'backup_size_human': get_file_size_str(backup_size),
        'compression_ratio': f"{(backup_size / total_size * 100):.1f}%" if total_size > 0 else "N/A",
        'file_types': type_counts,
        'top_files': [
            {
                'path': f['path'],
                'size': get_file_size_str(f['size'])
            }
            for f in top_files
        ],
        'backup_path': backup_path
    }
    
    return summary

def main():
    try:
        # 收集文件
        files_to_backup, total_size = collect_files()
        
        if not files_to_backup:
            result = {
                'status': 'warning',
                'message': '没有找到需要备份的文件',
                'backup_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            print(json.dumps(result, ensure_ascii=False, indent=2))
            return 0
        
        # 创建备份
        backup_path, backup_size = create_backup(files_to_backup)
        
        # 生成摘要
        summary = generate_summary(files_to_backup, total_size, backup_path, backup_size)
        summary['status'] = 'success'
        
        # 输出 JSON
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0
        
    except Exception as e:
        result = {
            'status': 'error',
            'message': str(e),
            'backup_date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 1

if __name__ == "__main__":
    sys.exit(main())
