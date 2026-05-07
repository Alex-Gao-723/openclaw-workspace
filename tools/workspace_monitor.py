#!/usr/bin/env python3
"""
工作空间监控脚本 - 跟踪磁盘和工作空间大小变化趋势
用于长期观察系统资源使用情况

Usage:
    python3 workspace_monitor.py [--json] [--quiet]
"""

import json
import os
import sys
import shutil
from datetime import datetime, timezone, timedelta
from pathlib import Path
from typing import Dict, Any, Optional

# 北京时间
TZ_CN = timezone(timedelta(hours=8))
DATA_FILE = os.path.expanduser("~/.openclaw/workspace/.workspace_monitor.json")


def get_current_metrics() -> Dict[str, Any]:
    """获取当前系统指标"""
    # 磁盘空间
    disk = shutil.disk_usage("/")
    
    # 工作空间大小
    workspace = os.path.expanduser("~/.openclaw/workspace")
    total_size = 0
    file_count = 0
    dir_count = 0
    
    for dirpath, dirnames, filenames in os.walk(workspace):
        if "node_modules" in dirpath or ".git" in dirpath or "__pycache__" in dirpath:
            continue
        dir_count += len(dirnames)
        for f in filenames:
            fp = os.path.join(dirpath, f)
            if os.path.exists(fp):
                total_size += os.path.getsize(fp)
                file_count += 1
    
    return {
        "timestamp": datetime.now(TZ_CN).isoformat(),
        "disk": {
            "total_gb": round(disk.total / (1024**3), 2),
            "used_gb": round(disk.used / (1024**3), 2),
            "free_gb": round(disk.free / (1024**3), 2),
            "percent_used": round((disk.used / disk.total) * 100, 1),
        },
        "workspace": {
            "size_mb": round(total_size / (1024**2), 2),
            "file_count": file_count,
            "dir_count": dir_count,
        }
    }


def load_history() -> list:
    """加载历史数据"""
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, 'r') as f:
                return json.load(f)
        except Exception:
            return []
    return []


def save_history(history: list):
    """保存历史数据"""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, 'w') as f:
        json.dump(history, f, indent=2)


def analyze_trends(current: Dict[str, Any], history: list) -> Dict[str, Any]:
    """分析趋势变化"""
    trends = {
        "disk_change_gb": None,
        "disk_change_percent": None,
        "workspace_change_mb": None,
        "workspace_change_files": None,
        "days_since_last": None,
    }
    
    if history:
        last = history[-1]
        try:
            last_time = datetime.fromisoformat(last["timestamp"])
            current_time = datetime.fromisoformat(current["timestamp"])
            trends["days_since_last"] = round((current_time - last_time).total_seconds() / 86400, 1)
        except:
            pass
        
        trends["disk_change_gb"] = round(
            current["disk"]["used_gb"] - last["disk"]["used_gb"], 2
        )
        trends["disk_change_percent"] = round(
            current["disk"]["percent_used"] - last["disk"]["percent_used"], 1
        )
        trends["workspace_change_mb"] = round(
            current["workspace"]["size_mb"] - last["workspace"]["size_mb"], 2
        )
        trends["workspace_change_files"] = (
            current["workspace"]["file_count"] - last["workspace"]["file_count"]
        )
    
    return trends


def generate_report(current: Dict[str, Any], history: list, trends: Dict[str, Any]) -> Dict[str, Any]:
    """生成完整报告"""
    recommendations = []
    
    # 磁盘空间告警
    disk_pct = current["disk"]["percent_used"]
    if disk_pct > 90:
        recommendations.append(f"🔴 磁盘空间严重不足：已使用 {disk_pct}%")
    elif disk_pct > 80:
        recommendations.append(f"🟡 磁盘空间告急：已使用 {disk_pct}%")
    
    # 趋势告警
    if trends.get("disk_change_gb") is not None:
        if trends["disk_change_gb"] > 1:
            recommendations.append(
                f"📈 磁盘使用增长：+{trends['disk_change_gb']}GB (自上次{trends['days_since_last']}天前)"
            )
        if trends.get("workspace_change_mb") and trends["workspace_change_mb"] > 10:
            recommendations.append(
                f"📈 工作空间增长：+{trends['workspace_change_mb']}MB (新增{trends['workspace_change_files']}个文件)"
            )
        if trends.get("workspace_change_mb") and trends["workspace_change_mb"] < -10:
            recommendations.append(
                f"📉 工作空间减小：{trends['workspace_change_mb']}MB (减少{abs(trends['workspace_change_files'])}个文件)"
            )
    
    if not recommendations:
        recommendations.append("✅ 系统资源使用正常")
    
    return {
        "timestamp": current["timestamp"],
        "current": current,
        "trends": trends,
        "history_count": len(history),
        "recommendations": recommendations,
    }


def print_text_report(report: Dict[str, Any]):
    """打印文本报告"""
    print(f"📊 工作空间监控报告 ({report['timestamp']})")
    print("=" * 50)
    
    current = report["current"]
    trends = report["trends"]
    
    print(f"\n💾 磁盘空间 (/)")
    print(f"   已用: {current['disk']['percent_used']}% ({current['disk']['used_gb']}GB / {current['disk']['total_gb']}GB)")
    print(f"   可用: {current['disk']['free_gb']}GB")
    if trends["disk_change_gb"] is not None:
        change = trends["disk_change_gb"]
        symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"   变化: {symbol} {change:+.2f}GB (近{trends['days_since_last']}天)")
    
    print(f"\n📁 工作空间 (~/.openclaw/workspace)")
    print(f"   大小: {current['workspace']['size_mb']}MB")
    print(f"   文件: {current['workspace']['file_count']}个")
    print(f"   目录: {current['workspace']['dir_count']}个")
    if trends["workspace_change_mb"] is not None:
        change = trends["workspace_change_mb"]
        symbol = "📈" if change > 0 else "📉" if change < 0 else "➡️"
        print(f"   变化: {symbol} {change:+.2f}MB (近{trends['days_since_last']}天)")
    
    print(f"\n📋 历史记录")
    print(f"   数据点: {report['history_count']}个")
    
    print(f"\n💡 建议")
    for rec in report["recommendations"]:
        print(f"   {rec}")
    
    print()


def print_json_report(report: Dict[str, Any]):
    """打印 JSON 报告"""
    print(json.dumps(report, indent=2, ensure_ascii=False))


def print_quiet_report(report: Dict[str, Any]):
    """仅打印异常信息"""
    has_issue = False
    for rec in report["recommendations"]:
        if not rec.startswith("✅"):
            print(rec)
            has_issue = True
    if not has_issue:
        print("✅ 系统资源使用正常")


def main():
    json_mode = "--json" in sys.argv
    quiet_mode = "--quiet" in sys.argv
    
    # 获取当前指标
    current = get_current_metrics()
    
    # 加载历史
    history = load_history()
    
    # 分析趋势
    trends = analyze_trends(current, history)
    
    # 生成报告
    report = generate_report(current, history, trends)
    
    # 保存数据
    history.append(current)
    # 保留最近 90 天的数据
    if len(history) > 90:
        history = history[-90:]
    save_history(history)
    
    # 输出报告
    if json_mode:
        print_json_report(report)
    elif quiet_mode:
        print_quiet_report(report)
    else:
        print_text_report(report)
    
    # 返回退出码
    disk_pct = current["disk"]["percent_used"]
    if disk_pct > 90:
        sys.exit(2)
    elif disk_pct > 80:
        sys.exit(1)
    sys.exit(0)


if __name__ == "__main__":
    main()
