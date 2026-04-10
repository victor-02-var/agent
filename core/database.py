import os
from supabase import create_client, Client
from dotenv import load_dotenv

load_dotenv()

class AuditDatabase:
    def __init__(self):
        url: str = os.getenv("SUPABASE_URL")
        key: str = os.getenv("SUPABASE_SERVICE_ROLE_KEY") # Use service role for backend writes
        self.supabase: Client = create_client(url, key)

    def save_audit_report(self, repo_name, health_score, report_text, raw_metrics):
        """
        Saves the final CEO report and technical metrics to the 'audits' table.
        """
        try:
            data = {
                "repo_name": repo_name,
                "health_score": int(health_score),
                "ceo_report": report_text,
                "raw_metrics": raw_metrics, # This stores the JSON from GitForensics
            }
            
            # Insert into the 'audits' table
            response = self.supabase.table("audits").insert(data).execute()
            
            print(f"✅ Audit for {repo_name} successfully saved to Supabase.")
            return response.data
        except Exception as e:
            print(f"❌ Database Error: {e}")
            return None

    def get_latest_audit(self, repo_name):
        """
        Retrieves the most recent audit for a specific repository.
        Useful for the CEO Dashboard 'Previous Scans' view.
        """
        response = self.supabase.table("audits") \
            .select("*") \
            .eq("repo_name", repo_name) \
            .order("created_at", desc=True) \
            .limit(1) \
            .execute()
        return response.data