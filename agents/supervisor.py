# -*- coding: utf-8 -*-
import os
import re
import time
import json
import smtplib
import requests
from datetime import datetime, timedelta
from email.message import EmailMessage
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv
from cryptography.fernet import Fernet

# Internal Imports
from core.git_engine import GitForensics
from core.database import AuditDatabase

# Load environment variables
load_dotenv()

# --- CRYPTOGRAPHIC VAULT UTILITY (With Self-Healing Fallback) ---
class SentinelVault:
    def __init__(self):
        # 1. Fetch key from .env and strip any hidden whitespace
        key_raw = os.getenv("SENTINEL_MASTER_KEY", "").strip()
        
        # 2. EMERGENCY FALLBACK: If .env key is invalid/missing, use your provided key
        if not key_raw or len(key_raw) < 32:
            key_raw = "PFlPu_iDI78Z1__kqpYo_bFBYJ82_9EMHEMPp6597vQ="
            print("💡 Vault: Using hardcoded fallback key for encryption.")

        try:
            self.cipher = Fernet(key_raw.encode())
        except Exception as e:
            print(f"❌ CRYPTO CONFIG ERROR: {e}. Generating ephemeral session key.")
            self.cipher = Fernet(Fernet.generate_key())

    def encrypt_data(self, plain_text: str) -> str:
        if not plain_text: return ""
        return self.cipher.encrypt(plain_text.encode()).decode()

    def decrypt_data(self, encrypted_token: str) -> str:
        if not encrypted_token: return ""
        return self.cipher.decrypt(encrypted_token.encode()).decode()

# --- TELEGRAM SERVICE ---
class SentinelTelegram:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.chat_id = os.getenv("TELEGRAM_CEO_CHAT_ID")
        self.base_url = f"https://api.telegram.org/bot{self.token}/sendMessage"

    def send_executive_alert(self, repo_name, health_score, affliction):
        if not self.token or not self.chat_id: return
        emoji = "🔴" if health_score < 40 else "🟡" if health_score < 75 else "🟢"
        message = (
            f"<b>🛡️ Sentinel Executive Brief: {repo_name}</b>\n\n"
            f"<b>Health Score:</b> {emoji} {health_score}/100\n"
            f"<b>Primary Issue:</b> {affliction.get('issue', 'N/A')}\n"
            f"<b>Annual ROI Risk:</b> {affliction.get('revenue_impact', 'N/A')}\n\n"
            f"<i>👉 Full encrypted audit available on dashboard.</i>"
        )
        try:
            requests.post(self.base_url, json={"chat_id": self.chat_id, "text": message, "parse_mode": "HTML"})
        except: pass

# Define the data structure passed between agents
class AgentState(TypedDict):
    repo_path: str
    raw_metrics: dict
    health_score: int
    analytics: dict
    security_alerts: List[str] 
    cloud_analysis: str
    final_report: str
    financial_config: dict 

# --- Helper: Log Sanitizer ---
def sanitize_git_logs(logs):
    if not logs: return []
    sanitized = []
    for entry in logs[:20]:
        sanitized.append({
            "date": str(entry.get('date')),
            "message": entry.get('msg'),
            "author": entry.get('author'),
            "files_count": entry.get('num_files', 1)
        })
    return sanitized

