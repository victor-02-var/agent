# -*- coding: utf-8 -*-
"""
Miner Agent - Specialized in Git Forensics and Code Analysis
Responsible for extracting technical metrics from repositories
"""

from core.git_engine import GitForensics
from typing import Dict, Any

class MinerAgent:
    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.engine = GitForensics(repo_path)

    def analyze_codebase(self) -> Dict[str, Any]:
        """
        Perform comprehensive code analysis including:
        - Code complexity metrics
        - Churn analysis (hotspots)
        - Test coverage trends
        - Deployment frequency
        - Bug pattern analysis
        """
        print("🔍 [Miner Agent] Starting comprehensive codebase analysis...")

        try:
            metrics = self.engine.analyze_all()

            # Calculate health score based on multiple factors
            health_score = self._calculate_health_score(metrics)

            print(f"✅ [Miner Agent] Analysis complete. Health Score: {health_score}/100")

            return {
                "metrics": metrics,
                "health_score": health_score,
                "analysis_summary": self._generate_summary(metrics, health_score)
            }

        except Exception as e:
            print(f"❌ [Miner Agent] Analysis failed: {e}")
            return {
                "metrics": {},
                "health_score": 0,
                "analysis_summary": f"Analysis failed: {str(e)}"
            }

    def _calculate_health_score(self, metrics: Dict[str, Any]) -> int:
        """
        Calculate overall health score based on multiple metrics:
        - Complexity: Lower is better
        - Test coverage: Higher is better
        - Bug frequency: Lower is better
        - Deployment frequency: Moderate is better (not too frequent or infrequent)
        """
        score = 100

        # Complexity penalty (max -30 points)
        avg_complexity = metrics.get('overall_complexity', {}).get('avg_cc', 0)
        complexity_penalty = min(30, avg_complexity * 2)
        score -= complexity_penalty

        # Test coverage bonus/penalty (max ±20 points)
        coverage_ratio = metrics.get('test_coverage_trends', {}).get('coverage_ratio', 0)
        if coverage_ratio < 0.5:
            score -= 20
        elif coverage_ratio > 1.0:
            score += 10  # Good test coverage

        # Bug frequency penalty (max -25 points)
        bug_frequency = metrics.get('bug_patterns', {}).get('bug_fix_frequency', 0)
        bug_penalty = min(25, bug_frequency * 100)
        score -= bug_penalty

        # Deployment frequency assessment (max ±15 points)
        deploy_freq = metrics.get('deployment_frequency', {}).get('deployment_frequency_per_month', 0)
        if deploy_freq < 1:  # Less than monthly
            score -= 10
        elif deploy_freq > 12:  # More than weekly
            score -= 15
        else:
            score += 5  # Good deployment cadence

        return max(0, min(100, int(score)))

    def _generate_summary(self, metrics: Dict[str, Any], health_score: int) -> str:
        """Generate a human-readable summary of the analysis"""

        complexity = metrics.get('overall_complexity', {})
        test_coverage = metrics.get('test_coverage_trends', {})
        bugs = metrics.get('bug_patterns', {})
        deployments = metrics.get('deployment_frequency', {})

        summary = f"""
CODEBASE ANALYSIS SUMMARY
========================
Health Score: {health_score}/100

COMPLEXITY METRICS:
- Average Complexity: {complexity.get('avg_cc', 0):.1f}
- Total Lines: {complexity.get('total_lines', 0):,}
- Files Analyzed: {complexity.get('file_count', 0)}

TEST COVERAGE:
- Test Files: {test_coverage.get('test_files_count', 0)}
- Source Files: {test_coverage.get('source_files_count', 0)}
- Coverage Ratio: {test_coverage.get('coverage_ratio', 0):.2%}

BUG PATTERNS:
- Total Bug Fixes: {bugs.get('total_bug_fixes', 0)}
- Bug Fix Frequency: {bugs.get('bug_fix_frequency', 0):.3f}

DEPLOYMENT PATTERNS:
- Deployments (90 days): {deployments.get('recent_deployments_90d', 0)}
- Frequency: {deployments.get('deployment_frequency_per_month', 0):.1f}/month
"""

        # Add risk assessment
        if health_score >= 80:
            summary += "\nRISK LEVEL: LOW - Codebase is healthy"
        elif health_score >= 60:
            summary += "\nRISK LEVEL: MEDIUM - Some areas need attention"
        elif health_score >= 40:
            summary += "\nRISK LEVEL: HIGH - Significant technical debt"
        else:
            summary += "\nRISK LEVEL: CRITICAL - Immediate refactoring required"

        return summary
