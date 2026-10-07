import pytest
from src.prompt_builder import build_prompt

def test_grounding_instructions():
    prompt = build_prompt("Context", "Question")
    
    assert "Use ONLY the evidence supplied below." in prompt
    assert "Do not invent facts." in prompt
    assert "Do not use outside knowledge." in prompt
    assert "Every factual claim must cite one or more evidence IDs." in prompt
    assert "Clearly label inference or uncertainty." in prompt
    assert "If the evidence is insufficient, say so." in prompt
    assert "Preserve units, dates and currencies exactly as supplied." in prompt
    assert "Do not fabricate evidence IDs or citations." in prompt

def test_question_preservation():
    question = "What were Alphabet Inc.'s Q4 2023 revenues?"
    prompt = build_prompt("Context", question)
    assert question in prompt

def test_context_preservation():
    context = "Evidence ID: ev_001\nRevenues were $86.3 billion."
    prompt = build_prompt(context, "Question")
    assert context in prompt

def test_deterministic_output():
    context = "Evidence ID: ev_001"
    question = "What is the revenue?"
    prompt1 = build_prompt(context, question)
    prompt2 = build_prompt(context, question)
    
    assert prompt1 == prompt2

def test_empty_context():
    question = "What is the revenue?"
    prompt = build_prompt("", question)
    
    # Should still contain instructions, the question, and an empty evidence block
    assert "If the evidence is insufficient, say so." in prompt
    assert "USER QUESTION:\nWhat is the revenue?" in prompt
    assert "SUPPLIED EVIDENCE:" in prompt

def test_separation():
    prompt = build_prompt("Some context", "Some question")
    assert "SYSTEM:" in prompt
    assert "USER QUESTION:" in prompt
    assert "SUPPLIED EVIDENCE:" in prompt
    
    # Check order
    sys_idx = prompt.find("SYSTEM:")
    q_idx = prompt.find("USER QUESTION:")
    ev_idx = prompt.find("SUPPLIED EVIDENCE:")
    
    assert sys_idx < q_idx < ev_idx
