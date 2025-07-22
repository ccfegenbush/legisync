"""
Enhanced Prompt Templates for Better RAG Responses
"""

# Current simple chain_type="stuff" can be improved with custom prompts
LEGISLATIVE_RAG_PROMPT_TEMPLATE = """You are a helpful legislative research assistant for Texas bills and legislation. 
Based on the following legislative documents, provide a comprehensive and accurate response.

CONTEXT DOCUMENTS:
{context}

USER QUERY: {question}

INSTRUCTIONS:
1. **Direct Answer**: Start with a direct, concise answer to the user's question
2. **Specific Bills**: Always mention specific bill numbers (e.g., HB 55, SB 31) when available
3. **Key Details**: Include relevant details like session numbers, committees, and status
4. **Structure**: Use clear formatting with bullet points or numbered lists when appropriate
5. **Accuracy**: Only use information directly from the provided documents
6. **Helpful Context**: Explain legislative terminology when needed

If no relevant information is found, suggest alternative search terms or related topics.

RESPONSE:"""

RESPONSE_IMPROVEMENT_STRATEGIES = {
    "bill_summary": {
        "template": "**{bill_id}: {title}**\n• Session: {session}\n• Status: {status}\n• Summary: {summary}",
        "example": "**HB 55: Education Funding Reform**\n• Session: 891\n• Status: Passed Committee\n• Summary: Reforms property tax-based education funding formula"
    },
    
    "multiple_bills": {
        "template": "Found {count} relevant bills:\n\n{bill_summaries}\n\n**Key Themes:** {themes}",
        "example": "Found 3 relevant bills:\n\n• HB 55: Education funding\n• SB 31: Property tax relief\n• HB 82: School enrollment\n\n**Key Themes:** Education finance reform, property tax impacts"
    },
    
    "no_results": {
        "suggestions": [
            "Try broader search terms (e.g., 'education' instead of 'specific program name')",
            "Check spelling of bill numbers or legislative terms",
            "Search for related topics like 'budget', 'appropriations', or 'reform'",
            "Consider different time periods or legislative sessions"
        ]
    }
}

# Response quality metrics to track
RESPONSE_QUALITY_METRICS = {
    "bill_references": "Count of specific bill numbers mentioned",
    "session_info": "Inclusion of legislative session details", 
    "status_updates": "Current status of mentioned legislation",
    "actionable_info": "Concrete next steps or contact information",
    "source_attribution": "Clear linking back to source documents"
}
