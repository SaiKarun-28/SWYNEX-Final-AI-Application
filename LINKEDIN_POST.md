# LinkedIn Post — Task 4 (Final AI Application)

Copy and paste the post below. Attach a screenshot of a demo run in the terminal.

---

**Post text:**

Completed Task 4 of my internship with @SWYNEX Technologies — and it's the one I'm most proud of.

I built a **Smart Task Parser**: you type a natural language task like _"Finish the budget report by next Tuesday"_ and the tool instantly returns a structured, validated JSON object — category, priority, inferred deadline, and a confidence score.

**How it works:**
→ Powered by Google Gemini 2.5 Flash with native structured output (the API guarantees schema conformance, not just "try to return JSON")
→ Pydantic enforces the schema on the Python side — one model, zero drift between the validator and the API contract
→ Tasks below a confidence threshold are automatically flagged as ambiguous, so nothing gets silently miscategorised
→ Exponential backoff handles rate limits and transient failures gracefully
→ Offline smoke test verifies schema, enums, and ambiguity logic — no API key needed

**Example output:**

```
"Pay the electricity bill"
  category:    Finance
  priority:    High
  deadline:    none
  confidence:  0.88
```

**What I learnt:**
Structured output from LLMs is genuinely useful — but only when paired with runtime validation and transparent confidence signalling. The ethics of automating subjective judgements (what counts as "High priority"?) are real, and worth building in from day one.

GitHub: https://github.com/SaiKarun-28/SWYNEX-Final-AI-Application

#SWYNEX #Internship #Python #AI #LLM #Gemini #Productivity #MachineLearning

---

**Tip:** Attach a screenshot showing terminal output of `python demo.py` or `python cli.py "your task here"`. Screenshots get 3× more reach than text-only posts on LinkedIn.
