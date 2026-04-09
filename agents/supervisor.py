from langgraph.graph import StateGraph, END
from typing import TypedDict

class AgentState(TypedDict):
    repo_path: str
    raw_metrics: dict
    risk_assessment: dict
    final_report: str

def forensic_node(state: AgentState):
    # Calls GitForensics to get churn and complexity
    # This happens locally
    engine = GitForensics(state['repo_path'])
    metrics = engine.analyze_hotspots()
    return {"raw_metrics": metrics}

def report_node(state: AgentState):
    # Sends summarized metrics to Gemini for CEO report
    # No raw code is sent, only stats for privacy
    prompt = f"Summarize this risk for a CEO: {state['raw_metrics']}"
    # Call Gemini API here...
    return {"final_report": "Financial Risk: $..."}

# Construct Graph
workflow = StateGraph(AgentState)
workflow.add_node("mine", forensic_node)
workflow.add_node("report", report_node)
workflow.set_entry_point("mine")
workflow.add_edge("mine", "report")
workflow.add_edge("report", END)
app = workflow.compile()