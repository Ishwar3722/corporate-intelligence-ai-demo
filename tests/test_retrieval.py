import json
import os
from src.retrieval import retrieve

def load_fixture():
    fixture_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'sample_evidence.json')
    with open(fixture_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def test_exact_query():
    evidence_store = load_fixture()
    question = evidence_store["query"]
    results = retrieve(question, evidence_store)
    
    assert len(results) > 0
    assert results[0]["evidence_id"] == "ev_001"

def test_closely_related_query():
    evidence_store = load_fixture()
    question = "How much revenue did Alphabet report in Q4 2023?"
    results = retrieve(question, evidence_store)
    
    assert len(results) > 0
    assert results[0]["evidence_id"] == "ev_001"

def test_unrelated_query():
    evidence_store = load_fixture()
    question = "Who won the super bowl in 2022?"
    results = retrieve(question, evidence_store)
    
    # Should not return ev_001 as highly relevant
    assert len(results) == 0

def test_determinism():
    evidence_store = load_fixture()
    question = "Alphabet revenue 2023"
    results1 = retrieve(question, evidence_store)
    results2 = retrieve(question, evidence_store)
    
    assert results1 == results2
