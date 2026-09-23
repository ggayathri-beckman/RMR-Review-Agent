# RMR Review Agent

An AI agent that reviews **Risk Management Reports (RMR)** — product security
reports — against a master template, an authoritative checklist, and the
supporting security reports, then returns findings, scores, and review comments.

## What it is

Given an RMR, the agent works through `.github/RMR-Checklist.md` and reports
**PASS / FAIL / N/A** for every item. It:

- Detects unfilled placeholders (`«approver1»`, `<<...>>`, `<...>`) and altered
  boilerplate (black text = fixed, blue text = must-update).
- Confirms every claimed activity (SCR, VA, Penetration Test, SBOM, SAST/DAST)
  is backed by a matching report in `reports/`.
- Determines whether the product is a **Cyber Device** or **Non-Cyber Device**
  (several checks depend on this).
- Produces a **Correctness score** (passed / applicable items) and a
  **Precision score** (backed / claimed activities), plus ready-to-paste
  review comments.

## What it needs

Place the input files in these folders:

| Folder        | Contents                                              |
| ------------- | ----------------------------------------------------- |
| `templates/`  | Master RMR template (`.docx` or `.pdf`)               |
| `rmr/`        | The RMR under review (`.docx` or `.pdf`)              |
| `reports/`    | Supporting reports — Nessus, Veracode, SBOM, etc.     |

Requirements:

- **VS Code + GitHub Copilot** (for the `/rmr-review` agent).
- **Python 3.11+** — only if you also want the deterministic cross-check engine.

## How to use

### Option A — Copilot agent (recommended, no setup)

1. Open this folder in VS Code and reload the window.
2. Open Copilot Chat, choose **RMR Reviewer** mode or type `/rmr-review`.
3. Enter the RMR and template paths when prompted.
4. Read the findings, scores, and suggested comments.

### Option B — Command line (deterministic engine)

```powershell
python -m venv env
Activate.ps1
pip install -r requirements.txt

python review_agent.py `
  --rmr "rmr/<report>.docx" `
  --template "templates/<template>.pdf" `
  --reports "reports" `
  --write-comments   # optional: writes a .reviewed.docx with Word comments