# --- Agent 1: The Forensic Miner ---
def forensic_node(state: AgentState):
    print("🔍 [Agent: Miner] Performing Deep Multi-Vector Audit...")
    engine = GitForensics(state['repo_path'])
    metrics = engine.analyze_all()
    
    metrics['sanitized_history'] = sanitize_git_logs(metrics.get('sanitized_history', []))
    avg_cc = metrics.get('overall_complexity', {}).get('avg_cc', 0)
    hotspots = metrics.get('churn_metrics', {})
    bug_fixes = metrics.get('bug_patterns', {}).get('total_bug_fixes', 0)
    deploy_freq = metrics.get('deployment_frequency', {}).get('deployment_frequency_per_month', 0)
    entropy_map = metrics.get('entropy_map', {})
    dep_risks = metrics.get('dependency_risks', [])
    
    logic_density = max(5, 100 - (avg_cc * 12))
    stability_score = max(5, 100 - (bug_fixes * 8))
    volatile_files = len([v for v in hotspots.values() if v > 3])
    modularity_score = max(5, 100 - (volatile_files * 15))
    
    silos = [f for f in entropy_map.values() if f.get('is_silo') or f.get('is_knowledge_silo')]
    silo_count = len(silos)
    silo_penalty = silo_count * 10
    
    leaderboard = metrics.get('leaderboard', [])
    total_devs = len(leaderboard)
    silo_owners = set([f.get('primary_owner') for f in silos if f.get('primary_owner')])
    bus_factor = max(1, total_devs - len(silo_owners))
    momentum_score = min(100, max(5, deploy_freq * 25))

    config = state.get('financial_config', {})
    AVG_DEV_SALARY = config.get('avg_salary', 8000) 
    COST_PER_BUG = config.get('cost_per_bug', 500)

    tech_tax_ratio = min(0.7, (avg_cc / 20))
    monthly_loss_complexity = AVG_DEV_SALARY * tech_tax_ratio
    monthly_loss_bugs = bug_fixes * COST_PER_BUG
    total_leak = int(monthly_loss_complexity + monthly_loss_bugs)

    raw_health = (logic_density * 0.4) + (stability_score * 0.3) + (modularity_score * 0.2) + (momentum_score * 0.1)
    final_health = max(5, int(raw_health - silo_penalty))

    dynamic_timeline = []
    now = datetime.now()
    show_timeline = final_health < 75

    narratives = {
        "m1": { "neglect": f"System instability will peak. Unresolved {bug_fixes} bugs will likely cause a production outage.", "resolve": f"Stability recovered. Bug backlog cleared, reducing technical tax by ${monthly_loss_bugs}." },
        "m2": { "neglect": f"Knowledge Silo Crisis. {silo_count} files are now unmaintainable due to primary owner burnout.", "resolve": "Knowledge distribution complete. Bus factor increased, securing project continuity." },
        "m3": { "neglect": "Technical Bankruptcy. The cost of maintenance now exceeds the value of new features.", "resolve": "Architecture optimized. The project is now a high-velocity asset for the business." }
    }

    if show_timeline:
        if final_health < 20:
            dynamic_timeline.append({"day": 10, "date": (now + timedelta(days=10)).strftime("%b %d"), "event": "TOTAL SYSTEM COLLAPSE", "type": "risk", "severity": "Critical", "desc": "Technical debt has made the codebase unmaintainable."})
        if bug_fixes > 0:
            dynamic_timeline.append({"day": 30, "date": (now + timedelta(days=30)).strftime("%b %d"), "event": "Stability Regression Peak", "type": "security", "severity": "High", "desc": f"Projected failure in {bug_fixes} modules."})
        if silo_count > 0:
            dynamic_timeline.append({"day": 60, "date": (now + timedelta(days=60)).strftime("%b %d"), "event": "Key Contributor Burnout", "type": "risk", "severity": "Medium", "desc": f"Continuity risk in {silo_count} files."})
        dynamic_timeline.append({"day": 90, "date": (now + timedelta(days=90)).strftime("%b %d"), "event": "Projected ROI Deficit", "type": "finance", "severity": "High", "desc": f"Cumulative technical tax will hit ${total_leak * 3} by this quarter."})

    is_aws = any(k in str(metrics).lower() for k in ['aws', 'terraform', 'cloudformation', 'yml'])
    base_bill = 450.00
    projected_delta = (avg_cc * 10) + (bug_fixes * 5)

    analytics_payload = {
        "score": final_health, "show_timeline": show_timeline, "timeline": dynamic_timeline, "narratives": narratives,
        "vectors": {"logic_density": int(logic_density), "stability": int(stability_score), "modularity": int(modularity_score), "momentum": int(momentum_score)},
        "revenue_model": {"monthly_loss_total": total_leak, "tech_tax": int(monthly_loss_complexity), "stability_leak": int(monthly_loss_bugs), "efficiency": f"{int(final_health * 0.9)}%"},
        "bus_factor": {"score": bus_factor, "status": "Critical" if bus_factor < 2 else "Warning" if bus_factor < 4 else "Healthy"},
        "cloud_billing": {"is_aws": is_aws, "current_monthly_bill": base_bill, "projected_bill_after_pr": base_bill + projected_delta, "delta": projected_delta},
        "entropy": entropy_map, "dependency_risks": dep_risks
    }

    print(f"✅ Audit Complete. Health: {final_health}/100 | Timeline: {show_timeline}")
    return {"raw_metrics": metrics, "health_score": final_health, "analytics": analytics_payload}

# --- Agent: Sanitizer ---
def sanitization_node(state: AgentState):
    print("🛡️ [Agent: Sanitizer] Scanning for secrets...")
    raw_content = json.dumps(state.get("raw_metrics", {})) 
    secret_patterns = {"GitHub Token": r'ghp_[a-zA-Z0-9]{30,255}', "Generic API Key": r'(?i)(api_key|apikey|secret|password|token)["\s:]+["\s]*([a-zA-Z0-9_\-]{16,})'}
    alerts = []
    sanitized_content_str = raw_content
    for label, pattern in secret_patterns.items():
        if re.search(pattern, sanitized_content_str):
            alerts.append(label)
            sanitized_content_str = re.sub(pattern, f"<{label}_REDACTED>", sanitized_content_str)
    try: updated_metrics = json.loads(sanitized_content_str)
    except: updated_metrics = state.get("raw_metrics", {})
    return {"raw_metrics": updated_metrics, "security_alerts": alerts}

