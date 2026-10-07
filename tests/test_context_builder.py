import pytest
from src.context_builder import build_context

@pytest.fixture
def sample_evidence_item():
    return {
        "evidence_id": "ev_001",
        "source_name": "Alphabet Inc.",
        "source_tier": "Tier1",
        "source_url": "https://abc.xyz",
        "headline": "Q4 Results",
        "raw_snippet": "Revenues were $86.3B.",
        "extracted_facts": ["Revenue up 13%"]
    }

def test_single_evidence(sample_evidence_item):
    context = build_context([sample_evidence_item])
    
    assert "[EVIDENCE ITEM]" in context
    assert "Evidence ID: ev_001" in context
    assert "Source: Alphabet Inc." in context
    assert "Source Tier: Tier1" in context
    assert "URL: https://abc.xyz" in context
    assert "Headline: Q4 Results" in context
    assert "Revenues were $86.3B." in context
    assert "- Revenue up 13%" in context

def test_multiple_evidence(sample_evidence_item):
    item2 = dict(sample_evidence_item)
    item2["evidence_id"] = "ev_002"
    item2["headline"] = "Other Results"
    
    context = build_context([sample_evidence_item, item2])
    
    assert "Evidence ID: ev_001" in context
    assert "Evidence ID: ev_002" in context
    assert context.count("[EVIDENCE ITEM]") == 2

def test_deterministic_output(sample_evidence_item):
    input_data = [sample_evidence_item]
    context1 = build_context(input_data)
    context2 = build_context(input_data)
    
    assert context1 == context2

def test_empty_evidence():
    assert build_context([]) == ""

def test_size_boundary(sample_evidence_item):
    # Calculate the exact size of one block
    one_block_context = build_context([sample_evidence_item])
    block_len = len(one_block_context)
    
    item2 = dict(sample_evidence_item)
    item2["evidence_id"] = "ev_002"
    
    # max_chars allows 1 block but not 2
    context = build_context([sample_evidence_item, item2], max_chars=block_len + 10)
    
    assert "ev_001" in context
    assert "ev_002" not in context
    assert len(context) <= block_len + 10

def test_provenance_preservation(sample_evidence_item):
    context = build_context([sample_evidence_item])
    assert "Evidence ID: ev_001" in context
    assert "URL: https://abc.xyz" in context
