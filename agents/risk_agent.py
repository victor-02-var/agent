# -*- coding: utf-8 -*-
"""
Risk Agent - Specialized in Predictive Risk Analysis
Uses AI to predict component failures and technical risks
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class RiskAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.ollama_host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def predict_risks(self, metrics: Dict[str, Any], health_score: int) -> Dict[str, Any]:
        """
        Analyze metrics and predict potential failures in the next 90 days
        """
        print("🎯 [Risk Agent] Analyzing risk patterns and predicting failures...")

        try:
            # Try Ollama first (local models)
            analysis = self._analyze_with_ollama(metrics, health_score)
            if analysis:
                print("✅ [Risk Agent] Using local Ollama model")
                return {
                    "risk_analysis": analysis,
                    "model_used": "ollama",
                    "confidence": self._calculate_confidence(metrics)
                }

        except Exception as e:
            print(f"⚠️ [Risk Agent] Ollama failed: {e}")

        try:
            # Fallback to Google AI
            analysis = self._analyze_with_google_ai(metrics, health_score)
            if analysis:
                print("✅ [Risk Agent] Using Google AI")
                return {
                    "risk_analysis": analysis,
                    "model_used": "google_ai",
                    "confidence": self._calculate_confidence(metrics)
                }

        except Exception as e:
            print(f"⚠️ [Risk Agent] Google AI failed: {e}")

        # Final fallback
        return {
            "risk_analysis": self._generate_fallback_analysis(metrics, health_score),
            "model_used": "fallback",
            "confidence": 0.5
        }

    def _analyze_with_ollama(self, metrics: Dict[str, Any], health_score: int) -> Optional[str]:
        """Analyze using local Ollama models"""
        try:
            import ollama

            client = ollama.Client(host=self.ollama_host)

            prompt = self._build_risk_prompt(metrics, health_score)

            response = client.chat(
                model='mistral',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.3, 'top_p': 0.9}
            )

            return response['message']['content']

        except ImportError:
            raise Exception("Ollama not available")
        except Exception as e:
            raise Exception(f"Ollama analysis failed: {e}")

    def _analyze_with_google_ai(self, metrics: Dict[str, Any], health_score: int) -> Optional[str]:
        """Analyze using Google AI"""
        try:
            import google.genai as genai

            client = genai.Client(api_key=self.api_key)

            prompt = self._build_risk_prompt(metrics, health_score)

            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config={'temperature': 0.3, 'top_p': 0.9}
            )

            return response.text

        except ImportError:
            raise Exception("Google AI not available")
        except Exception as e:
            raise Exception(f"Google AI analysis failed: {e}")

    def _build_risk_prompt(self, metrics: Dict[str, Any], health_score: int) -> str:
        """Build the risk analysis prompt"""

        churn_hotspots = metrics.get('churn_metrics', {})
        complexity = metrics.get('overall_complexity', {})
        test_coverage = metrics.get('test_coverage_trends', {})
        bug_patterns = metrics.get('bug_patterns', {})
        deployments = metrics.get('deployment_frequency', {})

        return f"""
        TECHNICAL RISK ASSESSMENT - PREDICTIVE ANALYSIS

        CURRENT METRICS:
        - Health Score: {health_score}/100
        - Average Complexity: {complexity.get('avg_cc', 0):.1f}
        - Test Coverage Ratio: {test_coverage.get('coverage_ratio', 0):.2%}
        - Bug Fix Frequency: {bug_patterns.get('bug_fix_frequency', 0):.3f}
        - Deployment Frequency: {deployments.get('deployment_frequency_per_month', 0):.1f}/month

        TOP CODE HOTSPOTS (most frequently changed files):
        {self._format_hotspots(churn_hotspots)}

        BUG HOTSPOTS (files frequently involved in bug fixes):
        {self._format_hotspots(bug_patterns.get('bug_hotspots', {}))}

        TASK: As a Senior Software Architect, predict the most likely component failures in the next 90 days.

        Focus on:
        1. Code hotspots with high complexity
        2. Files with frequent bug fixes
        3. Low test coverage areas
        4. Deployment frequency issues

        Structure your response:
        - IDENTIFY top 3 risk components
        - EXPLAIN why each is at risk
        - ESTIMATE failure probability (High/Medium/Low)
        - SUGGEST preventive actions

        Be specific, technical, and actionable. Base predictions on the data provided.
        """

    def _format_hotspots(self, hotspots: Dict[str, int]) -> str:
        """Format hotspot data for the prompt"""
        if not hotspots:
            return "No significant hotspots identified"

        formatted = []
        for filename, count in list(hotspots.items())[:5]:
            formatted.append(f"- {filename}: {count} changes")

        return "\n".join(formatted)

    def _calculate_confidence(self, metrics: Dict[str, Any]) -> float:
        """Calculate confidence score based on data quality"""
        confidence = 0.5  # Base confidence

        # Higher confidence with more data points
        if metrics.get('overall_complexity', {}).get('file_count', 0) > 10:
            confidence += 0.2

        if len(metrics.get('churn_metrics', {})) > 5:
            confidence += 0.1

        if metrics.get('bug_patterns', {}).get('total_bug_fixes', 0) > 5:
            confidence += 0.1

        if metrics.get('test_coverage_trends', {}).get('test_files_count', 0) > 0:
            confidence += 0.1

        return min(1.0, confidence)

    def _generate_fallback_analysis(self, metrics: Dict[str, Any], health_score: int) -> str:
        """Generate basic risk analysis when AI models are unavailable"""

        complexity = metrics.get('overall_complexity', {}).get('avg_cc', 0)
        coverage = metrics.get('test_coverage_trends', {}).get('coverage_ratio', 0)
        bug_freq = metrics.get('bug_patterns', {}).get('bug_fix_frequency', 0)

        analysis = f"""
        RISK ANALYSIS (Fallback Mode)

        Based on automated metrics analysis:

        PRIMARY RISKS:
        """

        if complexity > 15:
            analysis += "\n1. HIGH COMPLEXITY - Average complexity score of {complexity:.1f} indicates maintainability issues"

        if coverage < 0.3:
            analysis += "\n2. LOW TEST COVERAGE - Only {coverage:.1%} test coverage increases regression risk"

        if bug_freq > 0.1:
            analysis += "\n3. FREQUENT BUG FIXES - {bug_freq:.1%} of commits are bug fixes"

        if health_score < 50:
            analysis += "\n4. OVERALL HEALTH - Critical health score requires immediate attention"

        analysis += f"""

        RECOMMENDATIONS:
        - Refactor high-complexity components
        - Increase test coverage to at least 70%
        - Implement code review processes
        - Schedule regular technical debt reduction

        Health Score: {health_score}/100
        """

        return analysis
