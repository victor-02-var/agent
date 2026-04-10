import os
import requests
from flask import Flask, redirect, request, session, render_template_string
from agents.supervisor import app as langgraph_app
from dotenv import load_dotenv

load_dotenv()
app = Flask(__name__)
app.secret_key = os.urandom(24)

# GitHub Credentials
CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")

@app.route('/')
def index():
    return '''
        <div style="text-align:center; margin-top:100px; font-family:sans-serif;">
            <h1>Predictive Engineering Intelligence</h1>
            <p>90-Day Risk Forecasting for Executive Leadership</p>
            <a href="/login">
                <button style="background:#2ea44f; color:white; padding:15px 30px; border:none; border-radius:6px; font-size:18px; cursor:pointer; font-weight:bold;">
                    Connect GitHub & Start Audit
                </button>
            </a>
        </div>
    '''

@app.route('/login')
def login():
    github_url = f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope=repo"
    return redirect(github_url)

@app.route('/callback')
def callback():
    code = request.args.get('code')
    
    # Exchange code for access token
    res = requests.post(
        "https://github.com/login/oauth/access_token",
        data={"client_id": CLIENT_ID, "client_secret": CLIENT_SECRET, "code": code},
        headers={"Accept": "application/json"}
    )
    data = res.json()
    access_token = data.get("access_token")
    
    if not access_token:
        return "Authentication Failed", 400

    session['github_token'] = access_token
    os.environ["GITHUB_TOKEN"] = access_token

    # Fetch User's Repositories
    headers = {"Authorization": f"token {access_token}"}
    repo_res = requests.get("https://api.github.com/user/repos?sort=updated&per_page=10", headers=headers)
    repos = repo_res.json()

    # Create dropdown options
    options = "".join([f'<option value="{r["html_url"]}">{r["full_name"]}</option>' for r in repos])

    return render_template_string('''
        <div style="max-width:500px; margin:100px auto; font-family:sans-serif; border:1px solid #ddd; padding:40px; border-radius:12px; box-shadow: 0 4px 10px rgba(0,0,0,0.1);">
            <h2 style="color:#24292f; margin-top:0;">Select Repository</h2>
            <p style="color:#57606a;">Choose a project to perform the 90-Day Engineering Audit.</p>
            <form action="/audit" method="POST">
                <select name="repo_url" style="width:100%; padding:12px; border-radius:6px; border:1px solid #d0d7de; margin-bottom:20px; font-size:16px;">
                    {{ options|safe }}
                </select>
                <button type="submit" style="width:100%; background:#2ea44f; color:white; padding:12px; border:none; border-radius:6px; font-size:16px; cursor:pointer; font-weight:bold;">
                    Start Agentic Audit
                </button>
            </form>
        </div>
    ''', options=options)

@app.route('/audit', methods=['POST'])
def audit():
    repo_url = request.form.get('repo_url')
    access_token = session.get('github_token')

    if not repo_url or not access_token:
        return redirect('/')

    initial_state = {
        "repo_path": repo_url,
        "raw_metrics": {},
        "health_score": 0,
        "security_alerts": [],
        "cloud_analysis": "",
        "final_report": ""
    }

    print(f"--- STARTING AGENTIC AUDIT FOR: {repo_url} ---")
    final_output = {}
    
    # Run the LangGraph flow
    for output in langgraph_app.stream(initial_state):
        final_output = output
        print(f"Agent Update: {output}")

    # Extract report from the correct node (usually 'report' or 'supervisor')
    report = ""
    if 'report' in final_output:
        report = final_output['report'].get('final_report', 'No report generated.')
    elif 'supervisor' in final_output:
        report = final_output['supervisor'].get('final_report', 'No report generated.')

    return render_template_string('''
        <div style="max-width:900px; margin:50px auto; font-family:sans-serif; line-height:1.6;">
            <a href="/" style="text-decoration:none; color:#0969da; font-weight:bold;">← Run New Audit</a>
            <h1 style="border-bottom:2px solid #2ea44f; padding-bottom:10px; color:#24292f;">90-Day Strategic Forecast</h1>
            <div style="background:#fff; border:1px solid #ddd; padding:30px; border-radius:8px; white-space: pre-wrap; font-size:15px;">
                {{ report }}
            </div>
        </div>
    ''', report=report)

if __name__ == '__main__':
    app.run(port=5000, debug=True)