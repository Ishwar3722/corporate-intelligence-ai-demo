from typing import List, Dict, Any

def build_context(retrieved_evidence: List[Dict[str, Any]], max_chars: int = 4000) -> str:
    """
    Builds a structured, bounded context string from retrieved evidence.
    """
    if not retrieved_evidence:
        return ""

    context_parts = []
    current_length = 0

    for item in retrieved_evidence:
        # Construct the block for a single evidence item
        lines = [
            "[EVIDENCE ITEM]",
            f"Evidence ID: {item.get('evidence_id', 'UNKNOWN')}",
            f"Source: {item.get('source_name', 'UNKNOWN')}",
            f"Source Tier: {item.get('source_tier', 'UNKNOWN')}",
            f"URL: {item.get('source_url', 'UNKNOWN')}",
            f"Headline: {item.get('headline', 'UNKNOWN')}",
            "Evidence:"
        ]
        
        snippet = item.get('raw_snippet', '')
        if snippet:
            lines.append(snippet)
            
        facts = item.get('extracted_facts', [])
        if facts:
            lines.append("Facts:")
            for fact in facts:
                lines.append(f"- {fact}")
                
        block = "\n".join(lines) + "\n\n"
        
        # Check if adding this block exceeds the max_chars
        # If it does, we stop adding evidence entirely to avoid truncation 
        # that could corrupt provenance.
        if current_length + len(block) > max_chars:
            break
            
        context_parts.append(block)
        current_length += len(block)

    return "".join(context_parts).strip()
