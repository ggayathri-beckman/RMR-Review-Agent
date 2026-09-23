"""Reads .docx files and extracts text runs along with their font color.

The template convention:
    - Black (or automatic/None) colored text = fixed boilerplate.
    - Blue colored text = placeholder that must be updated.

python-docx exposes the font color per run. Direct RGB colors are read
straight away. Theme colors are resolved best-effort.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional

from docx import Document
from docx.shared import RGBColor


# A run is considered "blue" when its blue channel dominates clearly.
def _is_blue(rgb: Optional[RGBColor]) -> bool:
    if rgb is None:
        return False
    r, g, b = rgb[0], rgb[1], rgb[2]
    return b > 120 and b >= r + 40 and b >= g + 40


def _is_black(rgb: Optional[RGBColor]) -> bool:
    # None means "automatic" which renders as black.
    if rgb is None:
        return True
    r, g, b = rgb[0], rgb[1], rgb[2]
    return r < 60 and g < 60 and b < 60


@dataclass
class Run:
    text: str
    color: Optional[RGBColor]

    @property
    def is_blue(self) -> bool:
        return _is_blue(self.color)

    @property
    def is_black(self) -> bool:
        return _is_black(self.color)


@dataclass
class Paragraph:
    runs: List[Run] = field(default_factory=list)

    @property
    def text(self) -> str:
        return "".join(r.text for r in self.runs)

    @property
    def blue_text(self) -> str:
        return "".join(r.text for r in self.runs if r.is_blue)


@dataclass
class DocxContent:
    path: str
    paragraphs: List[Paragraph] = field(default_factory=list)

    @property
    def full_text(self) -> str:
        return "\n".join(p.text for p in self.paragraphs)

    @property
    def blue_runs(self) -> List[Run]:
        return [r for p in self.paragraphs for r in p.runs if r.is_blue]

    @property
    def black_runs(self) -> List[Run]:
        return [r for p in self.paragraphs for r in p.runs if r.is_black]


def _run_color(run) -> Optional[RGBColor]:
    try:
        return run.font.color.rgb
    except Exception:
        return None


def read_docx(path: str) -> DocxContent:
    """Read a .docx file into a DocxContent structure (paragraphs + tables)."""
    document = Document(path)
    content = DocxContent(path=path)

    for para in document.paragraphs:
        content.paragraphs.append(
            Paragraph(runs=[Run(text=r.text, color=_run_color(r)) for r in para.runs])
        )

    # Include text inside tables (RMRs are table heavy).
    for table in document.tables:
        for row in table.rows:
            for cell in row.cells:
                for para in cell.paragraphs:
                    content.paragraphs.append(
                        Paragraph(
                            runs=[Run(text=r.text, color=_run_color(r)) for r in para.runs]
                        )
                    )

    return content


def read_pdf(path: str) -> DocxContent:
    """Read a .pdf into a DocxContent structure.

    PDFs carry no reliable font-color data, so blue/black detection does not
    apply; token/pattern and section rules still work on the extracted text.
    """
    from pypdf import PdfReader

    content = DocxContent(path=path)
    reader = PdfReader(path)
    for page in reader.pages:
        text = page.extract_text() or ""
        for line in text.splitlines():
            content.paragraphs.append(Paragraph(runs=[Run(text=line, color=None)]))
    return content


def read_document(path: str) -> DocxContent:
    """Read a .docx or .pdf file based on its extension."""
    if path.lower().endswith(".pdf"):
        return read_pdf(path)
    return read_docx(path)
