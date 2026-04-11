# -*- coding: utf-8 -*-
import os
import threading
import json
import re
import requests
from flask import Flask, redirect, request, session, jsonify, render_template_string
from flask_cors import CORS
from agents.supervisor import app as langgraph_app, SentinelVault  # Added SentinelVault import
from core.database import AuditDatabase
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

# Professional CORS handling for React/Vite development
CORS(app, resources={r"/*": {"origins": ["http://localhost:5173", "http://localhost:3000", "http://localhost:5000"]}})

# GitHub Credentials
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

# --- AUTH ROUTES ---

@app.route('/')
def index():
    return '''
        <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
            <h1>Predictive Engineering Intelligence</h1>
            <p>Structured AI Audits for Enterprise Leadership</p>
            <a href="/login">
                <button style="background:#2ea44f; color:white; padding:15px 30px; border:none; border-radius:6px; font-size:18px; cursor:pointer; font-weight:bold;">
                    Connect GitHub & Start API-Audit
                </button>
            </a>
        </div>
    '''

@app.route('/login')
def login():
    if not CLIENT_ID:
        return jsonify({"error": "GitHub Client ID missing"}), 500
    github_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo,user:email&redirect_uri=http://localhost:5000/callback"
    return redirect(github_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    if not code: return redirect('http://localhost:5173?error=no_code')
    
    try:
        res = requests.post("https://github.com/login/oauth/access_token",
            data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code},
            headers={"Accept": "application/json"})
        access_token = res.json().get("access_token")
        if access_token:
            session['github_token'] = access_token
            os.environ["GITHUB_TOKEN"] = access_token
            return redirect(f'http://localhost:5173?token={access_token}')
    except Exception as e:
        return redirect(f'http://localhost:5173?error=callback_error')

# --- EXTERNAL API ENDPOINTS ---

@app.route('/api/v1/health-badge/<repo_name>', methods=['GET'])
def get_health_badge(repo_name):
    """API for external dashboards to show project health status"""
    db = AuditDatabase()
    report = db.get_latest_report(repo_name)
    if not report: return jsonify({"error": "No audit found"}), 404
    
    return jsonify({
        "repo": repo_name,
        "health_score": report['health_score'],
        "status": "HEALTHY" if report['health_score'] > 75 else "BANKRUPT",
        "color": "#2ea44f" if report['health_score'] > 75 else "#FF4757"
    })

