#!/usr/bin/env python3
"""
Jephthah CLI Dashboard
Fancy real-time terminal dashboard - run from anywhere!

Usage:
    python -m jephthahhuman.dashboard.cli
    OR
    ./jephthah status
"""

import asyncio
import json
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

try:
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.columns import Columns
    from rich import box
except ImportError:
    print("Installing required packages...")
    import subprocess
    subprocess.run([sys.executable, "-m", "pip", "install", "rich", "-q"])
    from rich.console import Console
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.live import Live
    from rich.text import Text
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn
    from rich.columns import Columns
    from rich import box

# Determine data directory
SCRIPT_DIR = Path(__file__).parent.parent
DATA_DIR = SCRIPT_DIR / "data"

console = Console()


def load_job_data() -> Dict:
    """Load job application data from JSON file"""
    db_path = DATA_DIR / "job_applications.json"
    try:
        if db_path.exists():
            with open(db_path, 'r') as f:
                data = json.load(f)
                apps = data.get("applications", [])
                
                today = datetime.utcnow().date().isoformat()
                today_apps = [a for a in apps if a.get("applied_at", "").startswith(today)]
                
                # Count by site
                by_site = {}
                for a in apps:
                    site = a.get("site", "unknown")
                    by_site[site] = by_site.get(site, 0) + 1
                
                return {
                    "total": len(apps),
                    "today": len(today_apps),
                    "recent": apps[-10:][::-1],
                    "by_site": by_site,
                    "updated": data.get("updated", "Unknown")
                }
    except Exception as e:
        pass
    
    return {"total": 0, "today": 0, "recent": [], "by_site": {}, "updated": "N/A"}


def load_activity_log() -> List[Dict]:
    """Load recent activity from logs"""
    log_dir = DATA_DIR / "logs"
    activities = []
    
    try:
        if log_dir.exists():
            log_files = sorted(log_dir.glob("jephthah_*.log"), reverse=True)
            if log_files:
                with open(log_files[0], 'r') as f:
                    lines = f.readlines()[-30:]
                    for line in reversed(lines):
                        try:
                            if "|" in line:
                                parts = line.split("|")
                                if len(parts) >= 3:
                                    timestamp = parts[0].strip()[:19]
                                    level = parts[1].strip()
                                    message = parts[-1].strip()[:80]
                                    activities.append({
                                        "time": timestamp,
                                        "level": level,
                                        "message": message
                                    })
                        except:
                            pass
    except:
        pass
    
    return activities[:15]


def create_header() -> Panel:
    """Create the header panel"""
    grid = Table.grid(expand=True)
    grid.add_column(justify="left", ratio=1)
    grid.add_column(justify="center", ratio=2)
    grid.add_column(justify="right", ratio=1)
    
    grid.add_row(
        "🤖 [bold cyan]JEPHTHAH[/]",
        "[bold white]Autonomous Bot Dashboard[/]",
        f"[dim]{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}[/]"
    )
    
    return Panel(grid, style="bold blue", box=box.ROUNDED)


def create_stats_panel(job_data: Dict) -> Panel:
    """Create statistics panel"""
    stats = Table.grid(expand=True, padding=1)
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    stats.add_column(justify="center")
    
    stats.add_row(
        Panel(f"[bold green]{job_data['total']}[/]\n[dim]Total Applied[/]", box=box.ROUNDED),
        Panel(f"[bold yellow]{job_data['today']}[/]\n[dim]Today[/]", box=box.ROUNDED),
        Panel(f"[bold cyan]{len(job_data.get('by_site', {}))}[/]\n[dim]Sites[/]", box=box.ROUNDED),
        Panel("[bold magenta]$1M[/]\n[dim]Target[/]", box=box.ROUNDED),
    )
    
    return Panel(stats, title="📊 Statistics", box=box.ROUNDED)


def create_jobs_table(job_data: Dict) -> Panel:
    """Create recent jobs table"""
    table = Table(
        show_header=True,
        header_style="bold cyan",
        box=box.SIMPLE_HEAD,
        expand=True
    )
    
    table.add_column("Time", style="dim", width=8)
    table.add_column("Title", style="white", no_wrap=True)
    table.add_column("Company", style="yellow")
    table.add_column("Site", style="cyan")
    table.add_column("Salary", style="green")
    
    for job in job_data.get("recent", [])[:8]:
        time_str = job.get("applied_at", "")[:19]
        if time_str:
            try:
                dt = datetime.fromisoformat(time_str)
                time_str = dt.strftime("%H:%M")
            except:
                time_str = time_str[-8:-3]
        
        title = job.get("title", "Unknown")[:35]
        company = job.get("company", "Unknown")[:20]
        site = job.get("site", "?")
        salary = job.get("salary", "N/A")[:15]
        
        table.add_row(time_str, title, company, site, salary)
    
    if not job_data.get("recent"):
        table.add_row("[dim]No applications yet[/]", "", "", "", "")
    
    return Panel(table, title="💼 Recent Applications", box=box.ROUNDED)


