#!/usr/bin/env python3
"""Apply the controlled NĐ 30 formatting fix to the CVNK DOCX template.

This deliberately patches only ``word/document.xml`` as text.  The offline
HTML generator slices that OOXML directly, so opening and saving the vendor
template in Word is unsafe: Word would rewrite much more of the package.
"""

from __future__ import annotations

import argparse
import os
import re
import tempfile
from pathlib import Path
from zipfile import ZIP_DEFLATED, ZipFile


EXPECTED_LETTERS = 9

PARAGRAPH_RE = re.compile(r"<w:p\b[^>]*>.*?</w:p>", re.DOTALL)
TEXT_RE = re.compile(r"<w:t(?:\s+[^>]*)?>(.*?)</w:t>", re.DOTALL)
RUN_RE = re.compile(r"<w:r(?:\s+[^>]*)?>.*?</w:r>", re.DOTALL)
PBORDER_RE = re.compile(r"<w:pBdr>.*?</w:pBdr>", re.DOTALL)
INDENT_RE = re.compile(r"<w:ind\b[^>]*/>")
SPACING_RE = re.compile(r"<w:spacing\b[^>]*/>")
SINGLE_BOTTOM_RE = re.compile(r'<w:bottom\b[^>]*\bw:val="single"[^>]*/>')


# (needle in text, left/right indent in twips, border-to-content space in points).
# The issuing-unit rule is 1/3–1/2 of the issuing-unit line.  The motto rule
# matches the text width.  The notice's trích yếu rule is just under 1/2 of
# its text, as required for a document that bears a type name (THÔNG BÁO).
RULE_TARGETS = (
    ("KHU CÔNG NGHIỆP HẢI PHÒNG", 1375, 2),
    ("Độc lập - Tự do - Hạnh phúc", 1268, 2),
    ("V/v làm thủ tục xuất khẩu, nhập khẩu tại chỗ", 3350, 2),
)

# NĐ 30 specifies single spacing for these header lines.  The vendor template
# used 1.5-line spacing (w:line="360"), whose lower leading made the following
# border look detached even when the rule paragraph itself was only one point.
SINGLE_LINE_TARGETS = (
    "KHU CÔNG NGHIỆP HẢI PHÒNG",
    "Độc lập - Tự do - Hạnh phúc",
)


def paragraph_text(paragraph: str) -> str:
    return "".join(TEXT_RE.findall(paragraph))


def rule_xml(indent: int, space: int) -> str:
    return (
        "<w:pBdr>"
        '<w:top w:space="0" w:sz="0" w:val="nil"/>'
        '<w:left w:space="0" w:sz="0" w:val="nil"/>'
        f'<w:bottom w:space="{space}" w:sz="6" w:val="single" w:color="000000"/>'
        '<w:right w:space="0" w:sz="0" w:val="nil"/>'
        '<w:between w:space="0" w:sz="0" w:val="nil"/>'
        "</w:pBdr>"
    )


def patch_text_line_spacing(xml: str, needle: str) -> str:
    """Set the matching text paragraph to single line spacing (240 twips)."""
    replacements: list[tuple[int, int, str]] = []
    for paragraph_match in PARAGRAPH_RE.finditer(xml):
        paragraph = paragraph_match.group(0)
        if needle not in paragraph_text(paragraph):
            continue
        patched, spacing_count = SPACING_RE.subn(
            '<w:spacing w:after="0" w:before="0" w:line="240" w:lineRule="auto"/>',
            paragraph,
            count=1,
        )
        if spacing_count != 1:
            raise RuntimeError(f"Could not find exactly one spacing element for {needle!r}.")
        replacements.append((paragraph_match.start(), paragraph_match.end(), patched))

    if len(replacements) != EXPECTED_LETTERS:
        raise RuntimeError(
            f"Expected {EXPECTED_LETTERS} text paragraphs for {needle!r}, "
            f"found {len(replacements)}. Refusing to patch an unexpected template."
        )

    result = xml
    for start, end, replacement in reversed(replacements):
        result = f"{result[:start]}{replacement}{result[end:]}"
    return result


