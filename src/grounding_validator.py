import re
from dataclasses import dataclass, field
from typing import List, Dict, Any, Set

@dataclass
class Claim:
    text: str
    citations: List[str]
    is_inference: bool = False
    status: str = "UNKNOWN"

@dataclass
class ValidationResult:
    accepted: bool
    grounded: bool
    grounding_score: float
    claims: List[Claim]
    supported_claims: List[Claim]
    unsupported_claims: List[Claim]
    uncited_claims: List[Claim]
    invalid_citations: List[str]
    cited_evidence_ids: List[str]
    reason: str

STOP_WORDS = {"the", "is", "at", "which", "on", "in", "a", "an", "and", "or", "for", "of", "to", "what", "how", "much", "did", "were", "was", "has", "had", "been"}
INFERENCE_MARKERS = {"might", "may", "could", "possibly", "probably", "likely", "suggests", "inference", "uncertain", "insufficient evidence", "appears to"}

def _tokenize(text: str) -> Set[str]:
    words = re.findall(r'\b\w+\b', text.lower())
    return set(w for w in words if w not in STOP_WORDS)

def parse_citations(text: str) -> List[str]:
    """Finds all citations in the format [ev_XXX]"""
    return re.findall(r'\[(ev_[^\]]+)\]', text)

def extract_claims(answer: str) -> List[Claim]:
    """
    Lightweight deterministic MVP claim extraction.
    Splits by periods to get sentences, then splits into factual clauses.
    Associates citations in the sentence to its clauses.
    Detects explicit inference/uncertainty markers.
    """
    sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', answer) if s.strip()]
    claims = []
    
    for sentence in sentences:
        citations = parse_citations(sentence)
        lower_sentence = sentence.lower()
        
        is_inference = any(marker in lower_sentence for marker in INFERENCE_MARKERS)
        
        # Split into clauses by common conjunctions or semicolon
        # Using a regex that splits by ' and ', ' but ', ' while ', or ';'
        clauses = [c.strip() for c in re.split(r'\s+(?:and|but|while)\s+|;', sentence) if c.strip()]
        
        for clause in clauses:
            # Only consider it a factual claim if it has substantial words and is not just a citation
            clean_text = re.sub(r'\[ev_[^\]]+\]', '', clause).strip()
            if len(clean_text) > 3:
                claims.append(Claim(text=clause, citations=citations, is_inference=is_inference))
            
    return claims

def check_lexical_support(claim_text: str, evidence_text: str, threshold: float = 0.3) -> bool:
    """
    Lexical evidence-support heuristic.
    Checks if a sufficient ratio of the claim's tokens are present in the evidence.
    """
    clean_claim = re.sub(r'\[ev_[^\]]+\]', '', claim_text).strip()
    claim_tokens = _tokenize(clean_claim)
    if not claim_tokens:
        return True # Trivial claim with no significant tokens
        
    evidence_tokens = _tokenize(evidence_text)
    
    overlap = claim_tokens.intersection(evidence_tokens)
    ratio = len(overlap) / len(claim_tokens)
    
    return ratio >= threshold

def validate_answer(answer: str, evidence: List[Dict[str, Any]], support_threshold: float = 0.3) -> ValidationResult:
    """
    Rule-based post-generation grounding and citation validator.
    """
    evidence_map = {item.get("evidence_id"): item for item in evidence if item.get("evidence_id")}
    
    claims = extract_claims(answer)
    
    supported_claims = []
    unsupported_claims = []
    uncited_claims = []
    invalid_citations = set()
    cited_evidence_ids = set()
    
    # Process all citations to find invalid ones
    all_citations = parse_citations(answer)
    for cit in all_citations:
        if cit not in evidence_map:
            invalid_citations.add(cit)
        else:
            cited_evidence_ids.add(cit)
            
    # Process claims
    total_factual_claims = 0
    
    for claim in claims:
        if claim.is_inference:
            claim.status = "INFERENCE"
            continue
            
        total_factual_claims += 1
        
        if not claim.citations:
            claim.status = "UNCITED"
            uncited_claims.append(claim)
            continue
            
        is_supported = False
        has_invalid = False
        
        for cit in claim.citations:
            if cit not in evidence_map:
                has_invalid = True
                continue
                
            ev_item = evidence_map[cit]
            ev_text = ev_item.get("headline", "") + " " + ev_item.get("raw_snippet", "") + " " + " ".join(ev_item.get("extracted_facts", []))
            
            if check_lexical_support(claim.text, ev_text, threshold=support_threshold):
                is_supported = True
                break # Supported by at least one cited evidence
                
        if has_invalid and not is_supported:
            claim.status = "INVALID_CITATION"
            # It's an invalid citation claim, but we already track invalid_citations globally
            unsupported_claims.append(claim)
        elif is_supported:
            claim.status = "SUPPORTED"
            supported_claims.append(claim)
        else:
            claim.status = "UNSUPPORTED"
            unsupported_claims.append(claim)
            
    if total_factual_claims == 0:
        grounding_score = 1.0
    else:
        grounding_score = len(supported_claims) / total_factual_claims
        
    accepted = True
    reasons = []
    
    if invalid_citations:
        accepted = False
        reasons.append(f"Invalid citations found: {', '.join(invalid_citations)}")
        
    if uncited_claims:
        accepted = False
        reasons.append(f"{len(uncited_claims)} uncited factual claims found.")
        
    if unsupported_claims:
        accepted = False
        reasons.append(f"{len(unsupported_claims)} cited but unsupported factual claims found.")
        
    if total_factual_claims > 0 and grounding_score < 1.0:
        accepted = False
        reasons.append(f"Grounding score {grounding_score:.2f} is below 1.0.")
        
    reason_str = " | ".join(reasons) if reasons else "Answer meets all grounding requirements."
    grounded = accepted
    
    return ValidationResult(
        accepted=accepted,
        grounded=grounded,
        grounding_score=grounding_score,
        claims=claims,
        supported_claims=supported_claims,
        unsupported_claims=unsupported_claims,
        uncited_claims=uncited_claims,
        invalid_citations=list(invalid_citations),
        cited_evidence_ids=list(cited_evidence_ids),
        reason=reason_str
    )