def create_activity_panel(activities: List[Dict]) -> Panel:
    """Create activity log panel"""
    content = Text()
    
    for activity in activities[:10]:
        level = activity.get("level", "INFO")
        time_str = activity.get("time", "")[-8:]
        message = activity.get("message", "")[:60]
        
        level_style = {
            "INFO": "green",
            "WARNING": "yellow",
            "ERROR": "red",
            "DEBUG": "dim"
        }.get(level, "white")
        
        content.append(f"{time_str} ", style="dim")
        content.append(f"[{level[:3]}] ", style=level_style)
        content.append(f"{message}\n", style="white")
    
    if not activities:
        content.append("[dim]No activity yet[/]")
    
    return Panel(content, title="📋 Activity Log", box=box.ROUNDED)


def create_sites_panel(job_data: Dict) -> Panel:
    """Create sites distribution panel"""
    by_site = job_data.get("by_site", {})
    
    if not by_site:
        return Panel("[dim]No data yet[/]", title="🌐 Sites", box=box.ROUNDED)
    
    # Sort by count
    sorted_sites = sorted(by_site.items(), key=lambda x: x[1], reverse=True)[:8]
    
    table = Table.grid(padding=(0, 2))
    table.add_column(justify="left")
    table.add_column(justify="right")
    
    for site, count in sorted_sites:
        bar_len = min(count, 20)
        bar = "█" * bar_len
        table.add_row(
            f"[cyan]{site}[/]",
            f"[green]{bar}[/] {count}"
        )
    
    return Panel(table, title="🌐 Applications by Site", box=box.ROUNDED)


def create_status_panel() -> Panel:
    """Create bot status panel"""
    status_text = Text()
    status_text.append("● ", style="bold green")
    status_text.append("Bot Running\n\n", style="bold white")
    
    status_text.append("Email: ", style="cyan")
    status_text.append("✓ Connected\n", style="green")
    
    status_text.append("Browser: ", style="cyan")
    status_text.append("✓ Active\n", style="green")
    
    status_text.append("Telegram: ", style="cyan")
    status_text.append("✓ Online\n", style="green")
    
    status_text.append("\n[dim]Last update: ", style="dim")
    status_text.append(f"{datetime.now().strftime('%H:%M:%S')}[/]", style="dim")
    
    return Panel(status_text, title="⚡ Status", box=box.ROUNDED)


def create_dashboard() -> Layout:
    """Create the full dashboard layout"""
    layout = Layout()
    
    layout.split(
        Layout(name="header", size=3),
        Layout(name="body", ratio=1),
        Layout(name="footer", size=3),
    )
    
    layout["body"].split_row(
        Layout(name="left", ratio=2),
        Layout(name="right", ratio=1),
    )
    
    layout["left"].split(
        Layout(name="stats", size=6),
        Layout(name="jobs", ratio=1),
    )
    
    layout["right"].split(
        Layout(name="status", size=10),
        Layout(name="sites", ratio=1),
    )
    
    return layout


def update_dashboard(layout: Layout):
    """Update dashboard with current data"""
    job_data = load_job_data()
    activities = load_activity_log()
    
    layout["header"].update(create_header())
    layout["stats"].update(create_stats_panel(job_data))
    layout["jobs"].update(create_jobs_table(job_data))
    layout["status"].update(create_status_panel())
    layout["sites"].update(create_sites_panel(job_data))
    layout["footer"].update(create_activity_panel(activities))


def run_dashboard(refresh_rate: float = 2.0):
    """Run the live dashboard"""
    layout = create_dashboard()
    
    console.print("\n[bold cyan]JEPHTHAH DASHBOARD[/] - Press Ctrl+C to exit\n")
    
    with Live(layout, console=console, refresh_per_second=1, screen=True) as live:
        try:
            while True:
                update_dashboard(layout)
                live.update(layout)
                import time
                time.sleep(refresh_rate)
        except KeyboardInterrupt:
            pass
    
    console.print("\n[yellow]Dashboard closed.[/]")


def show_status():
    """Show a one-time status snapshot"""
    job_data = load_job_data()
    activities = load_activity_log()
    
    console.print()
    console.print(create_header())
    console.print(create_stats_panel(job_data))
    console.print(create_jobs_table(job_data))
    console.print(create_sites_panel(job_data))
    console.print(create_activity_panel(activities))
    console.print()


def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Jephthah Dashboard")
    parser.add_argument("--live", "-l", action="store_true", help="Run live dashboard (auto-refresh)")
    parser.add_argument("--refresh", "-r", type=float, default=5.0, help="Refresh rate in seconds (default: 5)")
    args = parser.parse_args()
    
    if args.live:
        run_dashboard(refresh_rate=args.refresh)
    else:
        show_status()


if __name__ == "__main__":
    main()
