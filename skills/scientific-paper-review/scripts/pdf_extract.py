#!/usr/bin/env python3
"""
Smart PDF extraction pipeline for scientific paper review.

Automatically selects the best available extractor, runs quality scoring,
and picks the highest-quality output. Falls back gracefully.

Usage:
    python pdf_extract.py <input.pdf> [--output-dir <dir>]

Extraction chain (tries in order, scores each, picks best):
    1. Marker      — best for multi-column, equations, reading order
    2. MinerU      — best for academic structure, heading hierarchy
    3. pdfplumber  — reliable baseline for simple layouts
    4. If all score poorly → outputs LLM_FALLBACK signal

Always runs PyMuPDF for image/figure metadata regardless of text extractor.
Always runs GROBID for structured reference/metadata extraction if available.

Output:
    - full_text.txt          best extraction result with page markers
    - full_text_meta.json    which extractor won, scores, available methods
    - tables.json            extracted tables as structured data
    - metadata.json          PDF metadata + GROBID metadata if available
    - figures_info.json      image count, dimensions, DPI estimates
    - references_grobid.json structured references from GROBID (if available)
"""

import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")
    sys.stderr.reconfigure(encoding="utf-8")


# ── Availability checks ──────────────────────────────────────────────────────

def check_marker() -> bool:
    """Check if marker is installed."""
    try:
        import marker  # noqa: F401
        return True
    except ImportError:
        pass
    return shutil.which("marker") is not None


def check_mineru() -> bool:
    """Check if MinerU (magic-pdf) is installed."""
    try:
        import magic_pdf  # noqa: F401
        return True
    except ImportError:
        pass
    return shutil.which("magic-pdf") is not None


def check_pdfplumber() -> bool:
    try:
        import pdfplumber  # noqa: F401
        return True
    except ImportError:
        return False


def check_pymupdf() -> bool:
    try:
        import fitz  # noqa: F401
        return True
    except ImportError:
        return False


def check_grobid() -> bool:
    """Check if GROBID is accessible (local or via Docker)."""
    import urllib.request
    try:
        req = urllib.request.Request("http://localhost:8070/api/isalive", method="GET")
        with urllib.request.urlopen(req, timeout=3) as resp:
            return resp.status == 200
    except Exception:
        pass
    return shutil.which("grobid") is not None


# ── Quality scoring ──────────────────────────────────────────────────────────

def score_extraction(text: str, page_count: int) -> dict:
    """Score extraction quality on multiple dimensions. Higher = better."""
    if not text or not text.strip():
        return {"total": 0, "char_count": 0, "details": "empty output"}

    char_count = len(text)
    lines = text.strip().split("\n")
    non_empty_lines = [l for l in lines if l.strip()]

    # Characters per page — scientific paper should have 2000-5000 chars/page
    chars_per_page = char_count / max(page_count, 1)
    density_score = min(chars_per_page / 3000, 1.0) * 30  # max 30 points

    # Structure detection — sections, headings
    heading_patterns = sum(1 for l in non_empty_lines
                          if re.match(r"^#{1,4}\s", l) or  # Markdown headings
                          re.match(r"^\d+\.?\s+[A-Z]", l) or  # Numbered sections
                          re.match(r"^(Abstract|Introduction|Method|Result|Discussion|Conclusion|References)", l, re.I))
    structure_score = min(heading_patterns / 6, 1.0) * 20  # max 20 points

    # Equation detection — LaTeX presence
    latex_count = len(re.findall(r"\$[^$]+\$|\\\[.*?\\\]|\\begin\{equation\}", text))
    equation_score = min(latex_count / 3, 1.0) * 15  # max 15 points

    # Table detection
    table_patterns = len(re.findall(r"\|.*\|.*\||\bTable\s+\d", text))
    table_score = min(table_patterns / 3, 1.0) * 10  # max 10 points

    # Garbled text detection — high ratio of non-ASCII non-Latin = likely broken
    printable = sum(1 for c in text if c.isprintable() or c in "\n\r\t")
    clean_ratio = printable / max(char_count, 1)
    clean_score = clean_ratio * 15  # max 15 points

    # Reading order — detect column-merge artifacts (short lines alternating with long)
    line_lengths = [len(l) for l in non_empty_lines[:50]]
    if line_lengths:
        avg_len = sum(line_lengths) / len(line_lengths)
        variance = sum((l - avg_len) ** 2 for l in line_lengths) / len(line_lengths)
        # High variance in line length suggests broken column merge
        order_score = max(0, 10 - (variance / 1000))  # max 10 points
    else:
        order_score = 0

    total = density_score + structure_score + equation_score + table_score + clean_score + order_score

    return {
        "total": round(total, 1),
        "char_count": char_count,
        "chars_per_page": round(chars_per_page, 0),
        "density": round(density_score, 1),
        "structure": round(structure_score, 1),
        "equations": round(equation_score, 1),
        "tables": round(table_score, 1),
        "cleanliness": round(clean_score, 1),
        "reading_order": round(order_score, 1),
    }


