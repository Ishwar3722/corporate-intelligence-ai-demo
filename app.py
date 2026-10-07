import os
import json
import streamlit as st

from src.retrieval import retrieve
from src.context_builder import build_context
from src.prompt_builder import build_prompt
from src.gemini_adapter import generate, GenerationError
from src.grounding_validator import validate_answer

st.set_page_config(page_title="Corporate Intelligence AI", layout="wide")

# --- HEADER ---
st.title("Corporate Intelligence AI")
st.subheader("Evidence-grounded business Q&A")
st.markdown("""
I built an evidence-grounded corporate intelligence assistant that retrieves relevant business evidence, constructs controlled context, uses Gemini for synthesis, and independently validates the resulting claims and citations. When the available evidence is insufficient, it refuses to fabricate an answer.
""")
st.caption("**Knowledge Base Scope:** Static demo knowledge base")

# --- SUGGESTED QUESTIONS ---
st.markdown("#### Suggested questions")

if "question_input" not in st.session_state:
    st.session_state.question_input = "What was Alphabet's revenue in Q4 2023?"

def set_q1(): st.session_state.question_input = "What was Alphabet's revenue in Q4 2023?"
def set_q2(): st.session_state.question_input = "How much did Alphabet's revenue grow year-over-year?"

col1, col2 = st.columns(2)
col1.button("What was Alphabet's revenue in Q4 2023?", on_click=set_q1, use_container_width=True)
col2.button("How much did Alphabet's revenue grow year-over-year?", on_click=set_q2, use_container_width=True)

st.markdown("---")

# --- INPUT ---
question = st.text_input("Ask a question about the supplied evidence...", key="question_input")

if st.button("Ask", type="primary"):
    if not question or not question.strip():
        st.warning("Please enter a question.")
        st.stop()
        
    api_key = os.environ.get("GEMINI_API_KEY", "")
    if not api_key:
        st.error("GEMINI_API_KEY is not set in the environment.")
        st.stop()
        
    try:
        with open("data/sample_evidence.json", "r", encoding="utf-8") as f:
            evidence_data = json.load(f)
    except Exception as e:
        st.error(f"Failed to load sample evidence: {e}")
        st.stop()
        
    with st.spinner("Executing pipeline..."):
        # Retrieve evidence
        retrieved_evidence = retrieve(question, evidence_data, top_k=5)
        
        # STATE 2: INSUFFICIENT EVIDENCE
        if not retrieved_evidence:
            st.error("### INSUFFICIENT EVIDENCE")
            st.markdown("I couldn't find sufficient evidence in the available knowledge base to answer this question reliably.")
            st.markdown("I will not generate an answer from outside knowledge.")
            st.stop()
            
        # Build context
        context = build_context(retrieved_evidence)
        
        # Build prompt
        prompt = build_prompt(context, question)
        
        # Generate
        try:
            raw_answer = generate(prompt)
        except GenerationError as e:
            st.error(f"Gemini API failure: {e}")
            st.stop()
        except Exception as e:
            st.error(f"Unexpected API failure: {e}")
            st.stop()
            
        # Validate
        validation_result = validate_answer(raw_answer, retrieved_evidence)
        
    # --- RESULT DISPLAY ---
    if validation_result.accepted:
        # STATE 1: GROUNDED / ACCEPTED
        st.success("### GROUNDED / ACCEPTED")
        st.markdown(f"#### Answer:\n{raw_answer}")
        st.markdown(f"**Grounding Score:** {validation_result.grounding_score:.2f}")
    else:
        # STATE 3: REJECTED
        st.error("### REJECTED — INSUFFICIENT GROUNDING")
        st.markdown(f"#### Model Answer:\n{raw_answer}")
        st.markdown(f"**Grounding Score:** {validation_result.grounding_score:.2f}")
        st.markdown(f"**Reason:** {validation_result.reason}")
        
        if validation_result.unsupported_claims:
            st.markdown(f"**Unsupported Claims:** {[c.text for c in validation_result.unsupported_claims]}")
        if validation_result.uncited_claims:
            st.markdown(f"**Uncited Claims:** {[c.text for c in validation_result.uncited_claims]}")
        if validation_result.invalid_citations:
            st.markdown(f"**Invalid Citations:** {validation_result.invalid_citations}")
            
    # --- EVIDENCE PRESENTATION ---
    st.markdown("---")
    st.subheader("Evidence Section")
    for ev in retrieved_evidence:
        with st.container(border=True):
            st.markdown(f"#### [{ev.get('evidence_id')}] {ev.get('headline')}")
            st.caption(f"**Source:** {ev.get('source_name')} | **Tier:** {ev.get('source_tier')} | [Source Link]({ev.get('source_url', '#')})")
            st.markdown(f"> *{ev.get('raw_snippet')}*")
            facts_str = ", ".join(ev.get("extracted_facts", []))
            st.markdown(f"**Extracted Facts:** {facts_str}")
            st.caption(f"Retrieval Score: {ev.get('score', 0):.2f}")
            
    # --- TRANSPARENCY / AUDIT SECTION ---
    st.markdown("---")
    st.subheader("Transparency / Audit Details")
    
    with st.expander("Evidence Used"):
        st.json(retrieved_evidence)
        
    with st.expander("Retrieved Context"):
        st.text(context)
        
    with st.expander("Grounded Prompt"):
        st.text(prompt)
        
    with st.expander("Validation Details"):
        st.write("#### Claims Analyzed")
        for claim in validation_result.claims:
            st.markdown(f"- **{claim.status}**: `{claim.text}` (citations: {claim.citations})")
        
        st.write("#### Summary")
        st.markdown(f"**Invalid Citations:** {validation_result.invalid_citations}")
        st.markdown(f"**Unsupported Claims:** {[c.text for c in validation_result.unsupported_claims]}")
        st.markdown(f"**Uncited Claims:** {[c.text for c in validation_result.uncited_claims]}")
