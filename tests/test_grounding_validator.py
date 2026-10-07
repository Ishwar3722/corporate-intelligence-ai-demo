import pytest
from src.grounding_validator import validate_answer, Claim, ValidationResult

EVIDENCE_MOCK = [
    {
        "evidence_id": "ev_001",
        "headline": "Alphabet Q4 2023 Earnings",
        "raw_snippet": "Alphabet generated $86.3 billion in Q4 2023 revenue.",
        "extracted_facts": ["Alphabet revenue was $86.3 billion in Q4 2023"]
    },
    {
        "evidence_id": "ev_002",
        "headline": "Cloud Growth",
        "raw_snippet": "Google Cloud revenue grew 26% year-over-year.",
        "extracted_facts": ["Google Cloud revenue grew 26%"]
    }
]

def test_fully_supported_answer():
    answer = "Alphabet generated $86.3 billion in Q4 2023 [ev_001]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is True
    assert result.grounded is True
    assert result.grounding_score == 1.0
    assert len(result.supported_claims) == 1
    assert len(result.unsupported_claims) == 0
    assert len(result.uncited_claims) == 0
    assert len(result.invalid_citations) == 0

def test_invalid_citation():
    answer = "Alphabet generated $86.3 billion in Q4 2023 [ev_999]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert result.grounded is False
    assert "ev_999" in result.invalid_citations
    assert len(result.unsupported_claims) == 1

def test_uncited_factual_claim():
    answer = "Alphabet generated $86.3 billion in Q4 2023."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert result.grounded is False
    assert len(result.uncited_claims) == 1
    assert result.grounding_score == 0.0

def test_cited_but_irrelevant_evidence():
    # Valid evidence ID, but snippet doesn't match claim
    answer = "Alphabet released a new AI model [ev_002]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert result.grounded is False
    assert len(result.unsupported_claims) == 1
    assert result.grounding_score == 0.0

def test_mixed_answer():
    answer = "Alphabet generated $86.3 billion in Q4 2023 [ev_001]. They also released a new car [ev_002]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert result.grounded is False
    assert len(result.supported_claims) == 1
    assert len(result.unsupported_claims) == 1
    assert result.grounding_score == 0.5

def test_no_citations():
    answer = "Alphabet generated revenue. Google Cloud grew."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert result.grounded is False
    assert len(result.uncited_claims) == 2
    assert result.grounding_score == 0.0

def test_clearly_labeled_inference():
    answer = "It is likely that Alphabet will continue to grow. This suggests a strong future."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    # Inference should not be treated as a factual claim requiring citation
    assert result.accepted is True
    assert result.grounding_score == 1.0 # 0 factual claims -> 1.0
    assert len(result.uncited_claims) == 0
    assert len([c for c in result.claims if c.is_inference]) == 2

def test_empty_evidence():
    answer = "Alphabet generated $86.3 billion [ev_001]."
    result = validate_answer(answer, [])
    
    assert result.accepted is False
    assert "ev_001" in result.invalid_citations
    assert len(result.unsupported_claims) == 1

def test_composite_claim_with_two_supporting_evidence_items():
    answer = "Alphabet generated $86.3 billion and Cloud grew 26% [ev_001] [ev_002]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is True
    assert result.grounding_score == 1.0
    assert len(result.supported_claims) == 2

def test_composite_claim_with_one_unsupported_clause():
    answer = "Alphabet generated $86.3 billion and Alphabet launched a new car [ev_001] [ev_002]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert len(result.supported_claims) == 1
    assert len(result.unsupported_claims) == 1
    assert result.grounding_score == 0.5
    
def test_composite_claim_with_only_one_relevant_citation():
    answer = "Alphabet generated $86.3 billion and Cloud grew 26% [ev_001]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert len(result.supported_claims) == 1
    assert len(result.unsupported_claims) == 1
    assert result.grounding_score == 0.5

def test_composite_claim_with_invalid_citation():
    answer = "Alphabet generated $86.3 billion and Cloud grew 26% [ev_001] [ev_999]."
    result = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result.accepted is False
    assert "ev_999" in result.invalid_citations
    
def test_determinism():
    answer = "Alphabet generated $86.3 billion [ev_001]."
    result1 = validate_answer(answer, EVIDENCE_MOCK)
    result2 = validate_answer(answer, EVIDENCE_MOCK)
    
    assert result1 == result2
