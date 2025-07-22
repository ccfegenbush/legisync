"""
Query Enhancement and Intent Recognition for Better RAG Results
"""
import re
from typing import List, Dict, Tuple, Optional
from enum import Enum

class QueryIntent(Enum):
    BILL_LOOKUP = "bill_lookup"          # "What is HB 55?"
    TOPIC_SEARCH = "topic_search"        # "education funding bills"
    STATUS_CHECK = "status_check"        # "status of healthcare legislation"
    COMPARISON = "comparison"            # "compare education bills"
    TIMELINE = "timeline"               # "recent environmental legislation"
    IMPACT_ANALYSIS = "impact_analysis"  # "how does this affect property taxes?"
    GENERAL_INFO = "general_info"       # "what is the legislative process?"

class QueryEnhancer:
    def __init__(self):
        self.bill_patterns = [
            r'\b[HS][BJR]\s*\d+\b',          # HB 55, SB 123, etc.
            r'\b(?:house|senate)\s*bill\s*\d+\b',  # House Bill 55
        ]
        
        self.topic_keywords = {
            "education": ["school", "teacher", "student", "education", "curriculum", "funding"],
            "healthcare": ["health", "medicaid", "medicare", "hospital", "medical", "insurance"],
            "transportation": ["highway", "road", "transit", "transportation", "infrastructure"],
            "environment": ["environment", "pollution", "climate", "water", "air", "conservation"],
            "budget": ["budget", "appropriation", "funding", "tax", "revenue", "spending"],
            "criminal_justice": ["crime", "prison", "police", "justice", "court", "sentence"]
        }
        
        self.status_keywords = ["status", "passed", "failed", "pending", "committee", "vote"]
        self.comparison_keywords = ["compare", "versus", "vs", "difference", "similar"]
        self.timeline_keywords = ["recent", "new", "latest", "upcoming", "current", "session"]
        
    def analyze_query(self, query: str) -> Dict[str, any]:
        """Analyze query to determine intent and extract key information"""
        query_lower = query.lower()
        
        # Determine intent
        intent = self._classify_intent(query_lower)
        
        # Extract entities
        entities = self._extract_entities(query)
        
        # Generate enhanced query variants
        enhanced_queries = self._generate_query_variants(query, intent, entities)
        
        # Suggest search parameters
        search_params = self._suggest_search_params(intent, entities)
        
        return {
            "original_query": query,
            "intent": intent,
            "entities": entities,
            "enhanced_queries": enhanced_queries,
            "search_params": search_params,
            "confidence": self._calculate_confidence(query_lower, intent, entities)
        }
    
    def _classify_intent(self, query_lower: str) -> QueryIntent:
        """Classify the user's intent based on query patterns"""
        # Check for specific bill references
        if any(re.search(pattern, query_lower, re.IGNORECASE) for pattern in self.bill_patterns):
            return QueryIntent.BILL_LOOKUP
        
        # Check for status inquiries
        if any(keyword in query_lower for keyword in self.status_keywords):
            return QueryIntent.STATUS_CHECK
        
        # Check for comparisons
        if any(keyword in query_lower for keyword in self.comparison_keywords):
            return QueryIntent.COMPARISON
        
        # Check for timeline queries
        if any(keyword in query_lower for keyword in self.timeline_keywords):
            return QueryIntent.TIMELINE
        
        # Check for impact analysis
        if any(word in query_lower for word in ["affect", "impact", "result", "consequence"]):
            return QueryIntent.IMPACT_ANALYSIS
        
        # Check for topic searches
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                return QueryIntent.TOPIC_SEARCH
        
        # Default to general info
        return QueryIntent.GENERAL_INFO
    
    def _extract_entities(self, query: str) -> Dict[str, List[str]]:
        """Extract key entities from the query"""
        entities = {
            "bills": [],
            "topics": [],
            "sessions": [],
            "committees": [],
            "timeframes": []
        }
        
        # Extract bill numbers
        for pattern in self.bill_patterns:
            bills = re.findall(pattern, query, re.IGNORECASE)
            entities["bills"].extend([bill.upper().replace(" ", " ") for bill in bills])
        
        # Extract topics
        query_lower = query.lower()
        for topic, keywords in self.topic_keywords.items():
            if any(keyword in query_lower for keyword in keywords):
                entities["topics"].append(topic)
        
        # Extract session numbers (e.g., "session 891", "87th session")
        session_patterns = [r'session\s+(\d+)', r'(\d+)(?:st|nd|rd|th)\s+session']
        for pattern in session_patterns:
            sessions = re.findall(pattern, query_lower)
            entities["sessions"].extend(sessions)
        
        # Extract timeframes
        timeframe_patterns = [r'\b(\d{4})\b', r'(recent|current|latest|upcoming|new)']
        for pattern in timeframe_patterns:
            timeframes = re.findall(pattern, query_lower)
            entities["timeframes"].extend(timeframes)
        
        return entities
    
    def _generate_query_variants(self, query: str, intent: QueryIntent, entities: Dict) -> List[str]:
        """Generate enhanced query variants for better search results"""
        variants = [query]  # Always include original
        
        # Add topic-specific variants
        if entities["topics"]:
            for topic in entities["topics"]:
                topic_keywords = self.topic_keywords.get(topic, [])
                for keyword in topic_keywords[:3]:  # Top 3 keywords
                    variants.append(f"{keyword} legislation")
                    variants.append(f"{keyword} bills")
        
        # Add bill-specific variants
        if entities["bills"]:
            for bill in entities["bills"]:
                variants.append(f"{bill} summary")
                variants.append(f"{bill} status")
        
        # Intent-specific enhancements
        if intent == QueryIntent.STATUS_CHECK:
            variants.extend([
                f"{query} committee",
                f"{query} vote",
                f"{query} passed"
            ])
        elif intent == QueryIntent.TIMELINE:
            variants.extend([
                f"current session {' '.join(entities['topics'])}",
                f"recent {' '.join(entities['topics'])} legislation"
            ])
        
        # Remove duplicates and empty strings
        return list(filter(None, list(set(variants))))
    
    def _suggest_search_params(self, intent: QueryIntent, entities: Dict) -> Dict[str, any]:
        """Suggest search parameters based on intent and entities"""
        params = {
            "similarity_threshold": 0.7,
            "max_documents": 5,
            "search_type": "similarity"
        }
        
        # Adjust based on intent
        if intent == QueryIntent.BILL_LOOKUP:
            params.update({
                "similarity_threshold": 0.8,  # Higher threshold for specific bills
                "max_documents": 3,
                "search_type": "exact_match_preferred"
            })
        elif intent == QueryIntent.TOPIC_SEARCH:
            params.update({
                "similarity_threshold": 0.6,  # Lower threshold for broader search
                "max_documents": 8,
                "search_type": "similarity"
            })
        elif intent == QueryIntent.COMPARISON:
            params.update({
                "max_documents": 10,  # More documents for comparison
                "search_type": "similarity"
            })
        
        # Add filters based on entities
        filters = {}
        if entities["sessions"]:
            filters["session"] = entities["sessions"]
        if entities["bills"]:
            filters["bill_ids"] = entities["bills"]
            
        if filters:
            params["filters"] = filters
        
        return params
    
    def _calculate_confidence(self, query_lower: str, intent: QueryIntent, entities: Dict) -> float:
        """Calculate confidence in the intent classification"""
        confidence = 0.5  # Base confidence
        
        # Increase confidence based on specific indicators
        if entities["bills"]:
            confidence += 0.3
        if entities["topics"]:
            confidence += 0.2
        if entities["sessions"]:
            confidence += 0.1
        
        # Intent-specific confidence adjustments
        intent_indicators = {
            QueryIntent.BILL_LOOKUP: any(re.search(pattern, query_lower) for pattern in self.bill_patterns),
            QueryIntent.STATUS_CHECK: any(word in query_lower for word in self.status_keywords),
            QueryIntent.COMPARISON: any(word in query_lower for word in self.comparison_keywords)
        }
        
        if intent_indicators.get(intent, False):
            confidence += 0.2
        
        return min(1.0, confidence)

