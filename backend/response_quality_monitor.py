"""
Response Quality Monitoring and Analytics
"""
import time
import json
import re
from typing import Dict, Any, List
from datetime import datetime
import asyncio

class ResponseQualityMonitor:
    def __init__(self):
        self.quality_metrics = []
        self.response_patterns = {
            "bill_references": re.compile(r'\b[HS][BJR]\s*\d+\b', re.IGNORECASE),
            "session_mentions": re.compile(r'session\s+\d+|legislative\s+session', re.IGNORECASE),
            "structured_formatting": re.compile(r'[•\-\*]|\*\*.*?\*\*|\d+\.'),
            "actionable_keywords": re.compile(r'\b(status|committee|vote|passed|failed|contact|deadline)\b', re.IGNORECASE)
        }
    
    def analyze_response_quality(self, query: str, response_dict: Dict[str, Any]) -> Dict[str, Any]:
        """Comprehensive response quality analysis"""
        response_text = response_dict.get("result", "")
        documents_found = response_dict.get("documents_found", 0)
        
        # Calculate quality metrics
        metrics = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "response_length": len(response_text),
            "documents_used": documents_found,
            "bill_specificity_score": self._calculate_bill_specificity(response_text),
            "structure_score": self._calculate_structure_score(response_text),
            "actionability_score": self._calculate_actionability_score(response_text),
            "completeness_score": self._calculate_completeness_score(response_dict),
            "user_satisfaction_predictors": self._predict_satisfaction_factors(response_dict)
        }
        
        # Overall quality score (weighted average)
        weights = {
            "bill_specificity_score": 0.25,
            "structure_score": 0.20,
            "actionability_score": 0.25,
            "completeness_score": 0.30
        }
        
        overall_score = sum(metrics[key] * weights[key] for key in weights)
        metrics["overall_quality_score"] = round(overall_score, 2)
        metrics["quality_grade"] = self._get_quality_grade(overall_score)
        
        # Store for analytics
        self.quality_metrics.append(metrics)
        
        return metrics
    
    def _calculate_bill_specificity(self, text: str) -> float:
        """Score based on specific bill references and legislative details"""
        bill_matches = len(self.response_patterns["bill_references"].findall(text))
        session_matches = len(self.response_patterns["session_mentions"].findall(text))
        
        # More points for bill references, some for session info
        score = min(1.0, (bill_matches * 0.3) + (session_matches * 0.2))
        return round(score, 2)
    
    def _calculate_structure_score(self, text: str) -> float:
        """Score response structure and readability"""
        structure_matches = len(self.response_patterns["structured_formatting"].findall(text))
        
        # Check for paragraph breaks and logical flow
        paragraph_breaks = len(text.split('\n\n'))
        
        # Points for formatting elements and good paragraph structure
        score = min(1.0, (structure_matches * 0.15) + (paragraph_breaks * 0.1))
        return round(score, 2)
    
    def _calculate_actionability_score(self, text: str) -> float:
        """Score based on actionable information provided"""
        actionable_matches = len(self.response_patterns["actionable_keywords"].findall(text))
        
        # Check for specific actionable elements
        actionable_indicators = [
            "contact", "next step", "deadline", "committee", 
            "status", "vote", "session", "website", "phone"
        ]
        
        indicator_count = sum(1 for indicator in actionable_indicators 
                            if indicator.lower() in text.lower())
        
        score = min(1.0, (actionable_matches * 0.1) + (indicator_count * 0.1))
        return round(score, 2)
    
    def _calculate_completeness_score(self, response_dict: Dict[str, Any]) -> float:
        """Score response completeness"""
        base_score = 0.3  # Base for having a response
        
        # Points for finding documents
        if response_dict.get("documents_found", 0) > 0:
            base_score += 0.4
        
        # Points for additional context
        if response_dict.get("sessions_referenced"):
            base_score += 0.1
            
        if response_dict.get("bill_numbers_found"):
            base_score += 0.1
            
        # Points for enhancement features
        if response_dict.get("enhancement_applied"):
            base_score += 0.1
            
        return round(min(1.0, base_score), 2)
    
    def _predict_satisfaction_factors(self, response_dict: Dict[str, Any]) -> Dict[str, bool]:
        """Predict factors that contribute to user satisfaction"""
        response_text = response_dict.get("result", "")
        
        return {
            "has_specific_bills": bool(self.response_patterns["bill_references"].search(response_text)),
            "well_structured": len(self.response_patterns["structured_formatting"].findall(response_text)) >= 2,
            "actionable_info": bool(self.response_patterns["actionable_keywords"].search(response_text)),
            "found_documents": response_dict.get("documents_found", 0) > 0,
            "provides_suggestions": "suggestion" in response_text.lower() or "try" in response_text.lower(),
            "appropriate_length": 100 <= len(response_text) <= 2000
        }
    
    def _get_quality_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 0.9:
            return "A"
        elif score >= 0.8:
            return "B" 
        elif score >= 0.7:
            return "C"
        elif score >= 0.6:
            return "D"
        else:
            return "F"
    
    def get_quality_analytics(self, time_window_hours: int = 24) -> Dict[str, Any]:
        """Get quality analytics for the specified time window"""
        cutoff_time = datetime.now().timestamp() - (time_window_hours * 3600)
        
        recent_metrics = [
            m for m in self.quality_metrics 
            if datetime.fromisoformat(m["timestamp"]).timestamp() > cutoff_time
        ]
        
        if not recent_metrics:
            return {"message": "No data available for the specified time window"}
        
        # Calculate averages
        avg_scores = {}
        score_keys = ["bill_specificity_score", "structure_score", "actionability_score", 
                     "completeness_score", "overall_quality_score"]
        
        for key in score_keys:
            avg_scores[f"avg_{key}"] = round(
                sum(m[key] for m in recent_metrics) / len(recent_metrics), 2
            )
        
        # Grade distribution
        grade_distribution = {}
        for metric in recent_metrics:
            grade = metric["quality_grade"]
            grade_distribution[grade] = grade_distribution.get(grade, 0) + 1
        
        # Satisfaction factor analysis
        satisfaction_factors = {
            "has_specific_bills": 0,
            "well_structured": 0,
            "actionable_info": 0,
            "found_documents": 0,
            "provides_suggestions": 0,
            "appropriate_length": 0
        }
        
        for metric in recent_metrics:
            factors = metric["user_satisfaction_predictors"]
            for factor, value in factors.items():
                if value:
                    satisfaction_factors[factor] += 1
        
        # Convert to percentages
        total_responses = len(recent_metrics)
        satisfaction_percentages = {
            factor: round((count / total_responses) * 100, 1)
            for factor, count in satisfaction_factors.items()
        }
        
        return {
            "time_window_hours": time_window_hours,
            "total_responses_analyzed": total_responses,
            "average_scores": avg_scores,
            "grade_distribution": grade_distribution,
            "satisfaction_factors_percentage": satisfaction_percentages,
            "top_improvement_areas": self._identify_improvement_areas(recent_metrics)
        }
    
    def _identify_improvement_areas(self, metrics: List[Dict]) -> List[str]:
        """Identify areas where response quality could be improved"""
        improvement_areas = []
        
        # Calculate average scores
        avg_bill_specificity = sum(m["bill_specificity_score"] for m in metrics) / len(metrics)
        avg_structure = sum(m["structure_score"] for m in metrics) / len(metrics)
        avg_actionability = sum(m["actionability_score"] for m in metrics) / len(metrics)
        avg_completeness = sum(m["completeness_score"] for m in metrics) / len(metrics)
        
        # Identify lowest scoring areas
        scores = {
            "Bill Specificity (add more specific bill references)": avg_bill_specificity,
            "Response Structure (improve formatting and organization)": avg_structure,
            "Actionability (include more actionable information)": avg_actionability,
            "Completeness (enhance response depth and context)": avg_completeness
        }
        
        # Sort by score and identify bottom areas
        sorted_areas = sorted(scores.items(), key=lambda x: x[1])
        
        for area, score in sorted_areas:
            if score < 0.7:  # Below "C" grade threshold
                improvement_areas.append(area)
        
        return improvement_areas[:3]  # Top 3 improvement areas

# Global instance for monitoring
response_quality_monitor = ResponseQualityMonitor()
