"""Inserts native Word comments into a copy of the RMR .docx.

Requires python-docx >= 1.1.0 which added Paragraph.add_comment.
If the installed version is older, this degrades gracefully and the review
still works via the printed report.
"""
from __future__ import annotations

import os
from typing import List

from docx import Document

from rules import Finding


def write_comments(rmr_path: str, findings: List[Finding], author: str = "RMR Agent") -> str:
    document = Document(rmr_path)

    # Map a location snippet -> findings for quick lookup.
    by_location = {}
    general: List[Finding] = []
    for f in findings:
        if f.location:
            by_location.setdefault(f.location.strip(), []).append(f)
        else:
            general.append(f)

    supports_comments = hasattr(document.paragraphs[0], "add_comment") if document.paragraphs else False

    if supports_comments:
        for para in document.paragraphs:
            snippet = para.text.strip()
            if snippet in by_location:
                text = "\n".join(f"[{x.severity}] {x.message}" for x in by_location[snippet])
                try:
                    para.add_comment(text, author=author, initials="RMR")
                except Exception:
                    pass

    # Add general findings as a comment on the first paragraph if possible.
    if supports_comments and general and document.paragraphs:
        text = "\n".join(f"[{x.severity}] {x.message}" for x in general)
        try:
            document.paragraphs[0].add_comment(text, author=author, initials="RMR")
        except Exception:
            pass

    base, ext = os.path.splitext(rmr_path)
    out_path = f"{base}.reviewed{ext}"
    document.save(out_path)
    return out_path
