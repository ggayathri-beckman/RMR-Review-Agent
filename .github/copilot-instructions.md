# Copilot Instructions — RMR Review Agent

This repository is a tool + agent for reviewing **Risk Management Reports (RMR)**:
comprehensive reports of all security activities.

## Domain rules (always apply)

- An RMR is validated against a **master template** (`templates/`), the **RMR
  report** under review (`rmr/`), and **supporting security reports** (`reports/`).
- **Black text = fixed boilerplate** ? must never change.
- **Blue text = placeholders** ? must be updated; flag if empty or unchanged.
- Values in the RMR must be backed by the supporting reports.
- The authoritative acceptance criteria is **`.github/RMR-Checklist.md`**. Every
  RMR review must work through that checklist and report PASS / FAIL / N/A per item.
- Several checklist items are conditional on whether the product is a **Cyber
  Device** or **Non-Cyber Device** — determine this first.

## Project layout

- `src/review_agent.py` — CLI entry point.
- `src/docx_reader.py` — reads `.docx` text + font colors (blue vs black detection).
- `src/rules.py` — deterministic rules engine (`Finding` dataclass).
- `src/scoring.py` — correctness + precision scores.
- `src/commenter.py` — writes native Word comments into a `.reviewed.docx` copy.
- `rules.yaml` — editable team rules and score weights.

## How to run

```
python src/review_agent.py --rmr "rmr/<file>.docx" --template "templates/<file>.docx" --reports "reports" --write-comments
```

## Conventions

- New rule types are registered in `src/rules.py` via the `@rule_type("name")`
  decorator and must return a list of `Finding` objects.
- Keep findings in the `Finding` format so scoring and commenting keep working.
- Never send document contents to external services unless the user explicitly asks.
