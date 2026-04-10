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
    Triggers the API-driven audit without local cloning.
    """
    print(f"\n{'='*60}")
    print(f"🚀 API-DRIVEN ENGINEERING INTELLIGENCE PLATFORM")
    print(f"Target: {repo_url}")
    print(f"{'='*60}\n")

    # Initial State: 'repo_path' now holds the URL for the API calls
    initial_state = {
        "repo_path": repo_url,
        "raw_metrics": {},
        "health_score": 0,
        "cloud_analysis": "",
        "final_report": ""
    }

    try:
        print("🛠️  Orchestrating API Agents...")
        
        final_report_text = "No report generated."
        
        # --- EXECUTION LOOP (Single Pass) ---
        for output in app.stream(initial_state):
            for key, value in output.items():
                if key == "mine":
                    print(f"✅ Miner Agent: API Data Fetched. Health: {value.get('health_score', 'N/A')}/100")
                elif key == "predict":
                    print("✅ Predictor Agent: 90-Day Risk Patterns identified.")
                elif key == "gatekeeper":
                    print("✅ Gatekeeper: Logical conflict check complete.")
                elif key == "report":
                    print("✅ Strategist Agent: Business Impact report saved to Supabase.")
                    final_report_text = value.get('final_report', final_report_text)

        # --- FINAL DISPLAY ---
        print("\n" + "="*60)
        print("📊 FINAL 90-DAY BUSINESS IMPACT REPORT")
        print("="*60 + "\n")
        print(final_report_text)
        
        print(f"\n✨ Audit complete for {repo_url}. No local cleanup required (API-based).")
        
    except Exception as e:
        print(f"\n❌ CRITICAL SYSTEM ERROR: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    # The CEO/User just provides the GitHub URL
    TARGET_REPO_URL = "https://github.com/victor-02-var/labpass-frontend.git" 
    
    start_audit(TARGET_REPO_URL)