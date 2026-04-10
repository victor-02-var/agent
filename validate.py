# -*- coding: utf-8 -*-
"""
Validation script for the Predictive Engineering Intelligence Platform
"""

def validate_imports():
    """Validate that all required modules can be imported"""
    print("🔍 Validating imports...")

    try:
        import langgraph
        print("✅ LangGraph imported")
    except ImportError as e:
        print(f"❌ LangGraph import failed: {e}")
        return False

    try:
        from core.git_engine import GitForensics
        print("✅ Git Engine imported")
    except ImportError as e:
        print(f"❌ Git Engine import failed: {e}")
        return False

    try:
        from core.database import AuditDatabase
        print("✅ Database module imported")
    except ImportError as e:
        print(f"❌ Database import failed: {e}")
        return False

    try:
        from agents.supervisor import app
        print("✅ Supervisor imported")
    except ImportError as e:
        print(f"❌ Supervisor import failed: {e}")
        return False

    try:
        from agents.miner_agent import MinerAgent
        print("✅ Miner Agent imported")
    except ImportError as e:
        print(f"❌ Miner Agent import failed: {e}")
        return False

    try:
        from agents.risk_agent import RiskAgent
        print("✅ Risk Agent imported")
    except ImportError as e:
        print(f"❌ Risk Agent import failed: {e}")
        return False

    try:
        from agents.ceo_agent import CEOAgent
        print("✅ CEO Agent imported")
    except ImportError as e:
        print(f"❌ CEO Agent import failed: {e}")
        return False

    return True

def validate_environment():
    """Validate environment variables"""
    print("\n🔍 Validating environment...")

    import os
    from dotenv import load_dotenv
    load_dotenv()

    required_vars = ['GITHUB_TOKEN', 'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY']
    optional_vars = ['GOOGLE_API_KEY', 'OLLAMA_BASE_URL']

    for var in required_vars:
        if os.getenv(var):
            print(f"✅ {var} configured")
        else:
            print(f"❌ {var} missing")
            return False

    for var in optional_vars:
        if os.getenv(var):
            print(f"✅ {var} configured")
        else:
            print(f"⚠️ {var} not configured (optional)")

    return True

def test_basic_functionality():
    """Test basic functionality of core components"""
    print("\n🔍 Testing basic functionality...")

    try:
        from core.git_engine import GitForensics

        # Test with current directory (should work even if not a git repo)
        engine = GitForensics(".")
        metrics = engine.analyze_all()
        print("✅ Git Engine analysis completed")
        print(f"   Found {metrics.get('overall_complexity', {}).get('file_count', 0)} files")

    except Exception as e:
        print(f"❌ Git Engine test failed: {e}")
        return False

    try:
        from agents.miner_agent import MinerAgent

        miner = MinerAgent(".")
        result = miner.analyze_codebase()
        print("✅ Miner Agent test completed")
        print(f"   Health Score: {result['health_score']}/100")

    except Exception as e:
        print(f"❌ Miner Agent test failed: {e}")
        return False

    return True

if __name__ == "__main__":
    print("🚀 Predictive Engineering Intelligence Platform - Validation")
    print("=" * 70)

    success = True

    if not validate_imports():
        success = False

    if not validate_environment():
        success = False

    if not test_basic_functionality():
        success = False

    print("\n" + "=" * 70)
    if success:
        print("✅ All validations passed! The platform is ready to use.")
        print("\nTo run the analysis:")
        print("  python main.py")
        print("\nTo test with a specific repository, modify the repo_url in main.py")
    else:
        print("❌ Some validations failed. Please fix the issues above.")

    print("=" * 70)