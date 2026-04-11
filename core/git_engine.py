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

    def get_collaborator_leaderboard(self, history):
        """Excludes owner to find top external contributors."""
        stats = {}
        for entry in history:
            user = entry['author']
            if user and user.lower() != self.owner.lower() and user != "Unknown":
                stats[user] = stats.get(user, 0) + 1
        return [{"user": u, "count": c} for u, c in sorted(stats.items(), key=lambda x: x[1], reverse=True)]

    def analyze_dependencies(self):
        """Scans manifest files for compromised versions."""
        vulnerability_db = {
            "requests": {"version": "2.25.0", "risk": "High", "issue": "Credential Leakage"},
            "flask": {"version": "1.1.2", "risk": "Critical", "issue": "Remote Code Execution"},
            "django": {"version": "2.2.10", "risk": "High", "issue": "SQL Injection"},
            "lodash": {"version": "4.17.15", "risk": "Medium", "issue": "Prototype Pollution"}
        }
        file_data = self._get("/contents/requirements.txt")
        alerts = []

        if file_data and 'content' in file_data:
            try:
                content = base64.b64decode(file_data['content']).decode('utf-8')
                for package, info in vulnerability_db.items():
                    if f"{package}=={info['version']}" in content:
                        alerts.append({
                            "package": package,
                            "version": info['version'],
                            "risk_level": info['risk'],
                            "description": info['issue']
                        })
            except: pass
        return alerts

    def get_entropy_metrics(self, file_author_map):
        """Calculates Knowledge Silo risk based on author concentration."""
        entropy_results = {}
        for path, authors in file_author_map.items():
            total_changes = sum(authors.values())
            top_author_count = max(authors.values())
            concentration = (top_author_count / total_changes) * 100
            
            entropy_results[path] = {
                "total_touches": total_changes,
                "author_concentration": round(concentration, 1),
                "is_knowledge_silo": concentration > 80,
                "primary_owner": max(authors, key=authors.get)
            }
        return entropy_results

    def sanitize_logs(self, raw_commits):
        """Prepares logs for AI agents."""
        sanitized_data = []
        noise = [r"merge branch", r"merge pull request"]
        for commit in raw_commits:
            msg = commit['msg']
            if any(re.search(p, msg.lower()) for p in noise): continue
            sanitized_data.append({
                "date": str(commit['date']),
                "message": msg,
                "author": commit['author'],
                "impact_factor": commit['num_files']
            })
        return sanitized_data[:20]

    def analyze_deployment_frequency(self, history):
        """Measures CI/CD momentum."""
        now = datetime.now(timezone.utc)
        ninety_days_ago = now - timedelta(days=90)
        deploy_keywords = ['deploy', 'release', 'prod', 'staging', 'version']
        recent = [c for c in history if c['date'] > ninety_days_ago 
                  and any(k in c['msg'].lower() for k in deploy_keywords)]
        freq = len(recent) / 3 
        return {
            "deployments_90d": len(recent),
            "monthly_frequency": round(freq, 2),
            "health": "High" if freq >= 4 else "Low"
        }

    def _get_complexity_via_api(self, hotspots):
        """In-memory CC analysis of top files."""
        top_files = sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:3]
        total_cc, count = 0, 0
        for path, _ in top_files:
            if not path.endswith(('.py', '.js', '.ts', '.java')): continue
            content_data = self._get(f"/contents/{path}")
            if content_data and 'content' in content_data:
                try:
                    code = base64.b64decode(content_data['content']).decode('utf-8', errors='ignore')
                    results = cc_visit(code)
                    total_cc += sum([r.complexity for r in results])
                    count += 1
                except: continue
        return round(total_cc / max(count, 1), 2)

    def analyze_all(self):
        """Comprehensive API-based repository analysis for JSON-First architecture"""
        print(f"🌐 [API Miner] Mining Data for {self.owner}/{self.repo_name}...")
        
        # 1. Fetch deep history (Increased limit for stable entropy calculation)
        commits = self._get("/commits?per_page=100") 
        raw_history = []
        hotspots = {}
        file_author_map = {} 
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
                
                # Sample the most recent 20 commits for detailed Hotspot and Entropy mapping
                if len(raw_history) <= 20:
                    detail = self._get(f"/commits/{c['sha']}")
                    if detail:
                        for f in detail.get('files', []):
                            path = f['filename']
                            hotspots[path] = hotspots.get(path, 0) + 1
                            
                            if path not in file_author_map:
                                file_author_map[path] = {}
                            file_author_map[path][author_login] = file_author_map[path].get(author_login, 0) + 1

        # 2. Module Execution
        leaderboard = self.get_collaborator_leaderboard(raw_history)
        dependency_risks = self.analyze_dependencies()
        entropy_metrics = self.get_entropy_metrics(file_author_map)
        sanitized = self.sanitize_logs(raw_history)
        avg_cc = self._get_complexity_via_api(hotspots)

        # 3. Return Structured Data for API consumption
        return {
            "metadata": {
                "owner": self.owner,
                "repo": self.repo_name,
                "scan_time": datetime.now(timezone.utc).isoformat()
            },
            "churn_metrics": dict(sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:10]),
            "overall_complexity": {"avg_cc": avg_cc},
            "deployment_frequency": self.analyze_deployment_frequency(raw_history),
            "bug_patterns": {"total_bug_fixes": bug_commits_count},
            "sanitized_history": sanitized,
            "leaderboard": leaderboard,
            "dependency_risks": dependency_risks,
            "entropy_map": entropy_metrics
        }

    def sanitize_logs(self, raw_commits):
        """Prepares logs for AI agents."""
        sanitized_data = []
        noise = [r"merge branch", r"merge pull request"]
        for commit in raw_commits:
            msg = commit['msg']
            if any(re.search(p, msg.lower()) for p in noise): continue
            sanitized_data.append({
                "date": str(commit['date']),
                "message": msg,
                "author": commit['author'],
                "impact_factor": commit['num_files']
            })
        return sanitized_data[:20]