@app.route('/api/v1/heatmap/<path:repo_name>', methods=['GET'])
def get_heatmap_data(repo_name):
    """Provides Heatmap coordinates based on Churn and Entropy"""
    db = AuditDatabase()
    vault = SentinelVault()
    report = db.get_latest_report(repo_name)
    
    if not report:
        return jsonify({"error": "No audit found"}), 404
    
    try:
        # DECRYPT RAW METRICS
        raw_encrypted = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_encrypted)
        analytics = json.loads(decrypted_metrics)
        
        entropy_data = analytics.get('entropy', {})
        heatmap = []
        for path, stats in entropy_data.items():
            churn_factor = min(50, stats.get('total_touches', 0) * 5)
            entropy_factor = stats.get('author_concentration', 0) * 0.5
            heat_score = int(churn_factor + entropy_factor)
            
            heatmap.append({
                "file": path, "value": heat_score, "touches": stats.get('total_touches'),
                "concentration": stats.get('author_concentration'), "is_silo": stats.get('is_knowledge_silo'),
                "owner": stats.get('primary_owner')
            })
        return jsonify(sorted(heatmap, key=lambda x: x['value'], reverse=True))
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/timeline/<path:repo_name>', methods=['GET'])
def get_timeline_data(repo_name):
    """Provides dynamic 90-day risk milestones based on health score"""
    db = AuditDatabase()
    vault = SentinelVault()
    report = db.get_latest_report(repo_name)
    
    if not report:
        return jsonify({"error": "No audit found"}), 404
    
    try:
        # DECRYPT RAW METRICS
        raw_encrypted = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_encrypted)
        analytics = json.loads(decrypted_metrics)
        
        health_score = report.get('health_score', 0)
        timeline = analytics.get('timeline', [])
        show_timeline = analytics.get('show_timeline', health_score < 75)
        
        return jsonify({
            "repo": repo_name,
            "health_score": health_score,
            "show_timeline": show_timeline,
            "timeline": timeline,
            "narratives": analytics.get('narratives', {})
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/finance/<path:repo_name>', methods=['GET'])
def get_financial_risk(repo_name):
    """API for Executive Dashboard to pull financial loss metrics"""
    db = AuditDatabase()
    vault = SentinelVault()
    report = db.get_latest_report(repo_name)
    
    if not report:
        return jsonify({"error": "No audit found for this repository"}), 404
    
    try:
        # DECRYPT RAW METRICS & FINAL REPORT
        raw_encrypted_metrics = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_encrypted_metrics)
        analytics = json.loads(decrypted_metrics)

        raw_encrypted_report = report.get('report_text', '{}')
        decrypted_report = vault.decrypt_data(raw_encrypted_report)
        try:
            exec_summary = json.loads(decrypted_report)
        except:
            exec_summary = decrypted_report
        
        return jsonify({
            "financials": analytics.get('revenue_model', {}),
            "knowledge_silos": analytics.get('entropy', {}),
            "dependency_risks": analytics.get('dependency_risks', []),
            "health_score": report.get('health_score'),
            "executive_summary": exec_summary,
            "raw_metrics": analytics,
            "decryption_verified": True
        })
    except Exception as e:
        print(f"Error parsing finance data: {e}")
        return jsonify({"error": "Decryption failed"}), 500

@app.route('/api/analyze', methods=['POST'])
def analyze_repo():
    """Main Agentic Pipeline: Mines, Sanitizes, Predicts, and Reports"""
    try:
        data = request.get_json(force=True) if request.is_json else request.form
        repo_full_name = data.get('full_name')
        token = request.headers.get('Authorization', '').replace('Bearer ', '')
        
        if not repo_full_name or not token:
            return jsonify({"error": "Auth Token and Repo Name required"}), 400
        
        os.environ["GITHUB_TOKEN"] = token
        repo_url = f"https://github.com/{repo_full_name}"
        
        # Capture optional financial config from CEO UI
        fin_config = data.get('financial_config', {"avg_salary": 8000, "cost_per_bug": 500})

        initial_state = {
            "repo_path": repo_url, "raw_metrics": {}, "health_score": 0,
            "analytics": {}, "security_alerts": [], "cloud_analysis": "", "final_report": "",
            "financial_config": fin_config
        }
        
        print(f"🚀 [Sentinel] Initiating Audit for {repo_full_name}...")
        
        accumulated_data = {
            "health_score": 0, "security_alerts": [], "cloud_analysis": "",
            "final_report": "", "analytics": {}
        }
        
        for output in langgraph_app.stream(initial_state):
            if 'mine' in output:
                node = output['mine']
                accumulated_data['health_score'] = node.get('health_score', 0)
                accumulated_data['analytics'] = node.get('analytics', {})
            
            if 'sanitize' in output:
                accumulated_data['security_alerts'] = output['sanitize'].get('security_alerts', [])
            
            if 'predict' in output:
                accumulated_data['cloud_analysis'] = output['predict'].get('cloud_analysis', '')
            
            if 'report' in output:
                report_raw = output['report'].get('final_report', '{}')
                try:
                    accumulated_data['final_report'] = json.loads(report_raw)
                except:
                    accumulated_data['final_report'] = report_raw

        formatted_alerts = [{"type": a, "count": 1, "color": "#FF4757", "percentage": 100} for a in accumulated_data['security_alerts']]
        raw_metrics = accumulated_data['analytics']

        result = {
            "status": "success",
            "repo": repo_full_name,
            "health_score": accumulated_data['health_score'],
            "metrics": {
                "total_issues": len(formatted_alerts),
                "files_analyzed": len(raw_metrics.get('churn_metrics', {})),
                "lines_of_code": sum([max(0, int(stats.get('total_touches', 0)) * 15) for stats in raw_metrics.get('entropy', {}).values()])
            },
            "financials": raw_metrics.get('revenue_model', {}),
            "knowledge_silos": raw_metrics.get('entropy', {}),
            "security_alerts": formatted_alerts,
            "executive_summary": accumulated_data['final_report'],
            "raw_analysis": accumulated_data['cloud_analysis'],
            "analytics": raw_metrics,
            "raw_metrics": {"overall_complexity": {"avg_cc": 10}, "bug_patterns": {"total_bug_fixes": 0}} # Mock for UI safety
        }
        
        return jsonify(result), 200
        
    except Exception as e:
        print(f"❌ Analysis Error: {str(e)}")
        return jsonify({"error": str(e), "status": "error"}), 500
    
@app.route('/api/repos', methods=['GET'])
def get_user_repos():
    token = request.headers.get('Authorization', '').replace('Bearer ', '')
    if not token:
        return jsonify({"error": "No token provided"}), 401
    
    headers = {"Authorization": f"token {token}"}
    res = requests.get("https://api.github.com/user/repos", headers=headers)
    
    if res.status_code == 200:
        return jsonify(res.json())
    return jsonify({"error": "Failed to fetch repos"}), res.status_code

@app.route('/webhook', methods=['POST'])
def github_webhook():
    payload = request.json
    event_type = request.headers.get('X-GitHub-Event')
    
    # Trigger on Pull Requests or new Pushes to those PRs
    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            repo_full_name = payload['repository']['full_name']
            repo_url = payload['repository']['clone_url']
            
            # Extract the specific branch being merged
            branch = payload['pull_request']['head']['ref']
            
            print(f"🚀 [Autonomous] PR Event: {repo_full_name} | Branch: {branch}")
            
            # Start the AI Audit in the background
            thread = threading.Thread(
                target=run_background_audit, 
                args=(repo_full_name, branch, repo_url)
            )
            thread.start()
            
            return jsonify({"status": "Autonomous Audit Triggered"}), 202

    return jsonify({"status": "Event Ignored"}), 200

def run_background_audit(repo_name, branch, repo_url):
    """Executes the full LangGraph pipeline without human intervention"""
    print(f"🤖 [Agentic OS] Starting Unsupervised Audit for {repo_name}...")
    
    # We pass the branch name so the Miner knows exactly which code to audit
    initial_state = {
        "repo_path": repo_url,
        "branch": branch, # Ensure your GitForensics class can handle branch switching
        "raw_metrics": {}, 
        "health_score": 0,
        "analytics": {}, 
        "security_alerts": [], 
        "cloud_analysis": "", 
        "final_report": "",
        "financial_config": {"avg_salary": 8000, "cost_per_bug": 500} # Auto-config for CEO
    }
    
    try:
        # This will run all nodes: Mine -> Sanitize -> Predict -> Report (Save to DB & Telegram)
        langgraph_app.invoke(initial_state)
        print(f"✅ [Autonomous] Success: DB Updated & Telegram Sent for {repo_name}")
    except Exception as e:
        print(f"❌ [Autonomous] Critical Failure: {str(e)}")
if __name__ == '__main__':
    app.run(port=5000, debug=True)