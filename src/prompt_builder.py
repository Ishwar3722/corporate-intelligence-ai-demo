def build_prompt(context: str, question: str) -> str:
    """
    Constructs a deterministic, grounded LLM prompt using strict policy rules,
    the user's question, and the supplied evidence context.
    """
    
    system_instruction = """SYSTEM:
You are a corporate research assistant.

Use ONLY the evidence supplied below.

Rules:
1. Do not invent facts.
2. Do not use outside knowledge.
3. Every factual claim must cite one or more evidence IDs.
4. Clearly label inference or uncertainty.
5. If the evidence is insufficient, say so.
6. Preserve units, dates and currencies exactly as supplied.
7. Do not fabricate evidence IDs or citations."""

    user_question_section = f"USER QUESTION:\n{question}"
    
    evidence_section = f"SUPPLIED EVIDENCE:\n{context}"
    
    # Assemble with clear separation
    prompt = f"{system_instruction}\n\n{user_question_section}\n\n{evidence_section}"
    
    return prompt.strip()
