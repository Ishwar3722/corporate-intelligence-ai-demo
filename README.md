# Corporate Intelligence AI Demo (Repo 2)

Repo 2 is an independent AI showcase. The initial evidence source is a static local fixture.
Repo 1 is intentionally not required to run the demo.
Repo 1 has no implementation dependency in this milestone.

The current milestone implements:
* deterministic evidence retrieval
* controlled evidence context construction
* grounded prompt construction
* Gemini model generation
* deterministic citation parsing
* evidence-ID validation
* rule-based claim classification
* lexical evidence-support checking
* grounding scoring
* automatic acceptance/rejection

Please note:
* Evidence is still provided by the local static fixture.
* Repo 1 is not required.
* This is a deterministic MVP grounding validator, not a perfect semantic truth verifier. It uses lexical evidence matching and lightweight clause-level claim heuristics.