# ── Extractors ───────────────────────────────────────────────────────────────

def extract_marker(pdf_path: str, output_dir: str) -> str | None:
    """Extract using Marker (PDF to Markdown)."""
    try:
        result = subprocess.run(
            ["marker_single", pdf_path, "--output_dir", output_dir],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace",
        )
        # Marker outputs to a subdirectory
        for md_file in Path(output_dir).rglob("*.md"):
            return md_file.read_text(encoding="utf-8", errors="replace")
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"  Marker failed: {e}", file=sys.stderr)
    return None


def extract_mineru(pdf_path: str, output_dir: str) -> str | None:
    """Extract using MinerU (magic-pdf)."""
    try:
        result = subprocess.run(
            ["magic-pdf", "-p", pdf_path, "-o", output_dir, "-m", "auto"],
            capture_output=True, text=True, timeout=300,
            encoding="utf-8", errors="replace",
        )
        # MinerU outputs markdown
        for md_file in Path(output_dir).rglob("*.md"):
            return md_file.read_text(encoding="utf-8", errors="replace")
    except (subprocess.TimeoutExpired, FileNotFoundError, Exception) as e:
        print(f"  MinerU failed: {e}", file=sys.stderr)
    return None


def extract_pdfplumber(pdf_path: str) -> tuple[str, list[dict]]:
    """Extract using pdfplumber (baseline)."""
    import pdfplumber

    pages_text = []
    full_text_parts = []
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            pages_text.append({"page": i, "char_count": len(text)})
            full_text_parts.append(f"\n--- PAGE {i} ---\n{text}")

            # Tables
            for j, table in enumerate(page.extract_tables()):
                if table and len(table) > 1:
                    headers = [str(h).strip() if h else f"col_{k}" for k, h in enumerate(table[0])]
                    rows = []
                    for row in table[1:]:
                        row_dict = {}
                        for k, cell in enumerate(row):
                            key = headers[k] if k < len(headers) else f"col_{k}"
                            row_dict[key] = str(cell).strip() if cell else ""
                        rows.append(row_dict)
                    tables.append({"page": i, "table_index": j + 1, "headers": headers,
                                   "rows": rows, "row_count": len(rows)})

    return "\n".join(full_text_parts), tables


def extract_grobid(pdf_path: str) -> dict | None:
    """Extract structured metadata and references via GROBID."""
    import urllib.request
    try:
        boundary = "----FormBoundary7MA4YWxkTrZu0gW"
        pdf_data = Path(pdf_path).read_bytes()

        body = (
            f"--{boundary}\r\n"
            f'Content-Disposition: form-data; name="input"; filename="{Path(pdf_path).name}"\r\n'
            f"Content-Type: application/pdf\r\n\r\n"
        ).encode() + pdf_data + f"\r\n--{boundary}--\r\n".encode()

        req = urllib.request.Request(
            "http://localhost:8070/api/processFulltextDocument",
            data=body,
            headers={"Content-Type": f"multipart/form-data; boundary={boundary}"},
            method="POST",
        )
        with urllib.request.urlopen(req, timeout=120) as resp:
            tei_xml = resp.read().decode("utf-8")

        # Parse basic info from TEI XML
        refs = re.findall(r"<biblStruct[^>]*>(.*?)</biblStruct>", tei_xml, re.DOTALL)
        title_match = re.search(r"<title[^>]*type=\"main\"[^>]*>(.*?)</title>", tei_xml)
        authors = re.findall(r"<persName>(.*?)</persName>", tei_xml, re.DOTALL)

        return {
            "title": title_match.group(1) if title_match else "",
            "author_count": len(authors),
            "reference_count": len(refs),
            "tei_xml_length": len(tei_xml),
            "source": "GROBID",
        }
    except Exception as e:
        print(f"  GROBID failed: {e}", file=sys.stderr)
        return None


