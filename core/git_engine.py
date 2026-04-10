import requests
import os
import re
import base64
from datetime import datetime, timedelta, timezone
from radon.complexity import cc_visit

class GitForensics:
    def __init__(self, repo_url):
        """Initialize using GitHub API instead of local cloning"""
        parts = repo_url.rstrip('/').replace('.git', '').split('/')
        self.owner = parts[-2]
        self.repo_name = parts[-1]
        
        self.token = os.getenv("GITHUB_TOKEN")
        self.base_url = f"https://api.github.com/repos/{self.owner}/{self.repo_name}"
        self.headers = {
            "Authorization": f"token {self.token}",
            "Accept": "application/vnd.github.v3+json"
        }

    def _get(self, endpoint):
        """Helper for GitHub API GET requests"""
        response = requests.get(f"{self.base_url}{endpoint}", headers=self.headers)
        if response.status_code == 200:
            return response.json()
        return None

    def analyze_all(self):
        """Comprehensive API-based repository analysis"""
        print(f"🌐 [API Miner] Analyzing {self.owner}/{self.repo_name}...")
        
        # 1. Fetch recent commits (Increased per_page for better leaderboard)
        commits = self._get("/commits?per_page=100") 
        raw_history = []
        hotspots = {}
        bug_commits_count = 0
        bug_indicators = ['fix', 'bug', 'issue', 'error', 'fail', 'crash', 'regression']

        if commits:
            for c in commits:
                author_login = c.get('author', {}).get('login') if c.get('author') else "Unknown"
                msg = c['commit']['message']
                date_str = c['commit']['author']['date']
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                is_bug = any(ind in msg.lower() for ind in bug_indicators)
                if is_bug:
                    bug_commits_count += 1
                
                raw_history.append({
                    'date': date_obj, 
                    'msg': msg, 
                    'author': author_login,
                    'num_files': 1 
                })
                
                if len(raw_history) <= 5:
                    detail = self._get(f"/commits/{c['sha']}")
                    if detail:
                        for f in detail.get('files', []):
                            path = f['filename']
                            hotspots[path] = hotspots.get(path, 0) + 1

        # 2. Advanced Analysis Modules
        leaderboard = self.get_collaborator_leaderboard(raw_history)
        dependency_risks = self.analyze_dependencies() # <--- NEW: Dependency Scan
        sanitized = self.sanitize_logs(raw_history)
        avg_cc = self._get_complexity_via_api(hotspots)

        return {
            "churn_metrics": dict(sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:10]),
            "overall_complexity": {"avg_cc": avg_cc},
            "deployment_frequency": self.analyze_deployment_frequency(raw_history),
            "bug_patterns": {"total_bug_fixes": bug_commits_count},
            "sanitized_history": sanitized,
            "leaderboard": leaderboard,
            "dependency_risks": dependency_risks # <--- Added to return object
        }

    def analyze_dependencies(self):
        """Scans for compromised or outdated critical packages in requirements.txt"""
        # Demo Vulnerability Database
        vulnerability_db = {
            "requests": {"version": "2.25.0", "risk": "High", "issue": "Credential Leakage via Proxy"},
            "flask": {"version": "1.1.2", "risk": "Critical", "issue": "Remote Code Execution (RCE)"},
            "django": {"version": "2.2.10", "risk": "High", "issue": "SQL Injection vulnerability"},
            "lodash": {"version": "4.17.15", "risk": "Medium", "issue": "Prototype Pollution"}
        }
        
        # Attempt to fetch requirements.txt from root
        file_data = self._get("/contents/requirements.txt")
        alerts = []

        if file_data and 'content' in file_data:
            try:
                content = base64.b64decode(file_data['content']).decode('utf-8')
                for package, info in vulnerability_db.items():
                    # Check for exact version match (e.g., flask==1.1.2)
                    if f"{package}=={info['version']}" in content:
                        alerts.append({
                            "package": package,
                            "version": info['version'],
                            "risk": info['risk'],
                            "issue": info['issue']
                        })
                print(f"🛡️ [Dependency Guard] Found {len(alerts)} security risks.")
            except Exception as e:
                print(f"⚠️ Error parsing dependencies: {e}")
        
        return alerts

    def get_collaborator_leaderboard(self, history):
        stats = {}
        for entry in history:
            user = entry['author']
            if user and user.lower() != self.owner.lower() and user != "Unknown":
                stats[user] = stats.get(user, 0) + 1
        
        sorted_stats = sorted(stats.items(), key=lambda x: x[1], reverse=True)
        return [{"username": user, "commits": count} for user, count in sorted_stats]

    def _get_complexity_via_api(self, hotspots):
        top_files = sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:3]
        total_cc = 0
        count = 0
        
        for path, _ in top_files:
            if not path.endswith(('.py', '.js', '.ts', '.java')):
                continue
                
            content_data = self._get(f"/contents/{path}")
            if content_data and 'content' in content_data:
                try:
                    code = base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')
                    results = cc_visit(code)
                    total_cc += sum([r.complexity for r in results])
                    count += 1
                except:
                    continue
        return round(total_cc / max(count, 1), 2)

    def sanitize_logs(self, raw_commits):
        sanitized_data = []
        noise_patterns = [r"merge branch", r"merge pull request"]
        
        for commit in raw_commits:
            msg = commit['msg']
            if any(re.search(pattern, msg.lower()) for pattern in noise_patterns):
                continue
            
            sanitized_data.append({
                "date": str(commit['date']),
                "message": msg,
                "author": commit['author'],
                "files_count": commit['num_files']
            })
        return sanitized_data[:20]

    def analyze_deployment_frequency(self, history):
        now = datetime.now(timezone.utc)
        ninety_days_ago = now - timedelta(days=90)

        deploy_keywords = ['deploy', 'release', 'prod', 'staging', 'version']
        recent_deployments = [c for c in history if c['date'] > ninety_days_ago 
                             and any(k in c['msg'].lower() for k in deploy_keywords)]

        freq = len(recent_deployments) / 3 
        return {
            "recent_deployments_90d": len(recent_deployments),
            "deployment_frequency_per_month": round(freq, 2),
            "avg_time_between_deployments": round(30 / max(freq, 0.1), 2)
        }