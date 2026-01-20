"""
Jephthah Dashboard
Web-based monitoring dashboard for the autonomous bot
Run: python -m dashboard.app
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path
from flask import Flask, render_template, jsonify
from loguru import logger

# Paths
BASE_DIR = Path(__file__).parent.parent
DATA_DIR = BASE_DIR / "data"

app = Flask(__name__)


def get_job_stats():
    """Get job application statistics"""
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
                    "recent": apps[-10:][::-1],  # Last 10, newest first
                    "by_site": by_site
                }
    except Exception as e:
        logger.error(f"Error reading job stats: {e}")
    
    return {"total": 0, "today": 0, "recent": [], "by_site": {}}


def get_email_stats():
    """Get email statistics (placeholder)"""
    return {
        "sent": 0,
        "received": 0,
        "replied": 0
    }


def get_activity_log():
    """Get recent activity"""
    log_dir = DATA_DIR / "logs"
    activities = []
    
    try:
        if log_dir.exists():
            log_files = sorted(log_dir.glob("jephthah_*.log"), reverse=True)
            if log_files:
                with open(log_files[0], 'r') as f:
                    lines = f.readlines()[-50:]  # Last 50 lines
                    for line in reversed(lines):
                        try:
                            # Parse loguru format
                            if "|" in line:
                                parts = line.split("|")
                                if len(parts) >= 3:
                                    timestamp = parts[0].strip()[:19]
                                    level = parts[1].strip()
                                    message = parts[-1].strip()[:100]
                                    activities.append({
                                        "time": timestamp,
                                        "level": level,
                                        "message": message
                                    })
                        except:
                            pass
    except Exception as e:
        logger.error(f"Error reading activity log: {e}")
    
    return activities[:20]


@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')


@app.route('/api/stats')
def api_stats():
    """API endpoint for all stats"""
    return jsonify({
        "jobs": get_job_stats(),
        "emails": get_email_stats(),
        "activity": get_activity_log(),
        "timestamp": datetime.utcnow().isoformat()
    })


@app.route('/api/jobs')
def api_jobs():
    """API endpoint for job data"""
    return jsonify(get_job_stats())


@app.route('/api/activity')
def api_activity():
    """API endpoint for activity log"""
    return jsonify(get_activity_log())


@app.route('/cli')
def cli_dashboard():
    """Terminal-friendly dashboard - access from anywhere with: curl http://IP:9847/cli"""
    jobs = get_job_stats()
    activity = get_activity_log()
    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S UTC")
    
    # Build ASCII dashboard
    output = f"""
╔══════════════════════════════════════════════════════════════════════════════╗
║  🤖 JEPHTHAH BOT                                              {now}  ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  📊 STATISTICS                                                               ║
║  ┌────────────────┬────────────────┬────────────────┬────────────────┐       ║
║  │  Total Applied │     Today      │    Target      │     Status     │       ║
║  │      {str(jobs['total']).center(6)}      │      {str(jobs['today']).center(4)}      │      $1M       │   🟢 RUNNING   │       ║
║  └────────────────┴────────────────┴────────────────┴────────────────┘       ║
╠══════════════════════════════════════════════════════════════════════════════╣
║  💼 RECENT APPLICATIONS                                                      ║
"""
    
    if jobs['recent']:
        for app in jobs['recent'][:5]:
            title = app.get('title', 'Unknown')[:25].ljust(25)
            company = app.get('company', 'N/A')[:15].ljust(15)
            site = app.get('site', 'N/A')[:10].ljust(10)
            output += f"║  • {title} | {company} | {site}              ║\n"
    else:
        output += "║  No applications yet                                                         ║\n"
    
    output += """╠══════════════════════════════════════════════════════════════════════════════╣
║  📋 ACTIVITY LOG                                                             ║
"""
    
    for log in activity[:8]:
        time = log.get('time', '')[-8:]
        level = log.get('level', 'INF')[:3]
        msg = log.get('message', '')[:55].ljust(55)
        output += f"║  {time} [{level}] {msg}  ║\n"
    
    output += """╚══════════════════════════════════════════════════════════════════════════════╝

ACCESS: curl http://72.61.147.187:9847/cli
LIVE:   watch -n5 'curl -s http://72.61.147.187:9847/cli'
"""
    
    return output, 200, {'Content-Type': 'text/plain; charset=utf-8'}


def main():
    """Run the dashboard server"""
    print("""
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║              JEPHTHAH DASHBOARD                               ║
    ║                                                               ║
    ║   Open http://localhost:5000 in your browser                  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
    """)
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
