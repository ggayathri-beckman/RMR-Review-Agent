---
mode: 'agent'
description: 'Run a full RMR review and produce findings, scores, and suggested Word comments.'
tools: ['codebase', 'search', 'runCommands', 'editFiles']
---

# /rmr-review

Review a Risk Management Report end to end.

## Inputs
- RMR file: `${input:rmrPath:Path to the RMR .docx (e.g. rmr/report.docx)}`
- Template: `${input:templatePath:Path to the template .docx (e.g. templates/RMR_Template.docx)}`

## Steps

1. Read the RMR, the supporting reports in `reports/`, and the template.
2. Determine whether the product is a **Cyber Device** or **Non-Cyber Device**
   (several checklist items are conditional on this).
3. Work through **every item in `.github/RMR-Checklist.md`** and mark each
   PASS / FAIL / N/A with its location and a short reason.
4. For *(evidence)* items, confirm the referenced report (SCR, VA, PT, SBOM,
   etc.) actually exists in `reports/`; if missing, mark FAIL.
5. Optionally run the deterministic engine to cross-check structural findings:
   ```
   python src/review_agent.py --rmr "${input:rmrPath}" --template "${input:templatePath}" --reports "reports" --write-comments
   ```

## Output

- **Summary** verdict (and Cyber Device: yes/no).
- **Checklist results** table: Section | Question | Result | Location | Comment.
- **Findings** (the FAIL items) grouped by Critical / Major / Minor, each with location + fix.
- **Correctness score /100** = passed / (passed + failed), excluding N/A.
- **Precision score /100** = backed activities / claimed activities.
- **Evidence coverage** list.
- **Suggested Word comments**, ready to paste, per location.

Do not invent facts not supported by the RMR or the reports.
