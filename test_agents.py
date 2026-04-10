# -*- coding: utf-8 -*-
"""
Test script for the Predictive Engineering Intelligence Platform
"""

import os
import sys
from agents.miner_agent import MinerAgent
from agents.risk_agent import RiskAgent
from agents.ceo_agent import CEOAgent

def test_agents():
    """Test individual agents with sample data"""

    print("🧪 Testing Predictive Engineering Intelligence Platform")
    print("=" * 60)

    # Test Miner Agent
    print("\n1. Testing Miner Agent...")
    try:
        miner = MinerAgent(".")
        result = miner.analyze_codebase()
        print(f"✅ Miner Agent: Health Score {result['health_score']}/100")
        print("Sample metrics extracted successfully")
    except Exception as e:
        print(f"❌ Miner Agent failed: {e}")

    # Test Risk Agent
    print("\n2. Testing Risk Agent...")
    try:
        risk_agent = RiskAgent()
        sample_metrics = {
            "overall_complexity": {"avg_cc": 12.5},
            "test_coverage_trends": {"coverage_ratio": 0.6},
            "bug_patterns": {"bug_fix_frequency": 0.05}
        }
        result = risk_agent.predict_risks(sample_metrics, 75)
        print(f"✅ Risk Agent: {result['model_used']} model used")
        print("Risk analysis completed")
    except Exception as e:
        print(f"❌ Risk Agent failed: {e}")

    # Test CEO Agent
    print("\n3. Testing CEO Agent...")
    try:
        ceo_agent = CEOAgent()
        sample_analysis = "High complexity in core modules, moderate test coverage"
        result = ceo_agent.generate_business_report(sample_analysis, 75, sample_metrics)
        print(f"✅ CEO Agent: {result['model_used']} model used")
        print("Business report generated")
    except Exception as e:
        print(f"❌ CEO Agent failed: {e}")

    print("\n" + "=" * 60)
    print("🧪 Testing completed!")

if __name__ == "__main__":
    test_agents()