class ResponsePersonalizer:
    """Personalize responses based on user preferences and query history"""
    
    @staticmethod
    def personalize_response(response: str, user_context: Optional[Dict] = None) -> str:
        """Personalize response based on user context"""
        if not user_context:
            return response
        
        # Add user-specific context
        if user_context.get("expertise_level") == "beginner":
            # Add more explanatory text for beginners
            if "HB" in response or "SB" in response:
                explanation = "\n\n*Note: HB = House Bill, SB = Senate Bill*"
                response += explanation
        
        if user_context.get("interests"):
            # Highlight topics of interest
            for interest in user_context["interests"]:
                if interest.lower() in response.lower():
                    response = f"🔍 *Relevant to your interest in {interest}:*\n\n{response}"
                    break
        
        return response

# Usage example function
def enhance_query_processing(original_query: str) -> Dict[str, any]:
    """Complete query enhancement workflow"""
    enhancer = QueryEnhancer()
    analysis = enhancer.analyze_query(original_query)
    
    return {
        "enhanced_search": analysis,
        "recommended_approach": _get_search_strategy(analysis),
        "expected_result_type": _predict_result_type(analysis)
    }

def _get_search_strategy(analysis: Dict) -> str:
    """Recommend search strategy based on analysis"""
    intent = analysis["intent"]
    
    strategies = {
        QueryIntent.BILL_LOOKUP: "Exact bill match with metadata lookup",
        QueryIntent.TOPIC_SEARCH: "Semantic similarity with topic expansion", 
        QueryIntent.STATUS_CHECK: "Recent documents with status keywords",
        QueryIntent.COMPARISON: "Multi-document retrieval with side-by-side analysis",
        QueryIntent.TIMELINE: "Time-filtered search with chronological ordering"
    }
    
    return strategies.get(intent, "General semantic search")

def _predict_result_type(analysis: Dict) -> str:
    """Predict what type of result the user is expecting"""
    if analysis["entities"]["bills"]:
        return "Specific bill information with current status"
    elif analysis["entities"]["topics"]:
        return "Topic overview with related bills list"
    else:
        return "General information with actionable next steps"
