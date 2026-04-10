# Predictive Engineering Intelligence Platform

A multi-agent AI system that analyzes GitHub/GitLab repositories to predict software failures, assess code health, and generate executive business reports.

## 🚀 Features

- **Multi-Agent Architecture**: Uses LangGraph for orchestrating specialized AI agents
- **Comprehensive Code Analysis**:
  - Code complexity metrics (using Radon)
  - Git history analysis (using PyDriller)
  - Test coverage trends
  - Deployment frequency analysis
  - Bug pattern detection
- **Predictive Risk Analysis**: AI-powered failure prediction for the next 90 days
- **Business Impact Reports**: Converts technical analysis into CEO-friendly business reports
- **Database Persistence**: Stores results in Supabase for historical tracking

## 🏗️ Architecture

### Agents
1. **Miner Agent**: Extracts technical metrics from codebases
2. **Risk Agent**: Predicts component failures using AI analysis
3. **CEO Agent**: Generates business impact reports for executives

### Core Components
- **Git Engine**: Handles repository analysis and metrics extraction
- **Database**: Supabase integration for data persistence
- **Supervisor**: LangGraph orchestration of the agent workflow

## 📋 Prerequisites

- Python 3.8+
- GitHub Personal Access Token
- Google AI API Key (optional, for cloud AI)
- Ollama (optional, for local AI models)
- Supabase account (for data storage)

## 🛠️ Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd predictive-engineering-platform
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up environment variables in `.env`:
```env
GITHUB_TOKEN=your_github_token
GOOGLE_API_KEY=your_google_ai_key
SUPABASE_URL=your_supabase_url
SUPABASE_SERVICE_ROLE_KEY=your_supabase_key
OLLAMA_BASE_URL=http://localhost:11434
```

## 🚀 Usage

Run the analysis on a GitHub repository:

```bash
python main.py
```

The system will:
1. Clone the target repository securely
2. Analyze code complexity, churn patterns, and deployment history
3. Predict potential failures in the next 90 days
4. Generate a business impact report for executives
5. Save results to Supabase

## 📊 Analysis Metrics

The platform analyzes:

- **Code Complexity**: Cyclomatic complexity using Radon
- **Churn Analysis**: Files most frequently modified
- **Test Coverage**: Ratio of test files to source files
- **Deployment Frequency**: Release patterns over time
- **Bug Patterns**: Frequency and hotspots of bug fixes
- **Health Scoring**: Overall codebase health (0-100)

## 🤖 AI Integration

The system supports multiple AI backends:

1. **Ollama (Local)**: Mistral/Llama models for privacy
2. **Google AI**: Gemini models for cloud processing
3. **Fallback Mode**: Rule-based analysis when AI unavailable

## 🗄️ Database Schema

Results are stored in Supabase with the following structure:

```sql
CREATE TABLE audits (
    id SERIAL PRIMARY KEY,
    repo_name TEXT,
    health_score INTEGER,
    ceo_report TEXT,
    raw_metrics JSONB,
    created_at TIMESTAMP DEFAULT NOW()
);
```

## 🔧 Configuration

### Environment Variables

- `GITHUB_TOKEN`: GitHub API access token
- `GOOGLE_API_KEY`: Google AI API key
- `SUPABASE_URL`: Supabase project URL
- `SUPABASE_SERVICE_ROLE_KEY`: Supabase service role key
- `OLLAMA_BASE_URL`: Ollama server URL (default: http://localhost:11434)

### Analysis Parameters

- Repository depth: Shallow clone for faster analysis
- Commit limit: Last 100 commits for churn analysis
- File types: Python, JavaScript, TypeScript, Java
- Time window: 90-day analysis window

## 📈 Sample Output

```
🚀 PREDICTIVE ENGINEERING INTELLIGENCE PLATFORM
Target: https://github.com/example/repo.git
============================================================

🧹 Cleaning up previous audit data...
📥 Securely cloning repo for analysis...
🛠️ Orchestrating Agents...
🔍 [Agent: Miner] Analysis Complete. Health: 75/100
🤖 [Agent: Predictor] Risk patterns identified.
📊 [Agent: Strategist] Business report generated.

EXECUTIVE SUMMARY
Codebase health score of 75/100 indicates moderate technical debt...

PROJECTED REVENUE AT RISK
$50K-$100K potential loss from system failures...

STRATEGIC RECOMMENDATION
1. 2-week refactoring sprint
2. Increase test coverage to 80%
3. Implement CI/CD improvements
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

## ⚠️ Disclaimer

This tool provides predictive analysis based on code metrics and patterns. Results should be used as guidance for technical decision-making, not as definitive predictions.
