# -*- coding: utf-8 -*-
import os
import re
import time
from typing import TypedDict
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
    cloud_analysis: str
    final_report: str

# --- Helper: Log Sanitizer ---
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
    print("🔍 [Agent: Miner] Extracting and SANITIZING engineering metrics...")
    engine = GitForensics(state['repo_path'])
    metrics = engine.analyze_all()
    
    # 1. Sanitize history for the LLM
    metrics['sanitized_history'] = sanitize_git_logs(metrics.get('git_history', []))
    if 'git_history' in metrics: del metrics['git_history']
    
    # 2. Dynamic Health Score Calculation
    # We penalize for average complexity (avg_cc) and for every identified Hotspot
    avg_cc = metrics.get('overall_complexity', {}).get('avg_cc', 0)
    hotspot_count = len(metrics.get('churn_metrics', {}))
    
    # Formula: Start at 100, -15 per complexity unit, -5 per hotspot
    # This makes the score much more realistic for a demo
    calculated_score = max(0, min(100, int(100 - (avg_cc * 15) - (hotspot_count * 5))))
    
    return {
        "raw_metrics": metrics,
        "health_score": calculated_score
    }

# --- Agent 2: The Risk Predictor ---
def risk_prediction_node(state: AgentState):
    print("🤖 [Agent: Predictor] Analyzing 90-day risk patterns...")
    analysis = None
    prompt = f"""
    TECHNICAL RISK AUDIT:
    Metrics: {state['raw_metrics']}
    Current Health Score: {state['health_score']}/100
    
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
    CONTEXT: Incoming Pull Request for {os.path.basename(state['repo_path'])}
    AUDIT CONTEXT: {state['cloud_analysis']}
    RAW METRICS: {state['raw_metrics']}
    
    TASK: 
    1. Check if new changes touch 'Hotspots' (files with high CC or churn).
    2. Identify 'Logical Conflicts' (where new code breaks architectural patterns).
    3. Categorize Impact: [Major/Minor] and Blast Radius.
    """

    try:
        import ollama
        client = ollama.Client(host='http://localhost:11434')
        response = client.chat(model='mistral', messages=[{'role': 'user', 'content': prompt}])
        gatekeeper_analysis = response['message']['content']
        print("✅ Gatekeeper: Logical conflict check complete.")
    except Exception:
        gatekeeper_analysis = "Gatekeeper Warning: Potential architectural overlap in core modules."

    return {"cloud_analysis": state['cloud_analysis'] + "\n\nGATEKEEPER ALERT:\n" + gatekeeper_analysis}

# --- Agent 4: The CEO Strategist ---
def ceo_report_node(state: AgentState):
    print("📈 [Agent: Strategist] Generating 90-Day Business Impact Report...")
    report_content = None

    prompt = f"""
    Role: Strategic Business Consultant
    Input Analysis: {state['cloud_analysis']}
    Current Code Health: {state['health_score']}/100

    TASK: Convert analysis into a 90-Day Engineering Risk Forecast.
    
    YOU MUST INCLUDE THIS EXACT MARKDOWN TABLE:
    | Timeline | Risk Level | Technical Impact | Revenue at Risk |
    | :--- | :--- | :--- | :--- |
    | Day 0-30 | [Insert] | Minor bug regressions | $ [Insert] |
    | Day 31-60 | [Insert] | Hotspot module failure | $ [Insert] |
    | Day 61-90 | [Insert] | Complete system instability | $ [Insert] |

    Include:
    1. EXECUTIVE SUMMARY
    2. 90-DAY FORECAST (Explain table + Gatekeeper logical conflict alerts)
    3. STRATEGIC RECOMMENDATION (Fix vs Build)

    Tone: Professional, direct. Use currency ($).
    """

    try:
        import ollama
        client = ollama.Client(host='http://localhost:11434')
        response = client.chat(model='llama3', messages=[{'role': 'user', 'content': prompt}])
        report_content = response['message']['content']
        print("✅ Using local Llama 3 for CEO report")
    except Exception:
        try:
            from google import genai
            client = genai.Client(api_key=os.getenv("GOOGLE_API_KEY"))
            response = client.models.generate_content(model='gemini-2.0-flash', contents=prompt)
            report_content = response.text
            print("✅ Using Google AI for CEO report")
        except Exception:
            report_content = "Default Audit: High technical risk detected."

    print("💾 Saving audit results to Supabase...")
    try:
        db = AuditDatabase()
        db.save_audit_report(
            repo_name=os.path.basename(state['repo_path']),
            health_score=state['health_score'],
            report_text=report_content,
            raw_metrics=state['raw_metrics']
        )
    except Exception as e:
        print(f"⚠️ Database save failed: {e}")

    return {"final_report": report_content}

# --- LangGraph Construction ---
workflow = StateGraph(AgentState)

workflow.add_node("mine", forensic_node)
workflow.add_node("predict", risk_prediction_node)
workflow.add_node("gatekeeper", pr_gatekeeper_node)
workflow.add_node("report", ceo_report_node)

workflow.set_entry_point("mine")
workflow.add_edge("mine", "predict")
workflow.add_edge("predict", "gatekeeper")
workflow.add_edge("gatekeeper", "report")
workflow.add_edge("report", END)

app = workflow.compile()