# -*- coding: utf-8 -*-
import os
import re
import time
from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from dotenv import load_dotenv

# Internal Imports
from core.git_engine import GitForensics
from core.database import AuditDatabase

# Load environment variables
load_dotenv()

# Define the data structure passed between agents
class AgentState(TypedDict):
    repo_path: str
    raw_metrics: dict
    health_score: int
    analytics: dict
    security_alerts: List[str]  # <--- Added for Sanitization alerts
    cloud_analysis: str
    final_report: str

# --- Helper: Log Sanitizer (Filters Git noise) ---
def sanitize_git_logs(logs):
    """Filters out noise and keeps high-impact commit messages to save tokens."""
    if not logs: return []
    sanitized = []
    noise = ["merge", "chore", "style", "readme", "docs", "cleanup"]
    
    for entry in logs:
        msg = entry.get('msg', '').lower()
        if not any(word in msg for word in noise) or any(word in msg for word in ["fix", "bug", "refactor"]):
            sanitized.append({
                "date": entry.get('date'),
                "impact": entry.get('msg'),
                "complexity_delta": entry.get('num_files', 1)
            })
    return sanitized[:15]

# --- Agent 1: The Forensic Miner ---
def forensic_node(state: AgentState):
    print("🔍 [Agent: Miner] Calculating Multi-Vector Health Metrics...")
    engine = GitForensics(state['repo_path'])
    metrics = engine.analyze_all()
    
    # 1. Log Cleanup
    metrics['sanitized_history'] = sanitize_git_logs(metrics.get('git_history', []))
    if 'git_history' in metrics: del metrics['git_history']
    
    # 2. Raw Data Extraction
    avg_cc = metrics.get('overall_complexity', {}).get('avg_cc', 0)
    hotspots = metrics.get('churn_metrics', {})
    bug_fixes = metrics.get('bug_patterns', {}).get('total_bug_fixes', 0)
    
    # 3. Vector Calculations (For Frontend Visuals)
    # A. Logic Density (Higher CC = Lower Score)
    logic_density = max(0, 100 - (avg_cc * 12))
    
    # B. Stability Score (More Bug Fixes = Lower Stability)
    stability_score = max(0, 100 - (bug_fixes * 7))
    
    # C. Modularity Score (High Churn in many files = Low Modularity)
    volatile_files = len([v for v in hotspots.values() if v > 3])
    modularity_score = max(0, 100 - (volatile_files * 15))
    
    # D. Deployment Momentum (Frequency based)
    deploy_freq = metrics.get('deployment_frequency', {}).get('deployment_frequency_per_month', 0)
    momentum_score = min(100, deploy_freq * 25) # Assumes 4+ deploys/month is perfect 100

    # 4. Final Aggregated Health Score
    final_health = int((logic_density * 0.4) + (stability_score * 0.3) + (modularity_score * 0.2) + (momentum_score * 0.1))

    # 5. Build the "Frontend-Ready" Analytics Object
    analytics_payload = {
        "score": final_health,
        "breakdown": {
            "logic_density": int(logic_density),
            "stability": int(stability_score),
            "modularity": int(modularity_score),
            "momentum": int(momentum_score)
        },
        "risk_labels": {
            "logic": "High" if logic_density < 50 else "Moderate" if logic_density < 75 else "Low",
            "bankruptcy_risk": "Critical" if final_health < 40 else "Monitor" if final_health < 70 else "Healthy"
        }
    }

    print(f"✅ Multi-Vector Audit Complete. Health: {final_health}/100")

    return {
        "raw_metrics": metrics,
        "health_score": final_health,
        "analytics": analytics_payload # <--- Pass this to your state/frontend
    }
# --- NEW Agent: The Local Security Sanitizer ---
def sanitization_node(state: AgentState):
    print("🛡️ [Agent: Sanitizer] Scanning for sensitive API keys & Secrets...")
    
    # Force the ENTIRE raw_metrics object into a string for deep scanning
    import json
    raw_content = json.dumps(state.get("raw_metrics", {})) 
    
    secret_patterns = {
        # Updated Regex to be more flexible with length (36 to 255 chars)
        "GitHub Token": r'ghp_[a-zA-Z0-9]{30,255}', 
        "Generic API Key": r'(?i)(api_key|apikey|secret|password|token)["\s:]+["\s]*([a-zA-Z0-9_\-]{16,})'
    }
    
    alerts = []
    sanitized_content_str = raw_content

    for label, pattern in secret_patterns.items():
        if re.search(pattern, sanitized_content_str):
            alerts.append(label)
            sanitized_content_str = re.sub(pattern, f"<{label}_REDACTED>", sanitized_content_str)

    # Convert back to dict so the next agent can read it properly
    try:
        updated_metrics = json.loads(sanitized_content_str)
    except:
        updated_metrics = state.get("raw_metrics", {})

    return {
        "raw_metrics": updated_metrics,
        "security_alerts": alerts
    }
