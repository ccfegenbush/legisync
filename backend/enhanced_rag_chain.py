"""
Enhanced RAG Chain with Custom Prompts and Response Processing
"""
from langchain.chains.question_answering import load_qa_chain
from langchain.prompts import PromptTemplate
from langchain_core.output_parsers import StrOutputParser
from typing import List, Dict, Any
import re

class EnhancedRAGChain:
    def __init__(self, llm, vectorstore):
        self.llm = llm
        self.vectorstore = vectorstore
        self.setup_custom_chain()
    
    def setup_custom_chain(self):
        """Setup custom prompt template for better responses"""
        self.prompt_template = PromptTemplate(
            input_variables=["context", "question"],
            template="""You are a helpful legislative research assistant for Texas bills and legislation. 
Based on the following legislative documents, provide a comprehensive and accurate response.

CONTEXT DOCUMENTS:
{context}

USER QUERY: {question}

RESPONSE GUIDELINES:
1. **Direct Answer**: Start with a clear, direct answer
2. **Specific References**: Always cite specific bill numbers (HB, SB) when available
3. **Session & Status**: Include legislative session and current status when known
4. **Structure**: Use bullet points or numbered lists for multiple items
5. **Accuracy**: Only use information from the provided documents
6. **Helpful Format**: Make the response scannable and actionable

If no relevant bills are found, suggest alternative search terms or related legislative topics.

RESPONSE:"""
        )
        
        self.chain = load_qa_chain(
            llm=self.llm, 
            chain_type="stuff", 
            prompt=self.prompt_template
        )
    
    async def run_enhanced_query(self, query: str, documents: List[Any]) -> Dict[str, Any]:
        """Enhanced query processing with response improvement"""
        if not documents:
            return self._generate_no_results_response(query)
        
        # Run the chain with custom prompt
        result = await self.chain.arun(input_documents=documents, question=query)
        
        # Post-process the response for better formatting
        enhanced_result = self._enhance_response(result, documents)
        
        return {
            "query": query,
            "result": enhanced_result,
            "documents_found": len(documents),
            "source_documents": len(documents),
            "enhancement_applied": True
        }
    
    def _enhance_response(self, response: str, documents: List[Any]) -> str:
        """Post-process response for better formatting and completeness"""
        enhanced = response
        
        # Extract bill numbers and format them consistently
        bill_numbers = re.findall(r'\b[HS][BJR]\s*\d+\b', response.upper())
        for bill in bill_numbers:
            formatted_bill = f"**{bill.replace(' ', ' ')}**"
            enhanced = enhanced.replace(bill, formatted_bill)
        
        # Add document count if multiple sources
        doc_count = len(documents)
        if doc_count > 1:
            enhanced = f"*Based on {doc_count} legislative documents:*\n\n{enhanced}"
        
        # Add session information if available from metadata
        sessions = set()
        for doc in documents:
            if hasattr(doc, 'metadata') and 'session' in doc.metadata:
                sessions.add(doc.metadata['session'])
        
        if sessions:
            session_text = f"**Legislative Session(s):** {', '.join(sorted(sessions))}\n\n"
            enhanced = session_text + enhanced
        
        return enhanced
    
    def _generate_no_results_response(self, query: str) -> Dict[str, Any]:
        """Generate helpful response when no documents are found"""
        suggestions = [
            "Try broader search terms (e.g., 'education' instead of specific program names)",
            "Check spelling of bill numbers or legislative terms", 
            "Search for related topics like 'budget', 'appropriations', or 'reform'",
            "Consider different legislative sessions or time periods"
        ]
        
        response = f"""No specific bills found for your query: "{query}"

**Search Suggestions:**
• {chr(10).join(f"• {suggestion}" for suggestion in suggestions)}

**Popular Topics to Explore:**
• Education funding and school finance
• Healthcare and Medicaid policy  
• Transportation and infrastructure
• Criminal justice reform
• Environmental protection
• Tax policy and property taxes

Try rephrasing your question or using one of these broader topics."""

        return {
            "query": query,
            "result": response,
            "documents_found": 0,
            "suggestions_provided": True
        }

# Response quality scoring
class ResponseQualityScorer:
    @staticmethod
    def score_response(response_dict: Dict[str, Any]) -> Dict[str, float]:
        """Score response quality on multiple dimensions"""
        response_text = response_dict.get("result", "")
        
        scores = {
            "bill_specificity": ResponseQualityScorer._score_bill_references(response_text),
            "structure_clarity": ResponseQualityScorer._score_structure(response_text), 
            "actionability": ResponseQualityScorer._score_actionability(response_text),
            "completeness": ResponseQualityScorer._score_completeness(response_dict),
        }
        
        # Overall quality score (weighted average)
        weights = {"bill_specificity": 0.3, "structure_clarity": 0.2, "actionability": 0.2, "completeness": 0.3}
        overall_score = sum(scores[key] * weights[key] for key in scores)
        scores["overall"] = overall_score
        
        return scores
    
    @staticmethod
    def _score_bill_references(text: str) -> float:
        """Score based on specific bill references"""
        bill_pattern = r'\b[HS][BJR]\s*\d+\b'
        bill_count = len(re.findall(bill_pattern, text, re.IGNORECASE))
        return min(1.0, bill_count * 0.3)  # Max 1.0, 0.3 per bill reference
    
    @staticmethod
    def _score_structure(text: str) -> float:
        """Score based on response structure and formatting"""
        structure_indicators = [
            r'\*\*.*?\*\*',  # Bold formatting
            r'^\s*[•\-\*]',   # Bullet points
            r'^\s*\d+\.',    # Numbered lists
        ]
        
        score = 0.0
        for pattern in structure_indicators:
            if re.search(pattern, text, re.MULTILINE):
                score += 0.33
        
        return min(1.0, score)
    
    @staticmethod
    def _score_actionability(text: str) -> float:
        """Score based on actionable information provided"""
        actionable_keywords = [
            "session", "status", "committee", "vote", "passed", "failed",
            "contact", "next step", "deadline", "effective date"
        ]
        
        found_keywords = sum(1 for keyword in actionable_keywords if keyword.lower() in text.lower())
        return min(1.0, found_keywords * 0.15)
    
    @staticmethod
    def _score_completeness(response_dict: Dict[str, Any]) -> float:
        """Score based on response completeness"""
        base_score = 0.5  # Base for having a response
        
        if response_dict.get("documents_found", 0) > 0:
            base_score += 0.3
        
        if "source_documents" in response_dict:
            base_score += 0.1
            
        if response_dict.get("suggestions_provided"):
            base_score += 0.1
            
        return min(1.0, base_score)
