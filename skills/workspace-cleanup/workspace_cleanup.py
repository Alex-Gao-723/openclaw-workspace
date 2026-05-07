#!/usr/bin/env python3
"""
Workspace Cleanup Tool - 工作空间清理工具
自动清理临时文件、旧日志、Python 缓存，保持工作空间整洁健康。

Usage:
    python3 workspace_cleanup.py [--execute] [--json]
"""

import json
import os
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

# 北京时间
TZ_CN = timezone(timedelta(hours=8))

# 工作空间根目录
WORKSPACE_DIR = os.path.expanduser("~/.openclaw/workspace")

# 清理策略: (目录/模式, 保留天数, 描述)
CLEANUP_RULES = [
    # 临时文件 - 保留1天
    (os.path.join(WORKSPACE_DIR, "*.tmp"), 1, "temp"),
    (os.path.join(WORKSPACE_DIR, "temp"), 1, "temp"),
    
    # 日志文件 - 保留7天
    (os.path.join(WORKSPACE_DIR, "*.log"), 7, "logs"),
    (os.path.join(WORKSPACE_DIR, "logs"), 7, "logs"),
    
    # Python 缓存 - 保留3天
    (os.path.join(WORKSPACE_DIR, "__pycache__"), 3, "cache"),
    (os.path.join(WORKSPACE_DIR, "*.pyc"), 3, "cache"),
    (os.path.join(WORKSPACE_DIR, ".pytest_cache"), 3, "cache"),
    
    # 博客草稿 - 保留30天
    (os.path.join(WORKSPACE_DIR, "blog_*_draft*.md"), 30, "drafts"),
    
    # 备份文件 - 保留14天
    ("/tmp/openclaw-backups", 14, "backups"),
]

# 额外清理规则：递归删除的目录名
RECURSIVE_CLEANUP_DIRS = [
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
]


class CleanupItem:
    """单个待清理项目"""
    def __init__(self, path: str, age_days: float, size_bytes: int, category: str):
        self.path = path
        self.age_days = age_days
        self.size_bytes = size_bytes
        self.category = category
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "path": self.path,
            "age_days": round(self.age_days, 1),
            "size_bytes": self.size_bytes,
            "size_human": self._human_size(),
            "category": self.category,
        }
    
    def _human_size(self) -> str:
        size = self.size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


class CleanupResult:
    """清理结果汇总"""
    def __init__(self):
        self.items: List[CleanupItem] = []
        self.files_to_delete: List[str] = []
        self.dirs_to_delete: List[str] = []
        self.space_to_free: int = 0
        self.freed_space: int = 0
        self.dry_run: bool = True
        self.timestamp: str = datetime.now(TZ_CN).isoformat()
    
    def add_item(self, item: CleanupItem):
        self.items.append(item)
        self.space_to_free += item.size_bytes
        if os.path.isdir(item.path):
            self.dirs_to_delete.append(item.path)
        else:
            self.files_to_delete.append(item.path)
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "timestamp": self.timestamp,
            "dry_run": self.dry_run,
            "total_items": len(self.items),
            "files_to_delete": len(self.files_to_delete),
            "dirs_to_delete": len(self.dirs_to_delete),
            "space_to_free_bytes": self.space_to_free,
            "space_to_free_human": self._human_size(self.space_to_free),
            "freed_space_bytes": self.freed_space,
            "freed_space_human": self._human_size(self.freed_space),
            "items": [item.to_dict() for item in self.items],
        }
    
    @staticmethod
    def _human_size(size_bytes: int) -> str:
        size = size_bytes
        for unit in ["B", "KB", "MB", "GB"]:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def get_file_age_days(path: str) -> float:
    """获取文件/目录的年龄（天数）"""
    try:
        stat = os.stat(path)
        mtime = datetime.fromtimestamp(stat.st_mtime, tz=timezone.utc)
        now = datetime.now(timezone.utc)
        return (now - mtime).total_seconds() / 86400
    except Exception:
        return 0


def get_path_size(path: str) -> int:
    """获取文件或目录的大小"""
    try:
        if os.path.isfile(path):
            return os.path.getsize(path)
        elif os.path.isdir(path):
            total = 0
            for dirpath, dirnames, filenames in os.walk(path):
                for f in filenames:
                    fp = os.path.join(dirpath, f)
                    if os.path.exists(fp):
                        total += os.path.getsize(fp)
            return total
    except Exception:
        pass
    return 0


def scan_workspace(result: CleanupResult):
    """扫描工作空间，识别可清理文件"""
    
    # 1. 按规则扫描
    for pattern, keep_days, category in CLEANUP_RULES:
        if os.path.isfile(pattern) or os.path.isdir(pattern):
            # 直接路径
            _check_and_add(pattern, keep_days, category, result)
        elif "*" in pattern:
            # 通配符模式
            import glob
            for path in glob.glob(pattern):
                _check_and_add(path, keep_days, category, result)
    
    # 2. 递归扫描 Python 缓存目录
    for root, dirs, files in os.walk(WORKSPACE_DIR):
        # 跳过 .git 和 node_modules
        dirs[:] = [d for d in dirs if d not in {".git", "node_modules"}]
        
        # 检查是否需要清理的目录名
        for dirname in dirs:
            if dirname in RECURSIVE_CLEANUP_DIRS:
                path = os.path.join(root, dirname)
                age = get_file_age_days(path)
                if age > 3:  # 缓存保留3天
                    size = get_path_size(path)
                    result.add_item(CleanupItem(path, age, size, "cache"))
        
        # 检查 .pyc 文件
        for filename in files:
            if filename.endswith(".pyc"):
                path = os.path.join(root, filename)
                age = get_file_age_days(path)
                if age > 3:
                    size = get_path_size(path)
                    result.add_item(CleanupItem(path, age, size, "cache"))
    
    # 3. 扫描 /tmp 下的 openclaw 相关临时文件
    tmp_openclaw = "/tmp/openclaw"
    if os.path.exists(tmp_openclaw):
        for item in os.listdir(tmp_openclaw):
            path = os.path.join(tmp_openclaw, item)
            age = get_file_age_days(path)
            if age > 1:  # 临时文件保留1天
                size = get_path_size(path)
                result.add_item(CleanupItem(path, age, size, "temp"))
    
    # 4. 扫描旧的备份文件
    backups_dir = "/tmp/openclaw-backups"
    if os.path.exists(backups_dir):
        for item in os.listdir(backups_dir):
            path = os.path.join(backups_dir, item)
            age = get_file_age_days(path)
            if age > 14:  # 备份保留14天
                size = get_path_size(path)
                result.add_item(CleanupItem(path, age, size, "backups"))


