import os
import pytest
from unittest.mock import patch, MagicMock
import time

# Set up test environment
os.environ["TESTING"] = "true"
os.environ["LANGCHAIN_TRACING_V2"] = "false"

from response_quality_monitor import ResponseQualityMonitor

class TestResponseQualityMonitor:
    """Test cases for the response quality monitoring service"""
    
    def test_response_quality_monitor_initialization(self):
        """Test response quality monitor initialization"""
        monitor = ResponseQualityMonitor()
        assert monitor.quality_metrics == []
        assert hasattr(monitor, '_calculate_bill_specificity')
        assert hasattr(monitor, '_calculate_structure_score')
        assert hasattr(monitor, '_calculate_actionability_score')
        assert hasattr(monitor, '_calculate_completeness_score')
    
    def test_analyze_high_quality_response(self):
        """Test analysis of a high-quality response"""
        monitor = ResponseQualityMonitor()
        
        query = "education funding bills"
        result = {
            "result": """**Legislative Session: 891**

Based on 3 legislative documents:

**HB 55** - Education Funding Reform Act
This bill addresses public school funding formulas and property tax relief.

**SB 120** - School Finance Modernization
This bill updates the state's education funding mechanisms.

**Key Provisions:**
• Increased per-pupil funding by $500
• Property tax rate reductions
• New funding for special education programs
• Implementation timeline: September 2024

**Current Status:** Passed House, pending in Senate Education Committee

**Next Steps:** Contact your state senator to support SB 120""",
            "documents_found": 3,
            "source_documents": 3
        }
        
        quality_metrics = monitor.analyze_response_quality(query, result)
        
        # Check overall quality
        assert quality_metrics["overall_quality_score"] > 0.8
        assert quality_metrics["quality_grade"] in ["A", "B"]
        
        # Check individual scores
        assert quality_metrics["bill_specificity_score"] > 0.8  # Has specific bill numbers
        assert quality_metrics["structure_score"] > 0.8  # Well structured
        assert quality_metrics["actionability_score"] > 0.7  # Has next steps
        assert quality_metrics["completeness_score"] > 0.6  # Comprehensive
        
        # Check that metrics were stored
        assert len(monitor.quality_metrics) == 1
    
    def test_analyze_poor_quality_response(self):
        """Test analysis of a poor-quality response"""
        monitor = ResponseQualityMonitor()
        
        query = "healthcare legislation"
        result = {
            "result": "There are some bills about healthcare. They deal with various health issues.",
            "documents_found": 1,
            "source_documents": 1
        }
        
        quality_metrics = monitor.analyze_response_quality(query, result)
        
        # Check overall quality is low
        assert quality_metrics["overall_quality_score"] < 0.6
        assert quality_metrics["quality_grade"] in ["C", "D", "F"]
        
        # Check individual scores are low
        assert quality_metrics["bill_specificity_score"] < 0.5  # No specific bills
        assert quality_metrics["structure_score"] < 0.5  # Poor structure
        assert quality_metrics["actionability_score"] < 0.5  # No actionable info
        assert quality_metrics["completeness_score"] <= 0.7  # Very brief
    
    def test_analyze_no_documents_response(self):
        """Test analysis of no documents found response"""
        monitor = ResponseQualityMonitor()
        
        query = "non-existent topic"
        result = {
            "result": """No specific bills found for your query: "non-existent topic"

**Search Suggestions:**
• Try broader search terms (e.g., 'education' instead of specific program names)
• Check spelling of bill numbers or legislative terms

**Popular Topics to Explore:**
• Education funding and school finance
• Healthcare and Medicaid policy""",
            "documents_found": 0,
            "suggestions_provided": True
        }
        
        quality_metrics = monitor.analyze_response_quality(query, result)
        
        # Should still have decent quality for helpful no-results response
        assert quality_metrics["overall_quality_score"] > 0.25
        assert quality_metrics["structure_score"] > 0.7  # Well structured suggestions
        assert quality_metrics["actionability_score"] > 0.6  # Provides alternatives
    
    def test_bill_specificity_scoring(self):
        """Test bill specificity scoring logic"""
        monitor = ResponseQualityMonitor()
        
        # Test high specificity (multiple bills with details)
        high_specificity_response = """
        **HB 55** - Education Funding Bill addresses school finance.
        **SB 120** - Healthcare Reform modifies Medicaid policies.
        **HJR 25** - Constitutional Amendment for tax relief.
        """
        score = monitor._calculate_bill_specificity(high_specificity_response, 3)
        assert score > 0.8
        
        # Test medium specificity (some bills mentioned)
        medium_specificity_response = "HB 55 and another bill address education funding."
        score = monitor._calculate_bill_specificity(medium_specificity_response, 2)
        assert 0.4 < score < 0.8
        
        # Test low specificity (no specific bills)
        low_specificity_response = "Several bills address education issues."
        score = monitor._calculate_bill_specificity(low_specificity_response, 2)
        assert score < 0.4
    
    def test_structure_scoring(self):
        """Test response structure scoring"""
        monitor = ResponseQualityMonitor()
        
        # Test well-structured response
        well_structured = """
        **Education Funding Bills:**
        
        • HB 55 - Increases per-pupil funding
        • SB 120 - Property tax relief
        
        **Key Details:**
        1. Funding increase: $500 per student
        2. Implementation: Fall 2024
        
        **Next Steps:**
        Contact your representative
        """
        score = monitor._calculate_structure_score(well_structured)
        assert score > 0.8
        
        # Test poorly structured response
        poorly_structured = "There are bills about education funding they increase money for schools and reduce taxes implementation is fall 2024 contact representative"
        score = monitor._calculate_structure_score(poorly_structured)
        assert score < 0.5
    
    def test_actionability_scoring(self):
        """Test actionability scoring logic"""
        monitor = ResponseQualityMonitor()
        
        # Test highly actionable response
        actionable_response = """
        **Current Status:** HB 55 passed House, pending in Senate
        **Committee:** Senate Education Committee
        **Next Steps:** 
        • Contact Senator Smith at (512) 555-0100
        • Attend public hearing on March 15th
        • Submit written testimony by March 10th
        **Timeline:** Final vote expected April 1st
        """
        score = monitor._calculate_actionability_score(actionable_response)
        assert score > 0.8
        
        # Test less actionable response
        less_actionable = "HB 55 is about education funding and is currently being reviewed."
        score = monitor._calculate_actionability_score(less_actionable)
        assert score < 0.5
    
    def test_completeness_scoring(self):
        """Test completeness scoring logic"""
        monitor = ResponseQualityMonitor()
        
        # Test complete response
        complete_response = """
        Education funding in Texas is addressed by several bills in the current legislative session.
        
        HB 55 - Basic Education Funding Act increases per-pupil funding from $6,160 to $6,660, 
        representing a $500 increase per student. This bill passed the House on March 1st with 
        bipartisan support and is currently pending in the Senate Education Committee.
        
        The bill includes provisions for special education funding, rural school supplements, 
        and technology grants. Implementation is scheduled for the 2024-2025 school year.
        
        Related bills include SB 120 for property tax relief and HB 200 for teacher pay raises.
        """
        score = monitor._calculate_completeness_score(complete_response, 3)
        assert score > 0.8
        
        # Test incomplete response
        incomplete_response = "HB 55 is about education funding."
        score = monitor._calculate_completeness_score(incomplete_response, 3)
        assert score < 0.3
    
    def test_quality_analytics(self):
        """Test quality analytics generation"""
        monitor = ResponseQualityMonitor()
        
        # Add sample quality data
        sample_queries = [
            ("education funding", {"overall_quality_score": 0.85, "bill_specificity_score": 0.9}),
            ("healthcare bills", {"overall_quality_score": 0.75, "bill_specificity_score": 0.7}),
            ("tax reform", {"overall_quality_score": 0.65, "bill_specificity_score": 0.6}),
        ]
        
        for query, result in sample_queries:
            # Create mock result with quality metrics
            mock_result = {"result": "sample response", "documents_found": 2}
            with patch.object(monitor, '_calculate_bill_specificity', return_value=result["bill_specificity_score"]):
                with patch.object(monitor, '_calculate_structure_score', return_value=0.8):
                    with patch.object(monitor, '_calculate_actionability_score', return_value=0.7):
                        with patch.object(monitor, '_calculate_completeness_score', return_value=0.8):
                            monitor.analyze_response_quality(query, mock_result)
        
        # Get analytics
        analytics = monitor.get_quality_analytics(time_window_hours=24)
        
        assert "total_responses_analyzed" in analytics
        assert analytics["total_responses_analyzed"] == 3
        
        assert "average_scores" in analytics
        avg_scores = analytics["average_scores"]
        assert "avg_overall_quality_score" in avg_scores
        assert "avg_bill_specificity_score" in avg_scores
        
        assert "quality_distribution" in analytics
        distribution = analytics["quality_distribution"]
        assert sum(distribution.values()) == 3  # All responses accounted for
        
        assert "top_improvement_areas" in analytics
    
    def test_improvement_area_identification(self):
        """Test identification of improvement areas"""
        monitor = ResponseQualityMonitor()
        
        # Create responses with specific weaknesses
        weak_areas = {
            "bill_specificity_score": 0.3,  # Poor bill specificity
            "structure_score": 0.4,          # Poor structure  
            "actionability_score": 0.5,      # Poor actionability
            "completeness_score": 0.6        # Poor completeness
        }
        
        # Mock the scoring methods to return our test values
        for area, score in weak_areas.items():
            method_name = f"_calculate_{area}"
            with patch.object(monitor, method_name, return_value=score):
                pass
        
        # This would need to be run with all patches active
        # For now, test the improvement identification logic
        improvements = monitor._identify_improvement_areas({
            "bill_specificity_score": 0.3,
            "structure_score": 0.4, 
            "actionability_score": 0.5,
            "completeness_score": 0.6
        })
        
        # Should identify bill specificity as top improvement area
        assert "Bill Specificity" in improvements
        assert improvements["Bill Specificity"]["priority"] == "high"
        
    def test_quality_grade_assignment(self):
        """Test quality grade assignment logic"""
        monitor = ResponseQualityMonitor()
        
        # Test grade boundaries
        grade_tests = [
            (0.95, "A+"),
            (0.90, "A"),
            (0.85, "A-"),
            (0.80, "B+"),
            (0.75, "B"),
            (0.70, "B-"),
            (0.65, "C+"),
            (0.60, "C"),
            (0.55, "C-"),
            (0.50, "D"),
            (0.40, "F")
        ]
        
        for score, expected_grade in grade_tests:
            grade = monitor._get_quality_grade(score)
            assert grade == expected_grade, f"Score {score} should be grade {expected_grade}, got {grade}"
    
    def test_time_window_filtering(self):
        """Test filtering quality history by time window"""
        monitor = ResponseQualityMonitor()
        
        # Add old and recent entries
        current_time = time.time()
        
        # Add old entry (25 hours ago)
        old_entry = {
            "timestamp": current_time - (25 * 3600),
            "overall_quality_score": 0.8
        }
        monitor.quality_metrics.append(old_entry)
        
        # Add recent entry (1 hour ago)  
        recent_entry = {
            "timestamp": current_time - 3600,
            "overall_quality_score": 0.9
        }
        monitor.quality_metrics.append(recent_entry)
        
        # Get analytics for last 24 hours
        analytics = monitor.get_quality_analytics(time_window_hours=24)
        
        # Should only include recent entry
        assert analytics["total_responses_analyzed"] == 1
