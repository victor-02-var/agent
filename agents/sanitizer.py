import re

def sanitization_node(state):
    """
    Scans incoming repository data for secrets and redacts them 
    locally before the cloud LLM processes the risk report.
    """
    # We look at the raw metrics or code snippets gathered by the miner
    raw_content = str(state.get("raw_metrics", "")) 
    
    secret_patterns = {
        "Generic API Key": r'(?i)(api_key|apikey|secret|password|token)["\s:]+["\s]*([a-zA-Z0-9_\-]{16,})',
        "GitHub Token": r'ghp_[a-zA-Z0-9]{36}',
        "Bearer Token": r'Bearer\s+[a-zA-Z0-9\-\._~\+\/]+'
    }
    
    sanitized_content = raw_content
    alerts = []

    for label, pattern in secret_patterns.items():
        if re.search(pattern, sanitized_content):
            alerts.append(label)
            sanitized_content = re.sub(pattern, f"<{label}_REDACTED>", sanitized_content)

    # We update the state with sanitized data and a security flag
    return {
        "raw_metrics": sanitized_content,
        "security_alerts": alerts
    }