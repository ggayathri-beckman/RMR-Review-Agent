"""Scoring for the RMR Review Agent.

Two scores are produced:
  - correctness_score: 100 minus weighted penalties from findings.
  - precision_score:   how well the claimed security activities are backed by
                       actual supporting reports in the reports folder.
                       (e.g. if the RMR claims SAST and VA, both a SAST report
                       and a VA report must exist in reports/).
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import List

from docx_reader import DocxContent
from rules import EvidenceResult, Finding


@dataclass
class Scores:
    correctness: float
    precision: float
    findings_count: int
    claimed_activities: int = 0
    backed_activities: int = 0


def compute_scores(findings: List[Finding], rmr: DocxContent,
                   template: DocxContent, weights: dict,
                   evidence: List[EvidenceResult] = None) -> Scores:
    # Correctness: start at 100, subtract weighted penalties (capped at 0).
    penalty = 0.0
    for f in findings:
        penalty += float(weights.get(f.severity, 1))
    correctness = max(0.0, 100.0 - penalty)

    # Precision: of the security activities the RMR claims, how many are backed
    # by an actual supporting report in the reports folder.
    claimed = [e for e in (evidence or []) if e.claimed]
    backed = [e for e in claimed if e.backed]
    total_claimed = len(claimed)

    if total_claimed == 0:
        precision = 100.0
    else:
        precision = round(len(backed) / total_claimed * 100.0, 1)

    return Scores(correctness=round(correctness, 1),
                  precision=precision,
                  findings_count=len(findings),
                  claimed_activities=total_claimed,
                  backed_activities=len(backed))
