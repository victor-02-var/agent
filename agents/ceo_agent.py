# -*- coding: utf-8 -*-
"""
CEO Agent - Specialized in Business Impact Analysis
Converts technical analysis into executive-level business reports
"""

import os
from typing import Dict, Any, Optional
from dotenv import load_dotenv

load_dotenv()

class CEOAgent:
    def __init__(self):
        self.api_key = os.getenv("GOOGLE_API_KEY")
        self.ollama_host = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

    def generate_business_report(self, technical_analysis: str, health_score: int, metrics: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert technical analysis into a business-impact report for CEOs
        """
        print("📊 [CEO Agent] Generating executive business impact report...")

        try:
            # Try Ollama first (local models)
            report = self._generate_with_ollama(technical_analysis, health_score, metrics)
            if report:
                print("✅ [CEO Agent] Using local Ollama model")
                return {
                    "business_report": report,
                    "model_used": "ollama",
                    "executive_summary": self._extract_executive_summary(report)
                }

        except Exception as e:
            print(f"⚠️ [CEO Agent] Ollama failed: {e}")

        try:
            # Fallback to Google AI
            report = self._generate_with_google_ai(technical_analysis, health_score, metrics)
            if report:
                print("✅ [CEO Agent] Using Google AI")
                return {
                    "business_report": report,
                    "model_used": "google_ai",
                    "executive_summary": self._extract_executive_summary(report)
                }

        except Exception as e:
            print(f"⚠️ [CEO Agent] Google AI failed: {e}")

        # Final fallback
        return {
            "business_report": self._generate_fallback_report(technical_analysis, health_score, metrics),
            "model_used": "fallback",
            "executive_summary": f"Health Score: {health_score}/100 - Requires executive attention"
        }

    def _generate_with_ollama(self, technical_analysis: str, health_score: int, metrics: Dict[str, Any]) -> Optional[str]:
        """Generate report using local Ollama models"""
        try:
            import ollama

            client = ollama.Client(host=self.ollama_host)

            prompt = self._build_business_prompt(technical_analysis, health_score, metrics)

            response = client.chat(
                model='llama3',
                messages=[{'role': 'user', 'content': prompt}],
                options={'temperature': 0.2, 'top_p': 0.8}  # Lower temperature for business reports
            )

            return response['message']['content']

        except ImportError:
            raise Exception("Ollama not available")
        except Exception as e:
            raise Exception(f"Ollama report generation failed: {e}")

    def _generate_with_google_ai(self, technical_analysis: str, health_score: int, metrics: Dict[str, Any]) -> Optional[str]:
        """Generate report using Google AI"""
        try:
            import google.genai as genai

            client = genai.Client(api_key=self.api_key)

            prompt = self._build_business_prompt(technical_analysis, health_score, metrics)

            response = client.models.generate_content(
                model='gemini-2.0-flash-exp',
                contents=prompt,
                config={'temperature': 0.2, 'top_p': 0.8}
            )

            return response.text

        except ImportError:
            raise Exception("Google AI not available")
        except Exception as e:
            raise Exception(f"Google AI report generation failed: {e}")

    def _build_business_prompt(self, technical_analysis: str, health_score: int, metrics: Dict[str, Any]) -> str:
        """Build the business report prompt"""

        # Extract key business-relevant metrics
        complexity = metrics.get('overall_complexity', {})
        test_coverage = metrics.get('test_coverage_trends', {})
        deployments = metrics.get('deployment_frequency', {})
        bugs = metrics.get('bug_patterns', {})

        # Calculate potential business impact
        avg_complexity = complexity.get('avg_cc', 0)
        coverage_ratio = test_coverage.get('coverage_ratio', 0)
        deploy_freq = deployments.get('deployment_frequency_per_month', 0)
        bug_freq = bugs.get('bug_fix_frequency', 0)

        return f"""
        EXECUTIVE BUSINESS IMPACT REPORT GENERATOR

        ROLE: You are a Strategic Business Consultant reporting to the CEO.
        AUDIENCE: Non-technical CEO who cares about revenue, costs, and competitive advantage.

        TECHNICAL INPUT:
        Health Score: {health_score}/100
        Technical Analysis: {technical_analysis}

        KEY METRICS:
        - Code Complexity: {avg_complexity:.1f} (lower is better)
        - Test Coverage: {coverage_ratio:.1%}
        - Deployment Frequency: {deploy_freq:.1f}/month
        - Bug Fix Rate: {bug_freq:.1%}

        REQUIRED REPORT STRUCTURE:

        1. EXECUTIVE SUMMARY (Financial Health)
           - One paragraph overview of current technical health
           - Financial impact statement

        2. PROJECTED REVENUE AT RISK (Next 90 Days)
           - Quantify potential revenue loss from downtime/failures
           - Estimate customer impact and churn risk
           - Include cost of emergency fixes

        3. MARKET VELOCITY IMPACT (Technical debt vs Feature speed)
           - How technical debt slows feature delivery
           - Competitive disadvantage analysis
           - Time-to-market delays quantified

        4. STRATEGIC RECOMMENDATION (Actionable next steps)
           - Prioritized action items with timeframes
           - Resource requirements (people, budget)
           - Expected ROI of investments

        WRITING GUIDELINES:
        - Use simple business language (NO technical jargon)
        - Include specific dollar amounts and timeframes
        - Be direct and actionable
        - Focus on business outcomes, not technical details
        - Use "we" and "our" perspective
        - Keep total report under 800 words

        FORMAT: Clean, professional business report style.
        """

    def _extract_executive_summary(self, full_report: str) -> str:
        """Extract the executive summary section"""
        try:
            # Find the executive summary section
            lines = full_report.split('\n')
            in_summary = False
            summary_lines = []

            for line in lines:
                if 'EXECUTIVE SUMMARY' in line.upper():
                    in_summary = True
                    continue
                elif in_summary and line.strip() and any(section in line.upper() for section in
                        ['PROJECTED REVENUE', 'MARKET VELOCITY', 'STRATEGIC RECOMMENDATION']):
                    break
                elif in_summary:
                    summary_lines.append(line)

            summary = '\n'.join(summary_lines).strip()
            return summary if summary else "Executive summary not available"

        except:
            return "Executive summary extraction failed"

    def _generate_fallback_report(self, technical_analysis: str, health_score: int, metrics: Dict[str, Any]) -> str:
        """Generate basic business report when AI models are unavailable"""

        # Calculate estimated business impact
        if health_score >= 80:
            revenue_risk = "$10K-$25K"
            velocity_impact = "5-10% slower feature delivery"
            recommendations = "Maintain current practices"
        elif health_score >= 60:
            revenue_risk = "$25K-$75K"
            velocity_impact = "15-25% slower feature delivery"
            recommendations = "2-week refactoring sprint"
        elif health_score >= 40:
            revenue_risk = "$75K-$150K"
            velocity_impact = "30-40% slower feature delivery"
            recommendations = "1-month technical debt reduction"
        else:
            revenue_risk = "$150K-$500K+"
            velocity_impact = "50%+ slower feature delivery"
            recommendations = "Immediate 2-month intervention required"

        return f"""
EXECUTIVE SUMMARY
Our codebase health score of {health_score}/100 indicates significant technical challenges that require executive attention. Current technical debt is impacting our ability to deliver features quickly and reliably.

PROJECTED REVENUE AT RISK (Next 90 Days)
Based on current metrics, we face {revenue_risk} in potential revenue loss from system downtime, bug fixes, and delayed feature releases. Customer satisfaction may decline by 15-30% if critical issues emerge.

MARKET VELOCITY IMPACT
Technical debt is causing {velocity_impact}, putting us at a competitive disadvantage. Competitors with healthier codebases can release features 2-3x faster, potentially capturing market share.

STRATEGIC RECOMMENDATION
1. {recommendations} to address critical technical debt
2. Allocate budget for additional development resources
3. Implement automated testing and code review processes
4. Schedule quarterly technical health assessments

Expected ROI: 3-5x return on technical investments within 6 months through faster feature delivery and reduced downtime costs.
"""
