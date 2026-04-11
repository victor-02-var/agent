# -*- coding: utf-8 -*-
import os
import threading
import json
import re
import requests
from flask import Flask, redirect, request, session, jsonify, render_template_string, send_file
from flask_cors import CORS
from agents.supervisor import app as langgraph_app, SentinelVault 
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

# --- HELPER: RECURSIVE DICT UNWRAPPER ---
def force_dict(obj):
    """Drills through any depth of lists to find a dictionary."""
    while isinstance(obj, list) and len(obj) > 0:
        obj = obj[0]
    return obj if isinstance(obj, dict) else {}

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

@app.route('/api/v1/health-badge/<path:repo_name>', methods=['GET'])
def get_health_badge(repo_name):
    """API for external dashboards to show project health status"""
    db = AuditDatabase()
    clean_name = os.path.basename(repo_name)
    report = db.get_latest_audit(clean_name)
    if not report: return jsonify({"error": "No audit found"}), 404
    
    return jsonify({
        "repo": clean_name,
        "health_score": report['health_score'],
        "status": "HEALTHY" if report['health_score'] > 75 else "BANKRUPT",
        "color": "#2ea44f" if report['health_score'] > 75 else "#FF4757"
    })

@app.route('/api/v1/heatmap/<path:repo_name>', methods=['GET'])
def get_heatmap_data(repo_name):
    db = AuditDatabase()
    vault = SentinelVault()
    
    # 1. Database Fetch
    raw_db_result = db.get_latest_audit(repo_name) or db.get_latest_audit(os.path.basename(repo_name))
    
    # --- CRITICAL FIX START: UNWRAP THE DB LIST ---
    report = raw_db_result
    while isinstance(report, list) and len(report) > 0:
        report = report[0]
    # --- CRITICAL FIX END ---

    if not report or not isinstance(report, dict):
        return jsonify([])
    
    try:
        # 2. Decrypt with Safety
        # Use report['key'] if it's a dict, or report.get()
        metrics_blob = report.get('raw_metrics', '{}')
        decrypted = vault.decrypt_data(metrics_blob)
        data_packet = json.loads(decrypted)
        
        # Recursive Peel Helper
        def peel(obj):
            while isinstance(obj, list) and len(obj) > 0:
                obj = obj[0]
            return obj

        analytics = peel(data_packet)
        if not isinstance(analytics, dict):
            return jsonify([])

        # 3. Target Entropy
        entropy = analytics.get('entropy', analytics.get('knowledge_silos', {}))
        entropy = peel(entropy)

        heatmap_results = []
        if isinstance(entropy, dict):
            for path, stats in entropy.items():
                s = peel(stats)
                if not isinstance(s, dict): continue

                heatmap_results.append({
                    "file": path,
                    "touches": s.get('total_touches', 1),
                    "concentration": s.get('author_concentration', 100),
                    "owner": s.get('primary_owner', 'Lead Dev'),
                    "value": int(s.get('total_touches', 1) * 2) 
                })
            
        return jsonify(heatmap_results)

    except Exception as e:
        print(f"❌ Heatmap Final Safety Triggered: {str(e)}")
        return jsonify([])

