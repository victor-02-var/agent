import requests
import os
import re
import base64
from datetime import datetime, timedelta, timezone
from radon.complexity import cc_visit

class GitForensics:
    def __init__(self, repo_url):
        """Initialize using GitHub API instead of local cloning"""
        # Parse URL to get owner and repo name
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
        
        # 1. Fetch recent commits
        commits = self._get("/commits?per_page=50")
        raw_history = []
        hotspots = {}
        bug_commits_count = 0
        bug_indicators = ['fix', 'bug', 'issue', 'error', 'fail', 'crash', 'regression']

        if commits:
            for c in commits:
                msg = c['commit']['message']
                date_str = c['commit']['author']['date']
                date_obj = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
                
                is_bug = any(ind in msg.lower() for ind in bug_indicators)
                if is_bug:
                    bug_commits_count += 1
                
                # We keep the raw message here so the sanitizer can see it later
                raw_history.append({
                    'date': date_obj, 
                    'msg': msg, 
                    'num_files': 1 
                })
                
                # Sample hotspots from the latest commits
                if len(raw_history) <= 5:
                    detail = self._get(f"/commits/{c['sha']}")
                    if detail:
                        for f in detail.get('files', []):
                            path = f['filename']
                            hotspots[path] = hotspots.get(path, 0) + 1

        # 2. Sanitize logs for AI (This is where the Sanitizer Agent will look)
        sanitized = self.sanitize_logs(raw_history)

        # 3. Complexity analysis
        avg_cc = self._get_complexity_via_api(hotspots)

        return {
            "churn_metrics": dict(sorted(hotspots.items(), key=lambda x: x[1], reverse=True)[:10]),
            "overall_complexity": {"avg_cc": avg_cc},
            "deployment_frequency": self.analyze_deployment_frequency(raw_history),
            "bug_patterns": {"total_bug_fixes": bug_commits_count},
            "sanitized_history": sanitized # <--- The Sanitizer Agent scans this list
        }

    def _get_complexity_via_api(self, hotspots):
        """Fetches file content via API and runs CC analysis in memory"""
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
        """Pre-processes logs. NOTE: We keep the message intact so the Sanitizer Agent can scan for keys."""
        sanitized_data = []
        # We removed 'readme' and 'docs' from noise so we don't accidentally skip a leak in those files
        noise_patterns = [r"merge branch", r"merge pull request"]
        
        for commit in raw_commits:
            msg = commit['msg'] # Keep original casing for token detection
            if any(re.search(pattern, msg.lower()) for pattern in noise_patterns):
                continue
            
            sanitized_data.append({
                "date": str(commit['date']),
                "message": msg, # <--- Changed from 'impact' to 'message' for clarity
                "files_count": commit['num_files']
            })
        return sanitized_data[:20]

    def analyze_deployment_frequency(self, history):
        """Analyze deployment patterns"""
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