BLANK_RULE_RUN = (
    '<w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/>'
    '<w:sz w:val="2"/><w:szCs w:val="2"/></w:rPr>'
    '<w:t xml:space="preserve"> </w:t></w:r>'
)


def patch_rule_after_paragraph(xml: str, needle: str, indent: int, *, space: int) -> str:
    """Patch the one-point blank rule immediately after each matching text paragraph.

    A paragraph indentation limits both its text and its border.  Keeping the
    rule in its own otherwise blank paragraph preserves the text's available
    width (so neither the issuing unit nor trích yếu wraps).  The one-point
    preserved space makes the paragraph non-empty and keeps the rule stable
    in Word.  LibreOffice can still omit a valid paragraph border in this
    non-final right-header-cell position; do not add nested tables merely to
    work around that renderer quirk, because the offline generator deliberately
    requires exactly two tables per letter.
    """
    paragraphs = list(PARAGRAPH_RE.finditer(xml))
    replacements: list[tuple[int, int, str]] = []

    for index, paragraph_match in enumerate(paragraphs[:-1]):
        if needle not in paragraph_text(paragraph_match.group(0)):
            continue
        rule_match = paragraphs[index + 1]
        rule_paragraph = rule_match.group(0)
        # Accept either the untouched empty paragraph or a paragraph previously
        # normalized by this script.  Any non-whitespace content is unexpected.
        if paragraph_text(rule_paragraph).strip() or not SINGLE_BOTTOM_RE.search(rule_paragraph):
            raise RuntimeError(
                f"Expected a blank rule paragraph immediately after {needle!r}."
            )
        patched, border_count = PBORDER_RE.subn(
            rule_xml(indent, space), rule_paragraph, count=1
        )
        if border_count != 1:
            raise RuntimeError(f"Could not find exactly one paragraph border for {needle!r}.")
        patched, indent_count = INDENT_RE.subn(
            f'<w:ind w:left="{indent}" w:right="{indent}" w:firstLine="0"/>',
            patched,
            count=1,
        )
        if indent_count != 1:
            raise RuntimeError(f"Could not find exactly one indentation element for {needle!r}.")
        patched = RUN_RE.sub("", patched)
        patched = patched.replace("</w:pPr>", f"</w:pPr>{BLANK_RULE_RUN}", 1)
        replacements.append((rule_match.start(), rule_match.end(), patched))

    if len(replacements) != EXPECTED_LETTERS:
        raise RuntimeError(
            f"Expected {EXPECTED_LETTERS} rules after {needle!r}, found {len(replacements)}. "
            "Refusing to patch a template with an unexpected structure."
        )

    result = xml
    for start, end, replacement in reversed(replacements):
        result = f"{result[:start]}{replacement}{result[end:]}"
    return result


def patch_document_xml(xml: str) -> str:
    result = xml
    for needle in SINGLE_LINE_TARGETS:
        result = patch_text_line_spacing(result, needle)
    for needle, indent, space in RULE_TARGETS:
        result = patch_rule_after_paragraph(result, needle, indent, space=space)
    return result


def patch_docx(source_path: Path, output_path: Path) -> None:
    with ZipFile(source_path) as source:
        entries = [(info, source.read(info.filename)) for info in source.infolist()]

    document_entries = [data for info, data in entries if info.filename == "word/document.xml"]
    if len(document_entries) != 1:
        raise RuntimeError("DOCX must contain exactly one word/document.xml entry.")
    patched_document = patch_document_xml(document_entries[0].decode("utf-8")).encode("utf-8")

    output_path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary_name = tempfile.mkstemp(
        prefix=f".{output_path.name}.", suffix=".tmp", dir=output_path.parent
    )
    os.close(fd)
    temporary_path = Path(temporary_name)
    try:
        with ZipFile(temporary_path, "w", compression=ZIP_DEFLATED) as destination:
            for info, data in entries:
                destination.writestr(
                    info,
                    patched_document if info.filename == "word/document.xml" else data,
                )
        os.replace(temporary_path, output_path)
    finally:
        if temporary_path.exists():
            temporary_path.unlink()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("source", type=Path)
    parser.add_argument("output", type=Path)
    args = parser.parse_args()
    patch_docx(args.source, args.output)


if __name__ == "__main__":
    main()