@app.route('/api/v1/contributor-audit/<path:repo_name>', methods=['GET'])
def get_contributor_audit(repo_name):
    """Analyzes the top contributor's impact, frequency, and code quality."""
    db = AuditDatabase()
    vault = SentinelVault()
    clean_name = os.path.basename(repo_name)
    report = db.get_latest_audit(clean_name)
    
    if not report:
        return jsonify({"error": f"Audit not found for {clean_name}"}), 404
    
    try:
        raw_encrypted = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_encrypted)
        analytics = force_dict(json.loads(decrypted_metrics))
        
        leaderboard = analytics.get('leaderboard', [])
        if not leaderboard:
            return jsonify({"error": "No contributor data available"}), 404
        
        mvp = force_dict(leaderboard[0])
        mvp_name = mvp.get('author', 'Unknown')
        
        total_commits = sum([force_dict(d).get('commits', 0) for d in leaderboard])
        mvp_commits = mvp.get('commits', 0)
        contribution_share = (mvp_commits / total_commits) * 100 if total_commits > 0 else 0
        
        avg_cc = analytics.get('overall_complexity', {}).get('avg_cc', 10)
        quality_score = max(5, 100 - (avg_cc * 4)) 

        return jsonify({
            "contributor": mvp_name,
            "metrics": {
                "commit_count": mvp_commits,
                "project_share": f"{int(contribution_share)}%",
                "work_frequency": "High" if contribution_share > 30 else "Balanced",
                "quality_index": f"{int(quality_score)}/100",
                "risk_factor": "Critical" if contribution_share > 50 else "Low"
            },
            "status": "Elite" if quality_score > 80 else "Technical Debt Driver"
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/branch-stats/<path:repo_name>', methods=['GET'])
def get_branch_stats(repo_name):
    """Fetches branch count for 3D dependency mapping motive."""
    token = os.getenv("GITHUB_TOKEN")
    headers = {"Authorization": f"token {token}"}
    url = f"https://api.github.com/repos/{repo_name}/branches"
    
    try:
        res = requests.get(url, headers=headers)
        branches = res.json()
        return jsonify({
            "total_branches": len(branches) if isinstance(branches, list) else 0,
            "repo_path": repo_name
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/v1/timeline/<path:repo_name>', methods=['GET'])
def get_timeline_data(repo_name):
    """Provides dynamic 90-day risk milestones based on health score"""
    db = AuditDatabase()
    vault = SentinelVault()
    clean_name = os.path.basename(repo_name)
    report = db.get_latest_audit(clean_name)
    
    if not report:
        return jsonify({"error": "No audit found"}), 404
    
    try:
        raw_encrypted = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_encrypted)
        analytics = force_dict(json.loads(decrypted_metrics))
        
        health_score = report.get('health_score', 0)
        timeline = analytics.get('timeline', [])
        show_timeline = analytics.get('show_timeline', health_score < 75)
        
        return jsonify({
            "repo": clean_name,
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
    clean_name = os.path.basename(repo_name)
    report = db.get_latest_audit(clean_name)
    
    if not report:
        return jsonify({"error": f"No audit found for {clean_name}"}), 404
    
    try:
        raw_encrypted_metrics = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_encrypted_metrics)
        analytics = force_dict(json.loads(decrypted_metrics))

        raw_encrypted_report = report.get('report_text', '{}')
        decrypted_report = vault.decrypt_data(raw_encrypted_report)
        try:
            exec_summary = force_dict(json.loads(decrypted_report))
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
        return jsonify({"error": "Decryption failed"}), 500

@app.route('/api/v1/report/download/<path:repo_name>', methods=['GET'])
def download_report(repo_name):
    db = AuditDatabase()
    vault = SentinelVault()
    clean_name = os.path.basename(repo_name)
    
    try:
        report = db.get_latest_audit(clean_name)
    except Exception as e:
        print(f"🔄 Database Connection Reset: {e}. Retrying...")
        db = AuditDatabase()
        report = db.get_latest_audit(clean_name)
    
    if not report:
        return jsonify({"error": "No audit found. Run a fresh audit first."}), 404

    try:
        raw_metrics_encrypted = report.get('raw_metrics', '{}')
        decrypted_metrics = vault.decrypt_data(raw_metrics_encrypted)
        analytics_raw = json.loads(decrypted_metrics)
        
        raw_report_encrypted = report.get('report_text', '{}')
        decrypted_report = vault.decrypt_data(raw_report_encrypted)
        try:
            exec_raw = json.loads(decrypted_report)
        except:
            exec_raw = {"executive_summary": str(decrypted_report)}

        clean_analytics = force_dict(analytics_raw)
        clean_exec = force_dict(exec_raw)

        combined_payload = {**clean_analytics, "executive_summary": clean_exec}

        from core.reporter import generate_pdf_report
        pdf_path = generate_pdf_report(clean_name, combined_payload)
        
        return send_file(os.path.abspath(pdf_path), as_attachment=True)
        
    except Exception as e:
        print(f"❌ PDF FATAL ERROR: {str(e)}")
        return jsonify({"error": f"Report Engine Failure: {str(e)}"}), 500

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
                "lines_of_code": sum([max(0, int(force_dict(stats).get('total_touches', 0)) * 15) for stats in raw_metrics.get('entropy', {}).values()])
            },
            "financials": raw_metrics.get('revenue_model', {}),
            "knowledge_silos": raw_metrics.get('entropy', {}),
            "security_alerts": formatted_alerts,
            "executive_summary": accumulated_data['final_report'],
            "raw_analysis": accumulated_data['cloud_analysis'],
            "analytics": raw_metrics
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
    
    if event_type == "pull_request":
        action = payload.get("action")
        if action in ["opened", "synchronize", "reopened"]:
            repo_full_name = payload['repository']['full_name']
            repo_url = payload['repository']['clone_url']
            branch = payload['pull_request']['head']['ref']
            
            print(f"🚀 [Autonomous] PR Event: {repo_full_name} | Branch: {branch}")
            
            thread = threading.Thread(
                target=run_background_audit, 
                args=(repo_full_name, branch, repo_url)
            )
            thread.start()
            return jsonify({"status": "Autonomous Audit Triggered"}), 202

    return jsonify({"status": "Event Ignored"}), 200

def run_background_audit(repo_name, branch, repo_url):
    print(f"🤖 [Agentic OS] Starting Unsupervised Audit for {repo_name}...")
    initial_state = {
        "repo_path": repo_url,
        "branch": branch,
        "raw_metrics": {}, 
        "health_score": 0,
        "analytics": {}, 
        "security_alerts": [], 
        "cloud_analysis": "", 
        "final_report": "",
        "financial_config": {"avg_salary": 8000, "cost_per_bug": 500}
    }
    try:
        langgraph_app.invoke(initial_state)
        print(f"✅ [Autonomous] Success: DB Updated & Telegram Sent for {repo_name}")
    except Exception as e:
        print(f"❌ [Autonomous] Critical Failure: {str(e)}")

if __name__ == '__main__':
    app.run(port=5000, debug=True)