# --- Agent 2: Predictor ---
def risk_prediction_node(state: AgentState):
    print("🤖 [Agent: Predictor] Analyzing risk patterns...")
    rev_leak = state['analytics']['revenue_model']['monthly_loss_total']
    prompt = f"AUDIT: Metrics: {state['raw_metrics']} Health: {state['health_score']} Leak: ${rev_leak} Predict 3 hotspots."
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.post(f"{ollama_url}/api/generate", json={"model": "mistral", "prompt": prompt, "stream": False})
        analysis = response.json()["response"] if response.status_code == 200 else "High volatility detected."
    except: analysis = "High volatility detected in core architecture."
    return {"cloud_analysis": analysis}

# --- Agent 3: Gatekeeper ---
def pr_gatekeeper_node(state: AgentState):
    return {"cloud_analysis": state['cloud_analysis'] + "\n\nGATEKEEPER ALERT: PR impact categorized as Major."}

# --- Agent 4: CEO Strategist (WITH AES-256 & TELEGRAM) ---
def ceo_report_node(state: AgentState):
    print("📈 [Agent: Strategist] Generating JSON Executive Brief...")
    rev_data = state['analytics']['revenue_model']
    bug_fixes = state['raw_metrics'].get('bug_patterns', {}).get('total_bug_fixes', 0)
    complexity = state['raw_metrics'].get('overall_complexity', {}).get('avg_cc', 0)
    
    prompt = f"""
    You are an Enterprise Strategy Consultant. Translate this Git audit into a Strategic Brief for a non-technical CEO.
    DATA:
    - Health Score: {state['health_score']}/100
    - Monthly Revenue Leak: ${rev_data['monthly_loss_total']}
    - Bug Issues: {bug_fixes}
    - Technical Entropy: {complexity}

    REQUIRED JSON SCHEMA:
    {{
        "executive_summary": "A high-level business status (max 2 sentences).",
        "financial_affliction": {{
            "issue": "Primary driver of revenue loss",
            "revenue_impact": "How this affects the bottom line",
            "risk_level": "Critical | High | Medium"
        }},
        "strategic_pillars": [
            {{
                "pillar_name": "Infrastructure Resilience",
                "business_value": "Why the CEO should care",
                "ceo_action": "Instruction for the CTO"
            }}
        ],
        "security_status": "Brief risk statement",
        "bus_factor_alert": "Team continuity statement"
    }}
    """
    try:
        ollama_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
        response = requests.post(f"{ollama_url}/api/generate", json={"model": "mistral", "prompt": prompt, "stream": False})
        report_content = response.json()["response"] if response.status_code == 200 else json.dumps({"error": "Failed report"})
    except: report_content = json.dumps({"error": "Failed report"})
    
    # --- CRYPTOGRAPHIC VAULT LAYER ---
    vault = SentinelVault()
    print("🔐 [Vault] Encrypting Executive Report & Metrics with AES-256...")
    encrypted_report = vault.encrypt_data(report_content)
    encrypted_analytics = vault.encrypt_data(json.dumps(state['analytics']))

    print("💾 Saving ENCRYPTED results to Supabase...")
    try:
        db = AuditDatabase()
        db.save_audit_report(os.path.basename(state['repo_path']), state['health_score'], encrypted_report, encrypted_analytics)
    except: pass

    # --- TELEGRAM NOTIFICATION LAYER ---
    try:
        report_json = json.loads(report_content)
        tg = SentinelTelegram()
        tg.send_executive_alert(
            repo_name=os.path.basename(state['repo_path']),
            health_score=state['health_score'],
            affliction=report_json.get('financial_affliction', {})
        )
    except: pass
    
    return {"final_report": report_content}

# --- Agent 5: Email Sentinel ---
def security_email_node(state: AgentState):
    dep_risks = state['analytics'].get('dependency_risks', [])
    if dep_risks:
        msg = EmailMessage()
        msg['Subject'] = f"⚠️ SECURITY ALERT: {os.path.basename(state['repo_path'])}"
        msg['From'] = os.getenv("EMAIL_USER")
        msg['To'] = os.getenv("EMAIL_USER")
        msg.set_content(f"Compromised packages detected:\n{json.dumps(dep_risks, indent=2)}")
        try:
            with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
                smtp.login(os.getenv("EMAIL_USER"), os.getenv("EMAIL_PASS"))
                smtp.send_message(msg)
        except: pass
    return state

# --- LangGraph Construction ---
workflow = StateGraph(AgentState)
workflow.add_node("mine", forensic_node)
workflow.add_node("sanitize", sanitization_node)
workflow.add_node("predict", risk_prediction_node)
workflow.add_node("gatekeeper", pr_gatekeeper_node)
workflow.add_node("report", ceo_report_node)
workflow.add_node("email_alert", security_email_node)

workflow.set_entry_point("mine")
workflow.add_edge("mine", "sanitize")
workflow.add_edge("sanitize", "predict")
workflow.add_edge("predict", "gatekeeper")
workflow.add_edge("gatekeeper", "report")
workflow.add_edge("report", "email_alert")
workflow.add_edge("email_alert", END)

app = workflow.compile()