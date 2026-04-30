#!/usr/bin/env python3
"""
系统健康检查脚本 - 检查所有定时任务状态并生成报告

Usage:
    python3 health_check.py [--json] [--quiet]
"""

import json
import sys
import subprocess
import os
from datetime import datetime, timezone, timedelta
from typing import Dict, List, Any, Optional

# 北京时间
TZ_CN = timezone(timedelta(hours=8))


def get_gateway_info() -> tuple:
    """获取 Gateway URL 和 Token"""
    config_path = os.path.expanduser("~/.openclaw/openclaw.json")
    try:
        with open(config_path, 'r') as f:
            config = json.load(f)
        gateway = config.get("gateway", {})
        port = gateway.get("port", 18789)
        token = gateway.get("auth", {}).get("token", "")
        return f"http://127.0.0.1:{port}", token
    except Exception:
        return "http://127.0.0.1:18789", ""


def run_cron_list() -> List[Dict[str, Any]]:
    """获取所有 cron 任务列表 - 使用 --json 参数获取完整数据"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list", "--json"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            print(f"Error running cron list: {result.stderr}", file=sys.stderr)
            return run_cron_list_cli()

        # openclaw 的 JSON 输出前面可能有插件注册日志，需要找到 JSON 开始的位置
        output = result.stdout

        # JSON 对象以 {"jobs": [ 开头
        json_start = output.find('{\n  "jobs":')
        if json_start == -1:
            json_start = output.find('{"jobs":')

        if json_start != -1:
            data = json.loads(output[json_start:])
            return data.get("jobs", [])
        else:
            # 尝试直接解析整个输出
            data = json.loads(output)
            return data if isinstance(data, list) else data.get("jobs", [])
    except Exception as e:
        print(f"JSON parse failed: {e}", file=sys.stderr)
        return run_cron_list_cli()


def run_cron_list_cli() -> List[Dict[str, Any]]:
    """通过命令行获取 cron 列表（fallback）"""
    try:
        result = subprocess.run(
            ["openclaw", "cron", "list"],
            capture_output=True,
            text=True,
            timeout=30
        )
        if result.returncode != 0:
            return []
        return parse_cron_list_output(result.stdout)
    except Exception:
        return []


def parse_cron_list_output(output: str) -> List[Dict[str, Any]]:
    """解析 openclaw cron list 的文本输出（fallback）"""
    jobs = []
    lines = output.split("\n")
    
    header_idx = -1
    for i, line in enumerate(lines):
        if line.strip().startswith("ID") and "Name" in line:
            header_idx = i
            break
    
    if header_idx == -1:
        return jobs
    
    for i in range(header_idx + 1, len(lines)):
        line = lines[i]
        if not line.strip() or line.startswith("="):
            continue
        
        if len(line) > 36 and line[8] == "-" and line[13] == "-":
            job = parse_cron_line(line)
            if job:
                jobs.append(job)
    
    return jobs


def parse_cron_line(line: str) -> Optional[Dict[str, Any]]:
    """解析单行 cron 任务数据"""
    try:
        parts = line.split()
        if len(parts) < 6:
            return None
        
        job_id = parts[0]
        if len(job_id) != 36:
            return None
        
        status = "unknown"
        for part in parts:
            if part in ["ok", "error", "running", "paused"]:
                status = part
                break
        
        name_parts = []
        for part in parts[1:]:
            if part in ["cron", "in", "ago", "ok", "error", "running"]:
                break
            if "-" in part and len(part) > 10:
                break
            name_parts.append(part)
        
        name = " ".join(name_parts) if name_parts else "Unnamed"
        
        return {
            "id": job_id,
            "name": name,
            "enabled": True,
            "state": {
                "lastStatus": status,
                "lastRunAtMs": None,
                "nextRunAtMs": None,
                "lastDurationMs": 0,
                "consecutiveErrors": 0,
                "lastError": "",
                "lastDelivered": True,
                "lastDeliveryStatus": "unknown",
            },
            "schedule": {},
        }
    except Exception:
        return None


def format_duration(ms: int) -> str:
    """格式化持续时间"""
    if ms < 1000:
        return f"{ms}ms"
    elif ms < 60000:
        return f"{ms//1000}s"
    else:
        minutes = ms // 60000
        seconds = (ms % 60000) // 1000
        return f"{minutes}m{seconds}s"


def format_timestamp(ms: Optional[int]) -> str:
    """格式化时间戳为可读格式"""
    if not ms:
        return "N/A"
    dt = datetime.fromtimestamp(ms / 1000, tz=TZ_CN)
    return dt.strftime("%Y-%m-%d %H:%M")


def analyze_job(job: Dict[str, Any]) -> Dict[str, Any]:
    """分析单个任务状态"""
    state = job.get("state", {})
    
    # 确定状态等级
    status = state.get("lastStatus", "unknown")
    consecutive_errors = state.get("consecutiveErrors", 0)
    
    health = "healthy"
    if status == "error" or consecutive_errors > 0:
        health = "critical" if consecutive_errors >= 2 else "warning"
    
    return {
        "id": job.get("id", "unknown"),
        "name": job.get("name", "Unnamed"),
        "enabled": job.get("enabled", False),
        "schedule": job.get("schedule", {}),
        "lastStatus": status,
        "lastRunAt": format_timestamp(state.get("lastRunAtMs")),
        "nextRunAt": format_timestamp(state.get("nextRunAtMs")),
        "lastDuration": format_duration(state.get("lastDurationMs", 0)),
        "consecutiveErrors": consecutive_errors,
        "health": health,
        "lastError": state.get("lastError", ""),
        "lastDelivered": state.get("lastDelivered", False),
        "lastDeliveryStatus": state.get("lastDeliveryStatus", "unknown"),
    }


def check_disk_space() -> Dict[str, Any]:
    """检查磁盘空间"""
    try:
        import shutil
        stat = shutil.disk_usage("/")
        total = stat.total
        used = stat.used
        free = stat.free
        percent_used = (used / total) * 100

        status = "healthy"
        if percent_used > 90:
            status = "critical"
        elif percent_used > 80:
            status = "warning"

        return {
            "path": "/",
            "total_gb": round(total / (1024**3), 2),
            "used_gb": round(used / (1024**3), 2),
            "free_gb": round(free / (1024**3), 2),
            "percent_used": round(percent_used, 1),
            "status": status,
        }
    except Exception as e:
        return {"error": str(e), "status": "unknown"}


def check_workspace_size() -> Dict[str, Any]:
    """检查工作空间大小"""
    try:
        workspace = os.path.expanduser("~/.openclaw/workspace")
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(workspace):
            # 跳过 node_modules 和 .git
            if "node_modules" in dirpath or ".git" in dirpath:
                continue
            for f in filenames:
                fp = os.path.join(dirpath, f)
                if os.path.exists(fp):
                    total_size += os.path.getsize(fp)
                    file_count += 1

        return {
            "path": workspace,
            "size_mb": round(total_size / (1024**2), 2),
            "file_count": file_count,
        }
    except Exception as e:
        return {"error": str(e)}


def generate_report(jobs: List[Dict[str, Any]]) -> Dict[str, Any]:
    """生成完整健康报告"""
    analyzed = [analyze_job(job) for job in jobs]

    # 分类统计
    healthy = [j for j in analyzed if j["health"] == "healthy"]
    warning = [j for j in analyzed if j["health"] == "warning"]
    critical = [j for j in analyzed if j["health"] == "critical"]
    disabled = [j for j in analyzed if not j["enabled"]]

    # 配送问题
    delivery_issues = [j for j in analyzed
                      if j["lastDelivered"] is False and j["lastStatus"] == "ok"]

    # 系统健康检查
    disk = check_disk_space()
    workspace = check_workspace_size()

    return {
        "timestamp": datetime.now(TZ_CN).strftime("%Y-%m-%d %H:%M:%S"),
        "summary": {
            "total": len(analyzed),
            "healthy": len(healthy),
            "warning": len(warning),
            "critical": len(critical),
            "disabled": len(disabled),
            "deliveryIssues": len(delivery_issues),
        },
        "jobs": {
            "healthy": healthy,
            "warning": warning,
            "critical": critical,
            "disabled": disabled,
            "deliveryIssues": delivery_issues,
        },
        "system": {
            "disk": disk,
            "workspace": workspace,
        },
        "recommendations": generate_recommendations(analyzed, disk),
    }


def generate_recommendations(jobs: List[Dict[str, Any]], disk: Dict[str, Any]) -> List[str]:
    """生成改进建议"""
    recommendations = []

    critical_jobs = [j for j in jobs if j["health"] == "critical"]
    warning_jobs = [j for j in jobs if j["health"] == "warning"]

    if critical_jobs:
        names = ", ".join([j["name"] for j in critical_jobs])
        recommendations.append(
            f"🔴 紧急：{len(critical_jobs)}个任务连续失败2次以上: {names}"
        )

    if warning_jobs:
        names = ", ".join([j["name"] for j in warning_jobs])
        recommendations.append(
            f"🟡 警告：{len(warning_jobs)}个任务最近失败: {names}"
        )

    # 检查长时间未执行的任务
    now = datetime.now(TZ_CN)
    for job in jobs:
        if job["lastRunAt"] != "N/A":
            try:
                last_run = datetime.strptime(job["lastRunAt"], "%Y-%m-%d %H:%M")
                last_run = last_run.replace(tzinfo=TZ_CN)
                days_since = (now - last_run).days
                if days_since > 7 and job["enabled"]:
                    recommendations.append(
                        f"📅 {job['name']} 已 {days_since} 天未执行"
                    )
            except:
                pass

    # 磁盘空间检查
    if "percent_used" in disk:
        if disk["percent_used"] > 90:
            recommendations.append(
                f"💾 磁盘空间严重不足：已使用 {disk['percent_used']}% ({disk['used_gb']}GB / {disk['total_gb']}GB)"
            )
        elif disk["percent_used"] > 80:
            recommendations.append(
                f"💾 磁盘空间告急：已使用 {disk['percent_used']}% ({disk['used_gb']}GB / {disk['total_gb']}GB)"
            )

    if not recommendations:
        recommendations.append("✅ 所有任务状态正常，无需操作")

    return recommendations


def print_text_report(report: Dict[str, Any]):
    """打印文本格式报告"""
    print("=" * 60)
    print(f"🩺 系统健康检查报告")
    print(f"⏰ 检查时间: {report['timestamp']}")
    print("=" * 60)
    
    summary = report["summary"]
    print(f"\n📊 任务总览: {summary['total']} 个任务")
    print(f"   ✅ 健康: {summary['healthy']}")
    print(f"   🟡 警告: {summary['warning']}")
    print(f"   🔴 严重: {summary['critical']}")
    print(f"   ⚪ 禁用: {summary['disabled']}")
    if summary['deliveryIssues'] > 0:
        print(f"   📤 投递问题: {summary['deliveryIssues']}")
    
    # 系统信息
    system = report.get("system", {})
    disk = system.get("disk", {})
    workspace = system.get("workspace", {})
    
    if disk and "error" not in disk:
        print(f"\n💾 磁盘空间: /")
        status_icon = "✅" if disk["status"] == "healthy" else "🟡" if disk["status"] == "warning" else "🔴"
        print(f"   {status_icon} 已用: {disk['percent_used']}% ({disk['used_gb']}GB / {disk['total_gb']}GB)")
        print(f"   可用: {disk['free_gb']}GB")
    
    if workspace and "error" not in workspace:
        print(f"\n📁 工作空间: {workspace['path']}")
        print(f"   大小: {workspace['size_mb']}MB ({workspace['file_count']} 个文件)")
    
    # 严重任务
    if report["jobs"]["critical"]:
        print(f"\n{'='*60}")
        print("🔴 严重问题任务")
        print("=" * 60)
        for job in report["jobs"]["critical"]:
            print(f"\n  ❌ {job['name']}")
            print(f"     状态: {job['lastStatus']} | 连续失败: {job['consecutiveErrors']}次")
            print(f"     上次运行: {job['lastRunAt']} | 耗时: {job['lastDuration']}")
            if job['lastError']:
                print(f"     错误: {job['lastError']}")
    
    # 警告任务
    if report["jobs"]["warning"]:
        print(f"\n{'='*60}")
        print("🟡 警告任务")
        print("=" * 60)
        for job in report["jobs"]["warning"]:
            print(f"\n  ⚠️  {job['name']}")
            print(f"     状态: {job['lastStatus']} | 连续失败: {job['consecutiveErrors']}次")
            print(f"     上次运行: {job['lastRunAt']}")
    
    # 投递问题
    if report["jobs"]["deliveryIssues"]:
        print(f"\n{'='*60}")
        print("📤 投递问题 (任务成功但消息未送达)")
        print("=" * 60)
        for job in report["jobs"]["deliveryIssues"]:
            print(f"\n  📨 {job['name']}")
            print(f"     投递状态: {job['lastDeliveryStatus']}")
    
    # 建议
    print(f"\n{'='*60}")
    print("💡 改进建议")
    print("=" * 60)
    for rec in report["recommendations"]:
        print(f"  {rec}")
    
    print(f"\n{'='*60}")


def print_issues_only(report: Dict[str, Any]) -> bool:
    """仅打印有问题的任务，返回是否有问题"""
    has_issues = False

    # 严重任务
    if report["jobs"]["critical"]:
        has_issues = True
        print("🔴 严重问题任务")
        print("-" * 40)
        for job in report["jobs"]["critical"]:
            print(f"  ❌ {job['name']}")
            print(f"     状态: {job['lastStatus']} | 连续失败: {job['consecutiveErrors']}次")
            print(f"     上次运行: {job['lastRunAt']}")
            if job['lastError']:
                print(f"     错误: {job['lastError']}")
        print()

    # 警告任务
    if report["jobs"]["warning"]:
        has_issues = True
        print("🟡 警告任务")
        print("-" * 40)
        for job in report["jobs"]["warning"]:
            print(f"  ⚠️  {job['name']}")
            print(f"     状态: {job['lastStatus']} | 连续失败: {job['consecutiveErrors']}次")
            print(f"     上次运行: {job['lastRunAt']}")
        print()

    # 投递问题
    if report["jobs"]["deliveryIssues"]:
        has_issues = True
        print("📤 投递问题")
        print("-" * 40)
        for job in report["jobs"]["deliveryIssues"]:
            print(f"  📨 {job['name']}")
            print(f"     投递状态: {job['lastDeliveryStatus']}")
        print()

    return has_issues


def main():
    import argparse
    parser = argparse.ArgumentParser(description="系统健康检查")
    parser.add_argument("--json", action="store_true", help="输出JSON格式")
    parser.add_argument("--quiet", action="store_true", help="仅输出异常")
    args = parser.parse_args()

    jobs = run_cron_list()
    if not jobs:
        print("❌ 无法获取 cron 任务列表", file=sys.stderr)
        sys.exit(1)

    report = generate_report(jobs)

    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    elif args.quiet:
        # 仅输出有问题的任务
        has_issues = print_issues_only(report)
        if not has_issues:
            print("✅ 所有任务正常")
    else:
        print_text_report(report)
    
    # 如果有严重问题，退出码非0
    if report["summary"]["critical"] > 0:
        sys.exit(2)
    elif report["summary"]["warning"] > 0:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
