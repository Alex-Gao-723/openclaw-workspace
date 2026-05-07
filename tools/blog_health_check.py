#!/usr/bin/env python3
"""
博客系统健康检查脚本 - 验证博客发布管道的完整性
检查所有已发布博客的可访问性、HTML结构和服务器状态

Usage:
    python3 blog_health_check.py [--json] [--quiet]
"""

import json
import sys
import subprocess
import re
from pathlib import Path

# 配置
BLOG_RECORDS = Path("/root/.openclaw/workspace/tools/blog_records.json")
SERVER_HOST = "47.99.105.13"
SERVER_USER = "root"
SERVER_PASSWORD = "Gy280956117"
WEB_DIR = "/usr/share/nginx/html/blog"

def load_blog_records():
    """加载博客记录"""
    if BLOG_RECORDS.exists():
        with open(BLOG_RECORDS, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {"blogs": [], "last_number": 0}

def check_url_accessible(url):
    """检查URL是否可访问"""
    try:
        result = subprocess.run(
            ["curl", "-s", "-o", "/dev/null", "-w", "%{http_code}", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        code = result.stdout.strip()
        return code == "200", code
    except Exception as e:
        return False, str(e)

def check_blog_html_structure(url):
    """检查博客HTML结构完整性"""
    try:
        result = subprocess.run(
            ["curl", "-s", "--max-time", "10", url],
            capture_output=True, text=True, timeout=15
        )
        html = result.stdout
        
        checks = {
            "has_doctype": "<!DOCTYPE html>" in html,
            "has_html_tag": "<html" in html,
            "has_head": "<head>" in html or "<head " in html,
            "has_body": "<body>" in html or "<body " in html,
            "has_title": "<title>" in html,
            "has_container": "class=\"container\"" in html or 'class="container"' in html,
            "has_content": "class=\"content\"" in html or 'class="content"' in html,
            "has_footer": "class=\"footer\"" in html or 'class="footer"' in html,
            "has_meta": "class=\"meta\"" in html or 'class="meta"' in html,
        }
        
        all_ok = all(checks.values())
        missing = [k for k, v in checks.items() if not v]
        
        return all_ok, missing
    except Exception as e:
        return False, [str(e)]

def check_server_disk_space():
    """检查博客服务器磁盘空间"""
    try:
        cmd = [
            "sshpass", "-p", SERVER_PASSWORD,
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{SERVER_USER}@{SERVER_HOST}",
            "df -h / | tail -1 | awk '{print $5}' | sed 's/%//'"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            pct = int(result.stdout.strip())
            return pct, pct < 80
        return None, False
    except Exception as e:
        return None, False

def check_server_blog_count():
    """检查服务器上的博客文件数量"""
    try:
        cmd = [
            "sshpass", "-p", SERVER_PASSWORD,
            "ssh", "-o", "StrictHostKeyChecking=no",
            f"{SERVER_USER}@{SERVER_HOST}",
            f"ls {WEB_DIR}/*.html 2>/dev/null | wc -l"
        ]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        if result.returncode == 0:
            return int(result.stdout.strip())
        return 0
    except Exception:
        return 0

def check_duplicate_titles(records):
    """检查重复标题"""
    titles = {}
    duplicates = []
    for blog in records["blogs"]:
        title = blog["title"]
        if title in titles:
            duplicates.append({
                "title": title,
                "numbers": [titles[title], blog["number"]]
            })
        else:
            titles[title] = blog["number"]
    return duplicates

def check_numbering_gaps(records):
    """检查编号是否连续"""
    numbers = [b["number"] for b in records["blogs"]]
    if not numbers:
        return []
    
    expected = list(range(1, max(numbers) + 1))
    actual = sorted(numbers)
    
    gaps = []
    for exp in expected:
        if exp not in actual:
            gaps.append(exp)
    
    return gaps

def main():
    json_mode = "--json" in sys.argv
    quiet_mode = "--quiet" in sys.argv
    
    records = load_blog_records()
    blogs = records.get("blogs", [])
    
    # 执行检查
    results = {
        "total_blogs": len(blogs),
        "last_number": records.get("last_number", 0),
        "url_checks": [],
        "html_checks": [],
        "server_disk": None,
        "server_blog_count": None,
        "duplicates": [],
        "gaps": [],
        "issues": [],
        "summary": {}
    }
    
    # 1. 检查最近5篇博客的URL可访问性
    recent_blogs = blogs[-5:] if len(blogs) >= 5 else blogs
    url_ok_count = 0
    for blog in recent_blogs:
        ok, code = check_url_accessible(blog["url"])
        results["url_checks"].append({
            "number": blog["number"],
            "url": blog["url"],
            "accessible": ok,
            "http_code": code
        })
        if ok:
            url_ok_count += 1
        else:
            results["issues"].append(f"博客 #{blog['number']} 不可访问 (HTTP {code})")
    
    # 2. 检查最近3篇博客的HTML结构
    latest_blogs = blogs[-3:] if len(blogs) >= 3 else blogs
    html_ok_count = 0
    for blog in latest_blogs:
        ok, missing = check_blog_html_structure(blog["url"])
        results["html_checks"].append({
            "number": blog["number"],
            "valid": ok,
            "missing_elements": missing
        })
        if ok:
            html_ok_count += 1
        else:
            results["issues"].append(f"博客 #{blog['number']} HTML结构不完整: {', '.join(missing)}")
    
    # 3. 检查服务器磁盘空间
    disk_pct, disk_ok = check_server_disk_space()
    results["server_disk"] = {
        "percent_used": disk_pct,
        "healthy": disk_ok
    }
    if disk_pct is not None and disk_pct > 80:
        results["issues"].append(f"博客服务器磁盘使用率高: {disk_pct}%")
    elif disk_pct is None:
        results["issues"].append("无法检查博客服务器磁盘空间")
    
    # 4. 检查服务器博客文件数量
    server_count = check_server_blog_count()
    results["server_blog_count"] = server_count
    if server_count != len(blogs):
        results["issues"].append(
            f"博客记录数 ({len(blogs)}) 与服务器文件数 ({server_count}) 不一致"
        )
    
    # 5. 检查重复标题（仅作为信息，不作为错误，因为相同主题在不同日期可能重复）
    duplicates = check_duplicate_titles(records)
    results["duplicates"] = duplicates
    # 重复标题不加入issues列表，因为不同日期的相同主题是正常的
    
    # 6. 检查编号连续性（只检查记录中的编号，忽略1-39的历史断档）
    gaps = check_numbering_gaps(records)
    # 忽略1-39的断档（这些博客在系统建立前发布）
    real_gaps = [g for g in gaps if g >= 40]
    results["gaps"] = real_gaps
    if real_gaps:
        results["issues"].append(f"发现 {len(real_gaps)} 个编号断档: {real_gaps}")
    
    # 7. 检查服务器上的孤儿文件（不在记录中的文件）
    orphan_files = []
    if server_count > len(blogs):
        try:
            cmd = [
                "sshpass", "-p", SERVER_PASSWORD,
                "ssh", "-o", "StrictHostKeyChecking=no",
                f"{SERVER_USER}@{SERVER_HOST}",
                f"ls {WEB_DIR}/*.html"
            ]
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
            if result.returncode == 0:
                recorded_numbers = {b["number"] for b in blogs}
                for line in result.stdout.strip().split("\n"):
                    filename = Path(line).name
                    # 检查是否是编号文件
                    num_match = re.match(r'(\d+)\.html$', filename)
                    if num_match:
                        num = int(num_match.group(1))
                        if num not in recorded_numbers:
                            orphan_files.append(filename)
                    elif filename.endswith('.html'):
                        # 非编号HTML文件
                        orphan_files.append(filename)
        except Exception:
            pass
    results["orphan_files"] = orphan_files
    if orphan_files:
        results["issues"].append(f"发现 {len(orphan_files)} 个孤儿文件: {orphan_files}")
    
    # 汇总
    results["summary"] = {
        "url_accessible": f"{url_ok_count}/{len(recent_blogs)}",
        "html_valid": f"{html_ok_count}/{len(latest_blogs)}",
        "disk_healthy": disk_ok if disk_pct is not None else False,
        "count_match": server_count == len(blogs),
        "no_duplicates": len(duplicates) == 0,
        "no_gaps": len(real_gaps) == 0,
        "no_orphans": len(orphan_files) == 0,
        "overall_healthy": (
            url_ok_count == len(recent_blogs) and
            html_ok_count == len(latest_blogs) and
            (disk_ok if disk_pct is not None else False) and
            server_count == len(blogs) and
            len(real_gaps) == 0 and
            len(orphan_files) == 0
        )
    }
    
    # 输出
    if json_mode:
        print(json.dumps(results, indent=2, ensure_ascii=False))
    elif quiet_mode:
        if results["issues"]:
            for issue in results["issues"]:
                print(f"⚠️ {issue}")
            sys.exit(1)
        else:
            print("✅ 博客系统健康")
            sys.exit(0)
    else:
        print(f"📚 博客系统健康检查 ({len(blogs)} 篇博客)")
        print("=" * 60)
        print()
        print(f"🔗 URL可访问性: {url_ok_count}/{len(recent_blogs)} (最近5篇)")
        for check in results["url_checks"]:
            status = "✅" if check["accessible"] else "❌"
            print(f"   {status} #{check['number']}: HTTP {check['http_code']}")
        
        print()
        print(f"📝 HTML结构完整性: {html_ok_count}/{len(latest_blogs)} (最近3篇)")
        for check in results["html_checks"]:
            status = "✅" if check["valid"] else "❌"
            detail = "" if check["valid"] else f" - 缺失: {', '.join(check['missing_elements'])}"
            print(f"   {status} #{check['number']}{detail}")
        
        print()
        if disk_pct is not None:
            disk_status = "✅" if disk_ok else "❌"
            print(f"💾 服务器磁盘: {disk_status} {disk_pct}% 使用率")
        else:
            print(f"💾 服务器磁盘: ⚠️ 无法检查")
        
        print()
        count_status = "✅" if server_count == len(blogs) else "⚠️"
        print(f"📊 博客数量一致性: {count_status} 记录{len(blogs)} vs 服务器{server_count}")
        if orphan_files:
            for orphan in orphan_files:
                print(f"   ⚠️ 孤儿文件: {orphan}")
        
        print()
        gap_status = "✅" if not real_gaps else f"⚠️ {len(real_gaps)}个"
        print(f"🔢 编号连续性: {gap_status}")
        if real_gaps:
            print(f"   断档编号: {real_gaps}")
        
        print()
        if results["issues"]:
            print("⚠️ 发现问题:")
            for issue in results["issues"]:
                print(f"   • {issue}")
        else:
            print("✅ 博客系统完全健康")
        
        print()
        print("=" * 60)
    
    # 返回退出码
    if results["issues"]:
        sys.exit(1)
    sys.exit(0)

if __name__ == "__main__":
    main()
