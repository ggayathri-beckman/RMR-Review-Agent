# RMR Review Agent

A tool to review **Risk Management Reports (RMR)** against a master template and
a set of supporting security reports, then produce review comments and a
quality score.

## What it does

1. Reads the RMR `.docx` and the supporting `.docx` files in `reports/`.
2. Understands the template convention:
   - **Black text** = fixed boilerplate that must NOT change.
   - **Blue text** = placeholders that MUST be updated.
3. Applies the rules defined in `rules.yaml`.
4. **Verifies evidence**: for every security activity the RMR claims (e.g. SAST,
   VA, Penetration Test, SBOM, Threat Model), it checks that a matching
   supporting report actually exists in `reports/`.
5. Outputs:
   - A list of review comments (what is wrong / what to fix).
   - An evidence-coverage list (claimed activity -> supporting report).
   - Optionally inserts native Word comments into a copy of the RMR.
   - A **correctness score** and a **precision score**.

### Scores

- **Correctness score /100** — starts at 100, subtracts weighted penalties for
  each rule violation (critical/major/minor weights from `rules.yaml`).
- **Precision score /100** — evidence coverage:
  `backed activities / claimed activities`. If the RMR says it performed SAST
  and VA, both a SAST report and a VA report must be present in `reports/`.

## Folder layout

```
templates/   -> master RMR template (.docx)
rmr/         -> the RMR report to be reviewed (.docx)
reports/     -> supporting security activity reports (.docx)
src/         -> the agent source code
rules.yaml   -> editable rules
```

## Setup

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

## Run

```powershell
python src/review_agent.py --rmr "rmr/MyReport.docx" --reports "reports" --template "templates/RMR_Template.docx"
```

Add `--write-comments` to produce a commented copy of the RMR.

## Use the Copilot AI agent (no API key needed)

This repo ships a custom GitHub Copilot agent so the whole team can review RMRs
straight from Copilot Chat.

Files that power it (all in `.github/`):
- `copilot-instructions.md` — always-on project context.
- `chatmodes/RMR Reviewer.chatmode.md` — a custom agent mode.
- `prompts/rmr-review.prompt.md` — a reusable `/rmr-review` command.

How to use in VS Code:
1. Reload the window after cloning so Copilot picks up the `.github` files.
2. Open **Copilot Chat**.
3. Either pick **RMR Reviewer** from the chat mode dropdown, or type
   `/rmr-review` and follow the prompts.

The agent reads the docs, runs `src/review_agent.py`, and returns findings,
scores, and suggested Word comments.

## Status

Scaffold in place. Drop the template into `templates/` and share the rules so
the rules engine and blue/black detection can be finalized.
