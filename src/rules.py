"""Rules engine for the RMR Review Agent.

Each rule produces zero or more Findings. Findings feed both the review
comments and the scoring.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Callable, Dict, List

from docx_reader import DocxContent


@dataclass
class Finding:
    rule_id: str
    severity: str          # critical | major | minor
    message: str
    location: str = ""     # e.g. paragraph text snippet


RuleFunc = Callable[[dict, DocxContent, DocxContent, List[DocxContent]], List[Finding]]

_REGISTRY: Dict[str, RuleFunc] = {}


def rule_type(name: str):
    def deco(fn: RuleFunc) -> RuleFunc:
        _REGISTRY[name] = fn
        return fn
    return deco


@rule_type("blue_must_change")
def _blue_must_change(cfg, rmr, template, reports) -> List[Finding]:
    findings: List[Finding] = []
    template_blue = {r.text.strip() for r in (template.blue_runs if template else [])}
    for run in rmr.blue_runs:
        text = run.text.strip()
        if not text:
            findings.append(
                Finding(cfg["id"], cfg["severity"],
                        "A blue placeholder is empty and must be filled in."))
        elif text in template_blue:
            findings.append(
                Finding(cfg["id"], cfg["severity"],
                        f"Blue placeholder still contains template text: '{text}'",
                        location=text))
    return findings


@rule_type("black_must_match")
def _black_must_match(cfg, rmr, template, reports) -> List[Finding]:
    findings: List[Finding] = []
    if not template:
        return findings
    template_black = {r.text.strip() for r in template.black_runs if r.text.strip()}
    rmr_black = {r.text.strip() for r in rmr.black_runs if r.text.strip()}
    for missing in template_black - rmr_black:
        findings.append(
            Finding(cfg["id"], cfg["severity"],
                    f"Fixed (black) boilerplate appears changed or missing: '{missing}'",
                    location=missing))
    return findings


@rule_type("not_empty")
def _not_empty(cfg, rmr, template, reports) -> List[Finding]:
    target = cfg.get("target", "")
    if target and target.lower() not in rmr.full_text.lower():
        return [Finding(cfg["id"], cfg["severity"],
                        f"Required field '{target}' not found or left blank.")]
    return []


@rule_type("required_section")
def _required_section(cfg, rmr, template, reports) -> List[Finding]:
    target = cfg.get("target", "")
    if target and target.lower() not in rmr.full_text.lower():
        return [Finding(cfg["id"], cfg["severity"],
                        f"Required section '{target}' is missing.")]
    return []


@rule_type("cross_check")
def _cross_check(cfg, rmr, template, reports) -> List[Finding]:
    # Value present in RMR must also appear in at least one supporting report.
    target = cfg.get("target", "")
    if not target:
        return []
    in_rmr = target.lower() in rmr.full_text.lower()
    in_reports = any(target.lower() in r.full_text.lower() for r in reports)
    if in_rmr and not in_reports:
        return [Finding(cfg["id"], cfg["severity"],
                        f"'{target}' is in the RMR but not backed by any supporting report.")]
    return []


@rule_type("placeholder_tokens")
def _placeholder_tokens(cfg, rmr, template, reports) -> List[Finding]:
    """Flag leftover template placeholder tokens still present in the RMR.

    Works without font color (also on PDF-derived text). Detects the literal
    placeholder conventions used by the GLB-QS-TMP-0186 template.
    """
    import re

    findings: List[Finding] = []
    text = rmr.full_text

    # Literal named placeholders (e.g. EnterInformationHere, EnterProductName).
    for token in cfg.get("tokens", []):
        if token.lower() in text.lower():
            findings.append(
                Finding(cfg["id"], cfg["severity"],
                        f"Placeholder '{token}' is still present and must be replaced.",
                        location=token))

    # Bracket / merge-field patterns: angle-brackets, EDMS fields, [Enter...].
    patterns = cfg.get("patterns", [])
    for pat in patterns:
        for match in re.findall(pat, text):
            snippet = match if isinstance(match, str) else " ".join(match)
            findings.append(
                Finding(cfg["id"], cfg["severity"],
                        f"Unfilled placeholder pattern found: '{snippet.strip()[:60]}'",
                        location=snippet.strip()[:60]))
    return findings


@rule_type("must_be_removed")
def _must_be_removed(cfg, rmr, template, reports) -> List[Finding]:
    """Flag template-only content that must be deleted from the final RMR.

    e.g. the Template Instructions / Translations pages, and blue instruction
    text that must be removed before routing for approval.
    """
    findings: List[Finding] = []
    text = rmr.full_text.lower()
    for marker in cfg.get("markers", []):
        if marker.lower() in text:
            findings.append(
                Finding(cfg["id"], cfg["severity"],
                        f"Template-only content must be removed from the report: '{marker}'",
                        location=marker))
    return findings


@dataclass
class EvidenceResult:
    activity: str          # e.g. "SAST"
    claimed: bool          # mentioned in the RMR?
    backed: bool           # a matching report exists in reports/?
    matched_reports: List[str]  # file names that satisfied it


def _activity_aliases(activity_cfg: dict) -> List[str]:
    names = [activity_cfg.get("name", "")]
    names += activity_cfg.get("aliases", [])
    return [n for n in names if n]


def check_evidence(activities_cfg, rmr, reports):
    """Verify that every security activity the RMR claims is backed by a report.

    Returns (findings, results). An activity is:
      - "claimed" if any of its names/aliases appears in the RMR text.
      - "backed"  if a report file name OR report content matches the activity.
    """
    import os

    findings: List[Finding] = []
    results: List[EvidenceResult] = []
    rmr_text = rmr.full_text.lower()

    for act in activities_cfg:
        aliases = _activity_aliases(act)
        severity = act.get("severity", "major")
        rule_id = act.get("id", f"evidence-{act.get('name', 'activity')}")

        claimed = any(a.lower() in rmr_text for a in aliases)
        if not claimed:
            results.append(EvidenceResult(act.get("name", ""), False, False, []))
            continue

        matched = []
        for rep in reports:
            fname = os.path.basename(rep.path).lower()
            hay = fname + " " + rep.full_text.lower()
            if any(a.lower() in hay for a in aliases):
                matched.append(os.path.basename(rep.path))

        backed = len(matched) > 0
        results.append(EvidenceResult(act.get("name", ""), True, backed, matched))

        if not backed:
            findings.append(
                Finding(rule_id, severity,
                        f"The RMR claims '{act.get('name')}' activity, but no supporting "
                        f"report was found in the reports folder.",
                        location=act.get("name", "")))
    return findings, results


def run_rules(rules_cfg: List[dict], rmr: DocxContent,
              template: DocxContent, reports: List[DocxContent]) -> List[Finding]:
    findings: List[Finding] = []
    for cfg in rules_cfg:
        fn = _REGISTRY.get(cfg.get("type", ""))
        if fn is None:
            continue
        findings.extend(fn(cfg, rmr, template, reports))
    return findings
