from __future__ import annotations

import hashlib
import json
import re
import shutil
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"


def main():
    source = PAPER / "build/main.pdf"
    document = pymupdf.open(source)
    assert 1 <= len(document) <= 10, f"Page cap exceeded: {len(document)}"
    all_text = " ".join(page.get_text() for page in document)
    normalized = " ".join(all_text.split())
    for author in ("Sumaiya Farhana Islam", "Adnan Bin Wahid", "Redowan Billah Sami", "Md. Touhidur Rahman"):
        assert author in normalized, f"Author absent: {author}"
    for email in ("bsse1450@iit.du.ac.bd", "bsse1442@iit.du.ac.bd", "bsse1409@iit.du.ac.bd", "bsse1432@iit.du.ac.bd"):
        assert email in normalized, f"Email absent: {email}"
    assert "[?]" not in normalized
    assert "REFERENCES" in normalized
    fonts = {font[0] for page in document for font in page.get_fonts() if font[0]}
    assert fonts and all(document.extract_font(xref)[3] for xref in fonts)
    assert "\ufffd" not in all_text, "Replacement glyph found in PDF"
    log = (PAPER / "build/main.log").read_text(encoding="utf-8", errors="replace")
    assert "undefined references" not in log.lower()
    assert not re.search(r"Citation .+ undefined", log)
    assert "Overfull \\hbox" not in log, "Review horizontal overflow before release"
    outside = []
    for page_index, page in enumerate(document):
        for word in page.get_text("words"):
            x0, y0, x1, y1 = word[:4]
            if x0 < 0 or y0 < 0 or x1 > page.rect.width or y1 > page.rect.height:
                outside.append({"page": page_index + 1, "word": word[4]})
    assert not outside, outside
    destination = PAPER / "manuscript.pdf"
    shutil.copy2(source, destination)
    preview = PAPER / "build/preview"
    preview.mkdir(exist_ok=True)
    for index, page in enumerate(document):
        page.get_pixmap(matrix=pymupdf.Matrix(1.3, 1.3)).save(preview / f"page-{index + 1:02d}.png")
    verification = {
        "page_count": len(document), "maximum_pages": 10,
        "compiler": "Tectonic 0.17.0 (XeTeX), standard IEEEtran journal class",
        "overleaf_recommended_compiler": "pdfLaTeX",
        "overleaf_build_not_executed": True,
        "authors_and_emails_verified": True, "unresolved_references": False,
        "all_fonts_embedded": True, "replacement_glyphs": 0,
        "horizontal_overflow": False, "text_outside_page": outside,
        "pdf_sha256": hashlib.sha256(destination.read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256((PAPER / "overleaf/main.tex").read_bytes()).hexdigest(),
        "evidence": "Completed standard run; no enhancement experiments rerun",
    }
    (PAPER / "verification.json").write_text(json.dumps(verification, indent=2) + "\n", encoding="ascii")
    print(json.dumps(verification, indent=2))


if __name__ == "__main__":
    main()
