import json
import re
from typing import List, Dict, Any

STOP_WORDS = {"the", "is", "at", "which", "on", "in", "a", "an", "and", "or", "for", "of", "to", "what", "how", "much", "did", "were"}

def tokenize(text: str) -> set[str]:
    words = re.findall(r'\b\w+\b', text.lower())
    return set(w for w in words if w not in STOP_WORDS)

def retrieve(question: str, evidence_store: Dict[str, Any], top_k: int = 5, threshold: float = 1.0) -> List[Dict[str, Any]]:
    """
    Deterministic retrieval based on lexical overlap.
    """
    question_tokens = tokenize(question)
    if not question_tokens:
        return []

    scored_evidence = []
    
    for item in evidence_store.get("evidence", []):
        # Combine relevant text fields for matching
        text_to_search = item.get("headline", "") + " " + item.get("raw_snippet", "")
        facts = " ".join(item.get("extracted_facts", []))
        text_to_search += " " + facts
        
        item_tokens = tokenize(text_to_search)
        
        # Calculate score: number of overlapping tokens
        overlap = question_tokens.intersection(item_tokens)
        score = len(overlap)
        
        if score >= threshold:
            scored_item = dict(item)
            scored_item["score"] = score
            scored_evidence.append(scored_item)
            
    # Sort descending by score, then ascending by evidence_id for determinism
    scored_evidence.sort(key=lambda x: (-x["score"], x["evidence_id"]))
    
    return scored_evidence[:top_k]
