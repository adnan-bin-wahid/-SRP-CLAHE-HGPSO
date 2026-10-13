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
    first_page = " ".join(document[0].get_text().split())
    tex = (PAPER / "overleaf/main.tex").read_text(encoding="ascii")
    assert r"\documentclass[conference]{IEEEtran}" in tex
    assert tex.count(r"\IEEEauthorblockN") == 4 and tex.count(r"\IEEEauthorblockA") == 4
    for affiliation in ("Institute of Information Technology", "University of Dhaka", "Dhaka, Bangladesh"):
        assert affiliation in first_page, f"Affiliation absent on first page: {affiliation}"
    for author in ("Sumaiya Farhana Islam", "Adnan Bin Wahid", "Redowan Billah Sami", "Md. Touhidur Rahman"):
        assert author in first_page, f"Author absent on first page: {author}"
    for email in ("bsse1450@iit.du.ac.bd", "bsse1442@iit.du.ac.bd", "bsse1409@iit.du.ac.bd", "bsse1432@iit.du.ac.bd"):
        assert email in first_page, f"Email absent on first page: {email}"
    author_boxes = []
    email_boxes = []
    for author, email in zip(
        ("Sumaiya Farhana Islam", "Adnan Bin Wahid", "Redowan Billah Sami", "Md. Touhidur Rahman"),
        ("bsse1450@iit.du.ac.bd", "bsse1442@iit.du.ac.bd", "bsse1409@iit.du.ac.bd", "bsse1432@iit.du.ac.bd"),
    ):
        names = document[0].search_for(author)
        emails = document[0].search_for(email)
        assert len(names) == len(emails) == 1, f"Header text missing or wrapped: {author}"
        assert names[0].y1 < emails[0].y0
        assert abs((names[0].x0 + names[0].x1) - (emails[0].x0 + emails[0].x1)) < 2
        author_boxes.append(names[0])
        email_boxes.append(emails[0])
    assert max(box.y0 for box in author_boxes) - min(box.y0 for box in author_boxes) < 1
    for boxes in (author_boxes, email_boxes):
        assert all(left.x1 < right.x0 for left, right in zip(boxes, boxes[1:])), "Overlapping author columns"
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
        "compiler": "Tectonic 0.17.0 (XeTeX), standard IEEEtran conference class",
        "layout": "IEEE conference, two body columns, four side-by-side author columns",
        "four_author_columns_verified": True,
        "affiliation_verified_on_first_page": True,
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
