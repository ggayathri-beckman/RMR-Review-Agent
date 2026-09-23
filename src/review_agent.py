"""RMR Review Agent - command line entry point.

Usage:
    python src/review_agent.py \
        --rmr "rmr/MyReport.docx" \
        --reports "reports" \
        --template "templates/RMR_Template.docx" \
        [--rules rules.yaml] [--write-comments]
"""
from __future__ import annotations

import argparse
import glob
import os
import sys
from typing import List

import yaml

from docx_reader import DocxContent, read_docx, read_document
from rules import Finding, run_rules
from scoring import compute_scores


def load_reports(folder: str) -> List[DocxContent]:
    reports: List[DocxContent] = []
    if not folder or not os.path.isdir(folder):
        return reports
    for pattern in ("*.docx", "*.pdf"):
        for path in glob.glob(os.path.join(folder, "**", pattern), recursive=True):
            if os.path.basename(path).startswith("~$"):
                continue
            reports.append(read_document(path))
    return reports


def print_report(findings: List[Finding], scores, evidence=None) -> None:
    print("\n" + "=" * 60)
    print("RMR REVIEW RESULT")
    print("=" * 60)

    if not findings:
        print("No issues found. ")
    else:
        order = {"critical": 0, "major": 1, "minor": 2}
        for f in sorted(findings, key=lambda x: order.get(x.severity, 3)):
            loc = f" (near: '{f.location[:50]}')" if f.location else ""
            print(f"  [{f.severity.upper():8}] {f.message}{loc}")

    if evidence:
        print("-" * 60)
        print("  EVIDENCE COVERAGE (claimed activity -> supporting report):")
        claimed = [e for e in evidence if e.claimed]
        if not claimed:
            print("    No known security activities were claimed in the RMR.")
        for e in claimed:
            if e.backed:
                print(f"    [OK]      {e.activity}: {', '.join(e.matched_reports)}")
            else:
                print(f"    [MISSING] {e.activity}: no supporting report found")

    print("-" * 60)
    print(f"  Issues found     : {scores.findings_count}")
    print(f"  Correctness score: {scores.correctness} / 100")
    print(f"  Precision score  : {scores.precision} / 100 "
          f"({scores.backed_activities}/{scores.claimed_activities} claimed activities backed)")
    print("=" * 60 + "\n")


def main(argv=None) -> int:
    parser = argparse.ArgumentParser(description="Review an RMR .docx report.")
    parser.add_argument("--rmr", required=True, help="Path to the RMR .docx to review.")
    parser.add_argument("--reports", default="reports", help="Folder with supporting .docx reports.")
    parser.add_argument("--template", default="", help="Path to the master template .docx.")
    parser.add_argument("--rules", default="rules.yaml", help="Path to the rules file.")
    parser.add_argument("--write-comments", action="store_true",
                        help="Write a commented copy of the RMR.")
    args = parser.parse_args(argv)

    if not os.path.isfile(args.rmr):
        print(f"ERROR: RMR file not found: {args.rmr}", file=sys.stderr)
        return 2

    with open(args.rules, "r", encoding="utf-8") as fh:
        rules_doc = yaml.safe_load(fh) or {}
    rules_cfg = rules_doc.get("rules", [])
    weights = rules_doc.get("scoring", {}).get("weights", {})
    activities_cfg = rules_doc.get("activities", [])

    rmr = read_document(args.rmr)
    template = read_document(args.template) if args.template and os.path.isfile(args.template) else None
    reports = load_reports(args.reports)

    findings = run_rules(rules_cfg, rmr, template, reports)

    from rules import check_evidence
    evidence_findings, evidence = check_evidence(activities_cfg, rmr, reports)
    findings.extend(evidence_findings)

    scores = compute_scores(findings, rmr, template, weights, evidence)

    print_report(findings, scores, evidence)

    if args.write_comments:
        from commenter import write_comments
        out = write_comments(args.rmr, findings)
        print(f"Commented copy written to: {out}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
