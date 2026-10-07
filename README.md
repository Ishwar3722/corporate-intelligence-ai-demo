# Corporate Intelligence AI Demo (Repo 2)

A focused, evidence-grounded corporate intelligence assistant built with Streamlit and Gemini.

This repository (Repo 2) serves as an independent, deterministic demonstration of an AI workflow constrained entirely by a provided static knowledge base. It does not integrate with any external Repo 1 data systems.

## What the Demo Does

This application answers business questions using *only* the supplied evidence. When a user asks a question, the application:
1. Retrieves relevant text snippets from a static fixture.
2. Constructs a controlled prompt incorporating this evidence.
3. Uses Gemini for synthesis.
4. Independently validates the generated answer to ensure every claim traces back to the retrieved evidence.
5. Surfaces transparency and audit details directly in the UI.

## The Evidence-Grounded Pipeline

The architecture is explicitly designed to prevent hallucinations and fabricated claims:

`Question → Deterministic Retrieval → Controlled Context → Grounded Prompt → Gemini → Grounding/Citation Validation → UI`

## Possible Answer States (M9)

To build trust, the UI clearly displays the validation outcome in one of three states:

*   **Grounded / Accepted**: The system successfully generated an answer and validated that every claim is supported by the retrieved evidence.
*   **Insufficient Evidence**: The retrieval step yielded no relevant evidence from the static database. The system refuses to invoke the LLM and will not generate an answer from outside knowledge.
*   **Rejected**: The system generated an answer, but the independent validation step found unsupported or uncited claims. The UI transparently presents the rejected answer along with the validation failure details.

## Current Knowledge-Base Limitation

The application uses a **static demo knowledge base** (currently a JSON fixture of sample financial data). It does **not** use live market data, real-time financial APIs, enterprise intelligence databases, or external search tools. 

## Live Demo / Deployment

*(Live Demo: to be deployed)*

1. Deploy the GitHub repository to Streamlit Community Cloud.
2. Select `main` branch and `app.py`.
3. Open Advanced settings / Secrets.
4. Add the root-level secret:

   `GEMINI_API_KEY = "your_api_key_here"`

5. Deploy.

*(Note: Streamlit Community Cloud automatically maps root-level secrets into native OS environment variables. The application reads this securely via the existing environment-variable interface (`os.environ.get`), meaning the actual secret must never be committed.)*

**Default Model:** The application defaults to using `gemini-3.7-flash`. To override this, you can optionally configure `GEMINI_MODEL` as an environment variable or secret.

## How to Run the Demo

1.  **Clone the repository**
2.  **Create a virtual environment and install dependencies**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Set your `GEMINI_API_KEY` as an environment variable**:
    ```powershell
    $env:GEMINI_API_KEY="your_api_key_here"
    ```
    *(Security Note: Do not hardcode the API key in the source files. The application expects it to be securely supplied through the environment.)*
4.  **Run the Streamlit application**:
    ```bash
    streamlit run app.py
    ```

## Example Supported Question

Once the application is running, you can test the "Grounded / Accepted" state by clicking the suggested question or typing:

> "What was Alphabet's revenue in Q4 2023?"
