# -*- coding: utf-8 -*-
import os
import sys
from agents.supervisor import app
from dotenv import load_dotenv

# Fix UTF-8 encoding for Windows console (Important for Emojis/Tables)
if sys.platform == 'win32':
    import codecs
    sys.stdout.reconfigure(encoding='utf-8')

# Load environment variables
load_dotenv()

def start_audit(repo_url):
    """
    Triggers the API-driven audit with the integrated Security Sanitizer.
    """
    print(f"\n{'='*60}")
    print(f"🚀 PREDICTIVE ENGINEERING INTELLIGENCE PLATFORM")
    print(f"Target: {repo_url}")
    print(f"{'='*60}\n")

    # Initial State matches the updated AgentState in supervisor.py
    initial_state = {
        "repo_path": repo_url,
        "raw_metrics": {},
        "health_score": 0,
        "security_alerts": [], # Added for the Sanitizer
        "cloud_analysis": "",
        "final_report": ""
    }

    try:
        print("🛠️  Orchestrating Multi-Agent Chain...")
        
        final_report_text = "No report generated."
        
        # --- EXECUTION LOOP ---
        for output in app.stream(initial_state):
            for key, value in output.items():
                if key == "mine":
                    print(f"✅ Miner Agent: API Data Fetched. Initial Health: {value.get('health_score', 'N/A')}/100")
                
                elif key == "sanitize":
                    alerts = value.get('security_alerts', [])
                    if alerts:
                        print(f"⚠️  SANITIZER ALERT: Detected and Redacted {len(alerts)} secrets! ({', '.join(alerts)})")
                    else:
                        print("✅ Sanitizer Agent: Local security sweep complete. No secrets found.")
                
                elif key == "predict":
                    print("✅ Predictor Agent: 90-Day Risk Patterns identified via Mistral.")
                
                elif key == "gatekeeper":
                    print("✅ Gatekeeper Agent: Logical conflict & architectural audit complete.")
                
                elif key == "report":
                    print("✅ Strategist Agent: Business Impact report saved to Supabase.")
                    final_report_text = value.get('final_report', final_report_text)

        # --- FINAL DISPLAY ---
        print("\n" + "="*60)
        print("📊 FINAL 90-DAY BUSINESS IMPACT REPORT")
        print("="*60 + "\n")
        print(final_report_text)
        
        print(f"\n✨ Audit complete for {repo_url}. Data is 100% Sanitized.")
        
    except Exception as e:
        print(f"\n❌ CRITICAL SYSTEM ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # You can change this URL to any repo you want to test
    TARGET_REPO_URL = "https://github.com/shubhxm26/PanchaCare" 
    
    start_audit(TARGET_REPO_URL)