def _check_and_add(path: str, keep_days: int, category: str, result: CleanupResult):
    """检查文件年龄并添加到结果"""
    if not os.path.exists(path):
        return
    
    age = get_file_age_days(path)
    if age > keep_days:
        size = get_path_size(path)
        result.add_item(CleanupItem(path, age, size, category))


def execute_cleanup(result: CleanupResult, dry_run: bool = True):
    """执行清理操作"""
    result.dry_run = dry_run
    
    if dry_run:
        return
    
    # 先删除文件
    for filepath in result.files_to_delete:
        try:
            if os.path.exists(filepath):
                os.remove(filepath)
                result.freed_space += next((i.size_bytes for i in result.items if i.path == filepath), 0)
        except Exception as e:
            print(f"  ⚠️  删除文件失败: {filepath} - {e}")
    
    # 再删除目录（从深到浅，避免删除父目录后无法删除子目录）
    dirs_sorted = sorted(result.dirs_to_delete, key=lambda x: len(x.split(os.sep)), reverse=True)
    for dirpath in dirs_sorted:
        try:
            if os.path.exists(dirpath):
                import shutil
                shutil.rmtree(dirpath)
                result.freed_space += next((i.size_bytes for i in result.items if i.path == dirpath), 0)
        except Exception as e:
            print(f"  ⚠️  删除目录失败: {dirpath} - {e}")


def generate_report(result: CleanupResult) -> str:
    """生成文本报告"""
    lines = []
    lines.append("=" * 60)
    lines.append("🧹 工作空间清理报告")
    lines.append(f"生成时间: {result.timestamp}")
    lines.append("=" * 60)
    lines.append("")
    
    mode = "预览 (dry-run)" if result.dry_run else "实际执行"
    lines.append(f"📋 模式: {mode}")
    lines.append("")
    
    lines.append(f"📊 扫描结果:")
    lines.append(f"   待清理文件: {len(result.files_to_delete)} 个")
    lines.append(f"   待清理目录: {len(result.dirs_to_delete)} 个")
    lines.append(f"   可释放空间: {result._human_size(result.space_to_free)}")
    lines.append("")
    
    if result.items:
        lines.append("📁 待清理项目 (按类别分组):")
        
        # 按类别分组
        by_category: Dict[str, List[CleanupItem]] = {}
        for item in result.items:
            by_category.setdefault(item.category, []).append(item)
        
        for category, items in sorted(by_category.items()):
            category_names = {
                "temp": "临时文件",
                "logs": "日志文件",
                "cache": "缓存文件",
                "drafts": "草稿文件",
                "backups": "备份文件",
            }
            cat_name = category_names.get(category, category)
            lines.append(f"\n   [{cat_name}] ({len(items)} 项)")
            
            # 只显示前5个
            for item in items[:5]:
                lines.append(f"      • {os.path.basename(item.path)}")
                lines.append(f"        年龄: {item.age_days:.1f}天 | 大小: {item._human_size()}")
            
            if len(items) > 5:
                lines.append(f"        ... 还有 {len(items) - 5} 项")
    
    lines.append("")
    
    if not result.dry_run:
        lines.append(f"✅ 已释放空间: {result._human_size(result.freed_space)}")
        lines.append("")
    
    if result.dry_run and result.items:
        lines.append("💡 提示: 使用 --execute 参数执行实际清理")
    elif not result.items:
        lines.append("✅ 工作空间很整洁，无需清理")
    
    lines.append("")
    lines.append("=" * 60)
    
    return "\n".join(lines)


def main():
    # 解析参数
    execute_mode = "--execute" in sys.argv
    json_mode = "--json" in sys.argv
    quiet_mode = "--quiet" in sys.argv
    
    # 扫描
    result = CleanupResult()
    scan_workspace(result)
    
    # 执行清理（如果不是 dry-run）
    if execute_mode:
        execute_cleanup(result, dry_run=False)
    
    # 输出报告
    if json_mode:
        print(json.dumps(result.to_dict(), indent=2, ensure_ascii=False))
    elif quiet_mode:
        # 仅在有可清理项时输出
        if result.items:
            print(f"🧹 可清理 {len(result.items)} 项，释放 {result._human_size(result.space_to_free)}")
            sys.exit(1)
        else:
            print("✅ 工作空间整洁")
            sys.exit(0)
    else:
        print(generate_report(result))
    
    # 返回退出码
    if result.items and not execute_mode:
        sys.exit(1)  # 有未清理的文件
    sys.exit(0)


if __name__ == "__main__":
    main()
