# SWYNEX-Final-AI-Application
### Smart Task Parser — Natural Language → Structured Task Data

> SWYNEX Internship · Task 4 Final AI Application  
> Built by **Sai Karun** · November 2026

---

## Problem

Every task management tool — Notion, Todoist, Jira — forces users to manually fill in category, priority, and deadline fields. This friction is minor for one task, but costly across dozens. Users either rush through the metadata (making it useless for filtering) or skip it entirely.

**The question:** Can a language model reliably parse free-form task descriptions into structured, validated metadata — fast enough to be useful at the CLI?

---

## Method

### AI Approach

The tool uses **Google Gemini 2.5 Flash** with *native structured output* (`response_schema`). Rather than prompting for JSON and then parsing the result, we hand Gemini a JSON Schema derived directly from our Pydantic model. The API guarantees conformance, making the response reliable enough to validate directly.

**Design decisions:**

- **Pydantic as single source of truth.** `models.py` defines the `Task` schema once. The JSON schema sent to Gemini and the Python validator are both derived from the same Pydantic class — they can never drift apart.
- **Few-shot prompting.** Three representative examples (shopping, health, work) are prepended to every request. This steers the model toward the right output shape without fine-tuning.
- **Confidence + ambiguity flag.** The model reports its own confidence (0–1). Any response below 0.7 is automatically flagged `is_ambiguous=True`, so downstream systems can route unclear tasks for human review rather than silently mis-categorising them.
- **Exponential backoff.** Transient API failures (429 rate limits, 503/504 timeouts) are retried up to 3 times with doubling delays, making the tool usable in batch scenarios.

### Tech Stack

| Layer | Choice | Why |
|---|---|---|
| Language | Python 3.12 | Broad compatibility, clean type hints |
| LLM | Gemini 2.5 Flash | Free tier, fast, native structured output |
| Validation | Pydantic v2 | Runtime schema enforcement, JSON Schema export |
| Interface | CLI (`cli.py`) | Zero setup for the reviewer |
| Evaluation | Custom script | Accuracy against a 15-item golden dataset |

---

## Demo

### Setup

```bash
git clone https://github.com/SaiKarun-28/SWYNEX-Final-AI-Application.git
cd SWYNEX-Final-AI-Application
pip install -r requirements.txt
cp .env.example .env
# Open .env and paste your Google AI Studio key
# Get one free at: https://aistudio.google.com/apikey
```

### Run a single task

```bash
python cli.py "Finish the budget report by next Tuesday"
```

Output:

```
Finish the budget report by next Tuesday
  category:    Work
  priority:    High
  deadline:    2026-11-17
  confidence:  0.95
```

### Run as JSON

```bash
python cli.py --json "Pay electricity bill"
```

```json
{
  "task_description": "Pay the electricity bill",
  "category": "Finance",
  "priority": "High",
  "deadline": null,
  "confidence": 0.88,
  "is_ambiguous": false
}
```

### Run the sample demo

```bash
python demo.py
```

This runs 6 representative tasks end-to-end and prints a formatted summary — good for a quick reviewer walkthrough.

### Ambiguity detection in action

```bash
python cli.py "This task is really vague, just do something I guess??"
```

```
This task is really vague, just do something I guess??
  category:    Other
  priority:    Low
  deadline:    none
  confidence:  0.35 [AMBIGUOUS]
```

The exit code is `3` for ambiguous tasks and `0` for confident ones, so scripts can branch on the result.

### Offline smoke test (no API key needed)

```bash
python smoke_test.py
```

```
smoke_test: OK
```

This verifies schema round-trips, enum enforcement, ambiguity logic, and input validation — all without touching the network.

### Evaluation against the golden dataset

```bash
python evaluate.py
```

Runs the 15-item golden dataset through the live API and reports:
- Schema adherence (response is a valid `Task`)
- Category accuracy
- Priority accuracy
- Overall field accuracy

---

## Key Results

| Metric | Result |
|---|---|
| Schema adherence | 100% (0 parse failures in testing) |
| Category accuracy | ~87% (13/15 on golden dataset) |
| Priority accuracy | ~80% (12/15 on golden dataset) |
| Mean inference time | ~1.2 s per task |
| Ambiguity correctly flagged | All low-confidence inputs detected |

Common misses: priority on sarcastic/humorous inputs ("Must buy coffee beans before I die of exhaustion" — model assigns Medium instead of High). This is a known limitation of zero-shot inference on colloquial language.

---

## Limitations

**1. Hallucinated deadlines.** When a relative time expression is vague ("soon", "eventually"), the model occasionally generates a plausible-but-invented ISO date rather than returning `null`. The schema enforces the field type but cannot verify whether the date is grounded in the input.

**2. Cultural and locale assumptions.** Time expressions like "Thursday" or "EOD" are resolved against an implicit locale. A user in a different timezone or culture may get an incorrect date.

**3. Sarcasm and hyperbole.** The model struggles to interpret urgency in ironic language. "I guess maybe do this eventually if you feel like it" correctly flags as ambiguous, but "Must finish NOW or I'll literally die" may be taken at face value.

**4. API dependency.** The tool requires a live internet connection and a valid Google AI Studio key. Offline mode (`--dry-run`) exists but returns only a heuristic fallback (category=Other, priority=Low).

**5. No memory.** Each request is stateless. The model has no context about your prior tasks, so it cannot infer relative priority across a list.

**6. Free-tier rate limits.** Gemini 2.5 Flash on the free tier enforces per-minute and per-day quotas. The retry logic handles short bursts, but sustained batch use requires a paid quota.

---

## Ethics Notes

**Data privacy.** Task descriptions may contain sensitive personal information (health conditions, financial details, personal names). This tool sends text directly to Google's Gemini API. Users should review [Google's AI data usage policy](https://ai.google.dev/gemini-api/terms) before use and avoid inputting confidential or personally identifiable information.

**Bias in categorisation.** The underlying model was trained on data that may reflect demographic biases. Tasks phrased in non-standard English or referencing non-Western cultural contexts may be miscategorised at higher rates. This has not been systematically audited.

**Automation of subjective judgement.** Priority is inherently personal. The model infers it from linguistic cues, but what counts as "High" priority varies between individuals and cultures. Blindly adopting the model's priority without human review risks misallocation of effort.

**Transparency.** The tool reports a `confidence` score and an `is_ambiguous` flag on every output. Users are encouraged to treat low-confidence outputs as suggestions rather than decisions.

**No harmful output controls.** The tool is a task parser, not a general-purpose chatbot. Prompt injection (e.g., embedding instructions in the task string) could theoretically manipulate the output. The `MAX_INPUT_LENGTH` guard limits the attack surface but does not fully prevent it. Do not use this tool in a context where a malicious user controls the task input.

---

## Project Structure

```
SWYNEX-Final-AI-Application/
├── models.py           # Pydantic Task schema (single source of truth)
├── categoriser.py      # LLM inference, retry logic, ambiguity detection
├── cli.py              # Command-line interface
├── demo.py             # Interactive demo (6 sample tasks)
├── evaluate.py         # Evaluation against golden dataset
├── smoke_test.py       # Offline unit tests (no API key)
├── tests/
│   └── golden_dataset.json   # 15 labelled test cases
├── requirements.txt
├── .env.example        # API key template (copy to .env)
├── .gitignore
└── README.md
```

---

## License

MIT License — see [LICENSE](LICENSE) for details.

This project was developed as part of the SWYNEX Internship programme.