def extract_figures_info(pdf_path: str) -> list[dict]:
    """Extract figure/image metadata using PyMuPDF."""
    try:
        import fitz
    except ImportError:
        return [{"warning": "PyMuPDF not installed. Run: pip install PyMuPDF"}]

    figures = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        for img_idx, img in enumerate(page.get_images(full=True)):
            xref = img[0]
            base_image = doc.extract_image(xref)
            if base_image:
                fig = {
                    "page": page_num + 1,
                    "image_index": img_idx + 1,
                    "width": base_image.get("width", 0),
                    "height": base_image.get("height", 0),
                    "format": base_image.get("ext", "unknown"),
                    "size_bytes": len(base_image.get("image", b"")),
                }
                # DPI estimate
                page_width_pt = page.rect.width
                if page_width_pt > 0 and fig["width"] > 0:
                    fig["estimated_dpi"] = round(fig["width"] / (page_width_pt / 72) * 2)
                figures.append(fig)

    doc.close()
    return figures


# ── Main pipeline ────────────────────────────────────────────────────────────

def main():
    if len(sys.argv) < 2:
        print(f"Usage: {sys.argv[0]} <input.pdf> [--output-dir <dir>]")
        sys.exit(1)

    pdf_path = sys.argv[1]
    output_dir = "."
    if "--output-dir" in sys.argv:
        idx = sys.argv.index("--output-dir")
        if idx + 1 < len(sys.argv):
            output_dir = sys.argv[idx + 1]
            os.makedirs(output_dir, exist_ok=True)

    if not os.path.exists(pdf_path):
        print(json.dumps({"error": f"File not found: {pdf_path}"}))
        sys.exit(1)

    # Detect available tools
    available = {
        "marker": check_marker(),
        "mineru": check_mineru(),
        "pdfplumber": check_pdfplumber(),
        "pymupdf": check_pymupdf(),
        "grobid": check_grobid(),
    }
    print(f"Available extractors: {json.dumps(available)}", file=sys.stderr)

    # Get page count for scoring
    page_count = 1
    if available["pdfplumber"]:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            page_count = len(pdf.pages)
    elif available["pymupdf"]:
        import fitz
        doc = fitz.open(pdf_path)
        page_count = len(doc)
        doc.close()

    # ── Run extractors and score ──────────────────────────────────────────

    candidates = {}

    if available["marker"]:
        print("  Trying Marker...", file=sys.stderr)
        with tempfile.TemporaryDirectory() as tmpdir:
            text = extract_marker(pdf_path, tmpdir)
            if text:
                candidates["marker"] = {"text": text, "score": score_extraction(text, page_count)}
                print(f"  Marker score: {candidates['marker']['score']['total']}", file=sys.stderr)

    if available["mineru"]:
        print("  Trying MinerU...", file=sys.stderr)
        with tempfile.TemporaryDirectory() as tmpdir:
            text = extract_mineru(pdf_path, tmpdir)
            if text:
                candidates["mineru"] = {"text": text, "score": score_extraction(text, page_count)}
                print(f"  MinerU score: {candidates['mineru']['score']['total']}", file=sys.stderr)

    if available["pdfplumber"]:
        print("  Trying pdfplumber...", file=sys.stderr)
        text, tables = extract_pdfplumber(pdf_path)
        if text:
            candidates["pdfplumber"] = {"text": text, "tables": tables,
                                         "score": score_extraction(text, page_count)}
            print(f"  pdfplumber score: {candidates['pdfplumber']['score']['total']}", file=sys.stderr)

    # ── Pick winner ───────────────────────────────────────────────────────

    llm_fallback = False
    winner_name = None
    winner_text = ""
    tables = []

    if candidates:
        winner_name = max(candidates, key=lambda k: candidates[k]["score"]["total"])
        winner_text = candidates[winner_name]["text"]
        tables = candidates[winner_name].get("tables", [])

        # If best score is still very low, signal LLM fallback
        if candidates[winner_name]["score"]["total"] < 25:
            llm_fallback = True
            print(f"  Winner '{winner_name}' scored only {candidates[winner_name]['score']['total']} — LLM fallback recommended", file=sys.stderr)
    else:
        llm_fallback = True
        print("  No extractors produced output — LLM fallback required", file=sys.stderr)

    # ── If no tables from winner, try pdfplumber for tables specifically ──

    if not tables and available["pdfplumber"] and winner_name != "pdfplumber":
        try:
            _, tables = extract_pdfplumber(pdf_path)
        except Exception:
            pass

    # ── Always run PyMuPDF for figures ────────────────────────────────────

    figures = []
    if available["pymupdf"]:
        figures = extract_figures_info(pdf_path)

    # ── Always try GROBID for metadata ────────────────────────────────────

    grobid_data = None
    if available["grobid"]:
        print("  Trying GROBID...", file=sys.stderr)
        grobid_data = extract_grobid(pdf_path)

    # ── Write outputs ─────────────────────────────────────────────────────

    # Full text
    text_path = os.path.join(output_dir, "full_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(winner_text if winner_text else "")

    # Extraction metadata
    scores_summary = {name: cand["score"] for name, cand in candidates.items()}
    meta = {
        "file": os.path.basename(pdf_path),
        "page_count": page_count,
        "available_extractors": available,
        "candidates_tested": list(candidates.keys()),
        "scores": scores_summary,
        "winner": winner_name,
        "llm_fallback_recommended": llm_fallback,
    }
    meta_path = os.path.join(output_dir, "full_text_meta.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(meta, f, indent=2, ensure_ascii=False)

    # Tables
    tables_path = os.path.join(output_dir, "tables.json")
    with open(tables_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, indent=2, ensure_ascii=False)

    # Figures
    figures_path = os.path.join(output_dir, "figures_info.json")
    with open(figures_path, "w", encoding="utf-8") as f:
        json.dump(figures, f, indent=2, ensure_ascii=False)

    # Metadata (basic + GROBID)
    pdf_metadata = {"page_count": page_count}
    if available["pdfplumber"]:
        import pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            info = pdf.metadata or {}
            pdf_metadata.update({
                "title": info.get("Title", ""),
                "author": info.get("Author", ""),
                "creator": info.get("Creator", ""),
            })
    if grobid_data:
        pdf_metadata["grobid"] = grobid_data
    metadata_path = os.path.join(output_dir, "metadata.json")
    with open(metadata_path, "w", encoding="utf-8") as f:
        json.dump(pdf_metadata, f, indent=2, ensure_ascii=False)

    # GROBID references
    if grobid_data:
        refs_path = os.path.join(output_dir, "references_grobid.json")
        with open(refs_path, "w", encoding="utf-8") as f:
            json.dump(grobid_data, f, indent=2, ensure_ascii=False)

    # ── Summary to stdout ─────────────────────────────────────────────────

    summary = {
        "status": "success" if not llm_fallback else "llm_fallback_recommended",
        "winner": winner_name,
        "winner_score": candidates[winner_name]["score"]["total"] if winner_name else 0,
        "all_scores": scores_summary,
        "llm_fallback_recommended": llm_fallback,
        "llm_fallback_reason": (
            "All extractors scored below quality threshold (25/100). "
            "Read the PDF directly using the LLM's native PDF reading capability "
            "for better results." if llm_fallback else None
        ),
        "page_count": page_count,
        "tables_found": len(tables),
        "images_found": len(figures),
        "low_dpi_images": [f for f in figures if f.get("estimated_dpi", 999) < 150],
        "grobid_available": grobid_data is not None,
        "files_created": [text_path, meta_path, tables_path, figures_path, metadata_path],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