# --- Agent 2: The Risk Predictor ---
def risk_prediction_node(state: AgentState):
    print("🤖 [Agent: Predictor] Analyzing 90-day risk patterns...")
    
    # LLM now receives the SANITIZED data
    prompt = f"""
    TECHNICAL RISK AUDIT:
    Metrics (Sanitized): {state['raw_metrics']}
    Current Health Score: {state['health_score']}/100
    Security Alerts Logged: {state.get('security_alerts', 'None')}
    
    Identify 3 hotspots and predict the specific component most likely to fail in 90 days.
    """

    try:
        import ollama
        client = ollama.Client(host='http://localhost:11434')
        response = client.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
        analysis = response['message']['content']
        print("✅ Using local Mistral for risk analysis")
    except Exception:
        print(f"⚠️ Ollama unavailable, trying Google AI...")
        try:
            from google import genai
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            analysis = response.text
            print("✅ Using Google AI for risk analysis")
        except Exception:
            analysis = "High volatility detected in core architecture."

    return {"cloud_analysis": analysis}

# --- Agent 3: The PR Gatekeeper ---
def pr_gatekeeper_node(state: AgentState):
    print("🛡️ [Agent: Gatekeeper] Evaluating logical conflicts & PR impact...")
    
    prompt = f"""
    CONTEXT: Incoming Pull Request Analysis
    AUDIT CONTEXT: {state['cloud_analysis']}
    SECURITY CONTEXT: {state.get('security_alerts', 'No breaches detected')}
    
    TASK: 
    1. Check if new changes touch 'Hotspots'.
    2. Identify 'Logical Conflicts'.
    3. Categorize Impact: [Major/Minor].
    """

    try:
        import ollama
        client = ollama.Client(host='http://localhost:11434')
        response = client.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
        gatekeeper_analysis = response['message']['content']
    except Exception:
        gatekeeper_analysis = "Gatekeeper Warning: Potential architectural overlap in core modules."

    return {"cloud_analysis": state['cloud_analysis'] + "\n\nGATEKEEPER ALERT:\n" + gatekeeper_analysis}

# --- Agent 4: The CEO Strategist ---
def ceo_report_node(state: AgentState):
    print("📈 [Agent: Strategist] Generating 90-Day Business Impact Report...")
    
    # Mention security catches in the report
    sec_context = f"BREACHES PREVENTED: {state.get('security_alerts', [])}" if state.get('security_alerts') else "Security Status: Clean"

    prompt = f"""
    Role: Strategic Business Consultant
    Input Analysis: {state['cloud_analysis']}
    Security Summary: {sec_context}
    Current Code Health: {state['health_score']}/100

    TASK: Convert analysis into a 90-Day Engineering Risk Forecast.
    Include the exact Markdown table with Timeline, Risk Level, Impact, and Revenue at Risk.
    
    IMPORTANT: If security alerts were found, add a section 'Security Firewall Update' praising the local redaction of accidental secrets.
    """

    try:
        from google import genai
        client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
        response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
        report_content = response.text
        print("✅ Using Gemini 2.0 Flash for CEO report")
    except Exception:
        report_content = "Default Audit: High technical risk detected."

    print("💾 Saving audit results to Supabase...")
    try:
        db = AuditDatabase()
        db.save_audit_report(
            repo_name=os.path.basename(state['repo_path']),
            health_score=state['health_score'],
            report_text=report_content,
            raw_metrics=str(state['raw_metrics'])[:1000] # Save snippets
        )
    except Exception as e:
        print(f"⚠️ Database save failed: {e}")

    return {"final_report": report_content}

# --- LangGraph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("mine", forensic_node)
workflow.add_node("sanitize", sanitization_node) # <--- Added node
workflow.add_node("predict", risk_prediction_node)
workflow.add_node("gatekeeper", pr_gatekeeper_node)
workflow.add_node("report", ceo_report_node)

workflow.set_entry_point("mine")
workflow.add_edge("mine", "sanitize")       # Flow: Mine -> Sanitize
workflow.add_edge("sanitize", "predict")    # Flow: Sanitize -> Predict
workflow.add_edge("predict", "gatekeeper")
workflow.add_edge("gatekeeper", "report")
workflow.add_edge("report", END)

app = workflow.compile()