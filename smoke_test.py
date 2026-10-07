import json
import os
from src.retrieval import retrieve
from src.context_builder import build_context
from src.prompt_builder import build_prompt
from src.gemini_adapter import generate

def main():
    # 1. Load the evidence fixture.
    fixture_path = os.path.join("data", "sample_evidence.json")
    with open(fixture_path, "r", encoding="utf-8") as f:
        evidence_store = json.load(f)

    # Question for the smoke test
    question = "What was Alphabet's revenue in Q4 2023?"

    # 2. Retrieve evidence using the existing deterministic retriever.
    retrieved_evidence = retrieve(question, evidence_store, top_k=5, threshold=1.0)

    # 3. Build controlled context.
    context = build_context(retrieved_evidence)

    # 4. Build the existing grounded prompt.
    prompt = build_prompt(context, question)

    print("Sending prompt to Gemini...")
    
    # 5. Send the prompt through the Gemini adapter.
    try:
        response = generate(prompt)
        
        # 6. Print the raw model response.
        print("\nUNVALIDATED MODEL OUTPUT")
        print("------------------------")
        print(response)
        print("------------------------")
    except Exception as e:
        print(f"Error during Gemini generation: {e}")
        import sys
        sys.exit(1)

if __name__ == "__main__":
    main()
