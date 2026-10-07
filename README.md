# Corporate Intelligence AI

**Evidence-grounded business Q&A that refuses to guess when the available evidence is insufficient.**

- **Live Demo**: [https://corporate-intelligence-ai.streamlit.app](https://corporate-intelligence-ai.streamlit.app)
- **GitHub**: [https://github.com/Ishwar3722/corporate-intelligence-ai-demo](https://github.com/Ishwar3722/corporate-intelligence-ai-demo)

---

## Product Overview

**PROBLEM:**
LLMs can produce confident answers that are not supported by the underlying evidence. In business and enterprise contexts, this creates a trust and verification problem.

**SOLUTION:**
This prototype uses an evidence-first pipeline that retrieves relevant evidence, constrains the LLM context, requires citations, validates generated claims, and refuses to answer when sufficient evidence is unavailable.

*Note: This is a prototype/demo and not an enterprise production system.*

---

## Try the Live Demo

### The Happy Path
> **"What was Alphabet's revenue in Q4 2023?"**

**Expected behavior:** A grounded answer using the supplied evidence and citation.

### The Boundary Test
> **"Tell me about cars."**

**Expected behavior:** `INSUFFICIENT EVIDENCE`. The system should not call Gemini when deterministic retrieval finds no supporting evidence.

**LLM Transient Failure Handling:**
If Gemini returns a transient 503 availability error, the application displays:
`EVIDENCE AVAILABLE — AI SYNTHESIS TEMPORARILY UNAVAILABLE`
This means the application can show the retrieved evidence without fabricating an AI-generated answer.

---

## Why This Design

| Problem | Design Response |
| :--- | :--- |
| **Hallucination risk** | Evidence-constrained prompting |
| **Unsupported questions** | Evidence sufficiency gate |
| **Unsupported factual claims** | Claim/citation validation |
| **LLM transient failure** | Evidence fallback |
| **Transparency** | Retrieved evidence/context/prompt/validation shown in UI |

---

## Architecture

```text
User Question
      ↓
Deterministic Evidence Retrieval
      ↓
(Insufficient Evidence Gate) ----→ (Stop: No AI Generation)
      ↓
Controlled Context Construction
      ↓
Grounded Prompt
      ↓
Gemini
      ↓
(503 Fallback) ------------------→ (Display Evidence Only)
      ↓
Claim / Citation Validation
      ↓
Grounded Answer
```

---

## How It Works

1. **Evidence Retrieval**
   - deterministic token/keyword overlap
   - deterministic ranking
   - zero-score evidence excluded

2. **Context Builder**
   - constructs bounded evidence blocks
   - preserves provenance
   - respects character limit

3. **Prompt Builder**
   - instructs Gemini to use only supplied evidence
   - requires evidence citations
   - prohibits invented facts
   - requires uncertainty when evidence is insufficient

4. **Gemini Adapter**
   - isolated LLM interface
   - Gemini API
   - environment-based secret handling

5. **Grounding Validator**
   - extracts claims
   - checks citations
   - checks lexical support against supplied evidence
   - rejects unsupported/uncited/invalid claims

6. **Evidence Sufficiency Gate**
   - prevents unnecessary LLM calls when retrieval returns no evidence

7. **503 Fallback**
   - distinguishes model availability from evidence availability
   - shows retrieved evidence when synthesis is temporarily unavailable
   - does not fabricate an answer

---

## Answer States

### GROUNDED / ACCEPTED
Evidence was retrieved and the generated answer passed grounding validation.

### INSUFFICIENT EVIDENCE
The knowledge base does not contain sufficient evidence. No LLM generation is attempted.

### REJECTED — INSUFFICIENT GROUNDING
An answer was generated but failed grounding/citation validation.

### EVIDENCE AVAILABLE — AI SYNTHESIS TEMPORARILY UNAVAILABLE
The evidence exists, but Gemini returned a transient 503. The system shows the evidence rather than fabricating an answer.

---

## Testing & Reliability

- 40 pytest tests currently pass.
- Tests cover retrieval, context construction, prompt construction, Gemini adapter behavior, grounding/citation validation, UI behavior, evidence sufficiency, permanent API failures, and 503 fallback behavior.
- The 503 regression test verifies that the fallback path completes without an application exception.
- The application has been tested on Streamlit Community Cloud.

---

## Tech Stack

- Python
- Streamlit
- Google Gemini API / google-genai
- pytest
- JSON evidence fixture

---

## Current Scope & Limitations

These are deliberate MVP constraints used to demonstrate the core grounding/control architecture:

- Static JSON evidence fixture
- Deterministic keyword/token retrieval
- No vector database
- No embeddings
- No live enterprise database
- No authentication
- No conversational memory
- One LLM provider
- Lexical grounding validation
- Current evidence set is intentionally small

---

## Future Extensions

*Potential future extensions:*

- embeddings/vector retrieval
- larger evidence stores
- approved read-only enterprise evidence integration
- richer semantic claim validation
- additional model providers
- authentication/access controls
- evaluation datasets and monitoring

---

## Local Setup

1. **Clone the repository**
2. **Create a virtual environment and install dependencies**:
   ```bash
   python -m venv venv
   venv\Scripts\activate
   pip install -r requirements.txt
   ```
3. **Configure API Key**:
   ```powershell
   $env:GEMINI_API_KEY="your_api_key_here"
   ```
   *(Optional)* Configure a specific model version:
   ```powershell
   $env:GEMINI_MODEL="gemini-3.7-flash"
   ```
4. **Run the Streamlit application**:
   ```bash
   streamlit run app.py
   ```
5. **Run the test suite**:
   ```bash
   pytest -q
   ```

---

*This project demonstrates an evidence-first approach to AI product design: constrain the information available to the model, test whether the generated answer is supported, and fail safely when it is not.*
