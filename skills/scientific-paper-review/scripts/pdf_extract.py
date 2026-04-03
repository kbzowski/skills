#!/usr/bin/env python3
"""
PDF text and table extraction for scientific paper review.

Usage:
    python pdf_extract.py <input.pdf> [--output-dir <dir>]

Output:
    - full_text.txt: complete text extraction with page markers
    - tables.json: extracted tables as structured data
    - metadata.json: PDF metadata (title, authors, page count, etc.)
    - figures_info.json: figure/image metadata (count, dimensions, DPI)

Dependencies: pip install pdfplumber PyMuPDF Pillow
"""

import json
import os
import sys
from pathlib import Path

try:
    import pdfplumber
except ImportError:
    print(json.dumps({"error": "pdfplumber not installed. Run: pip install pdfplumber"}))
    sys.exit(1)

try:
    import fitz  # PyMuPDF
except ImportError:
    fitz = None


def extract_text(pdf_path: str) -> tuple[str, list[dict]]:
    """Extract text from PDF with page markers."""
    pages_text = []
    full_text_parts = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            text = page.extract_text() or ""
            pages_text.append({"page": i, "char_count": len(text)})
            full_text_parts.append(f"\n--- PAGE {i} ---\n{text}")

    return "\n".join(full_text_parts), pages_text


def extract_tables(pdf_path: str) -> list[dict]:
    """Extract tables from PDF as structured data."""
    tables = []

    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages, 1):
            page_tables = page.extract_tables()
            for j, table in enumerate(page_tables):
                if table and len(table) > 1:
                    # First row as headers
                    headers = [str(h).strip() if h else f"col_{k}" for k, h in enumerate(table[0])]
                    rows = []
                    for row in table[1:]:
                        row_dict = {}
                        for k, cell in enumerate(row):
                            key = headers[k] if k < len(headers) else f"col_{k}"
                            row_dict[key] = str(cell).strip() if cell else ""
                        rows.append(row_dict)

                    tables.append({
                        "page": i,
                        "table_index": j + 1,
                        "headers": headers,
                        "rows": rows,
                        "row_count": len(rows),
                    })

    return tables


def extract_metadata(pdf_path: str) -> dict:
    """Extract PDF metadata."""
    metadata = {"file": os.path.basename(pdf_path)}

    with pdfplumber.open(pdf_path) as pdf:
        metadata["page_count"] = len(pdf.pages)
        info = pdf.metadata or {}
        metadata["title"] = info.get("Title", "")
        metadata["author"] = info.get("Author", "")
        metadata["creator"] = info.get("Creator", "")
        metadata["producer"] = info.get("Producer", "")
        metadata["creation_date"] = info.get("CreationDate", "")

    return metadata


def extract_figures_info(pdf_path: str) -> list[dict]:
    """Extract figure/image metadata using PyMuPDF."""
    if fitz is None:
        return [{"warning": "PyMuPDF not installed. Run: pip install PyMuPDF"}]

    figures = []
    doc = fitz.open(pdf_path)

    for page_num in range(len(doc)):
        page = doc[page_num]
        images = page.get_images(full=True)

        for img_idx, img in enumerate(images):
            xref = img[0]
            base_image = doc.extract_image(xref)

            if base_image:
                figures.append({
                    "page": page_num + 1,
                    "image_index": img_idx + 1,
                    "width": base_image.get("width", 0),
                    "height": base_image.get("height", 0),
                    "colorspace": base_image.get("colorspace", 0),
                    "bpc": base_image.get("bpc", 0),  # bits per component
                    "size_bytes": len(base_image.get("image", b"")),
                    "format": base_image.get("ext", "unknown"),
                })

    doc.close()

    # Calculate DPI estimates (approximate based on page dimensions)
    if figures and fitz is not None:
        doc = fitz.open(pdf_path)
        for fig in figures:
            page = doc[fig["page"] - 1]
            page_width_pt = page.rect.width  # points (1 inch = 72 points)
            if page_width_pt > 0 and fig["width"] > 0:
                # Rough DPI estimate assuming image spans ~50% of page width
                fig["estimated_dpi"] = round(fig["width"] / (page_width_pt / 72) * 2)
        doc.close()

    return figures


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

    # Extract everything
    print(f"Extracting from: {pdf_path}", file=sys.stderr)

    full_text, pages_info = extract_text(pdf_path)
    text_path = os.path.join(output_dir, "full_text.txt")
    with open(text_path, "w", encoding="utf-8") as f:
        f.write(full_text)
    print(f"  Text: {text_path} ({sum(p['char_count'] for p in pages_info)} chars)", file=sys.stderr)

    tables = extract_tables(pdf_path)
    tables_path = os.path.join(output_dir, "tables.json")
    with open(tables_path, "w", encoding="utf-8") as f:
        json.dump(tables, f, indent=2, ensure_ascii=False)
    print(f"  Tables: {tables_path} ({len(tables)} tables found)", file=sys.stderr)

    metadata = extract_metadata(pdf_path)
    metadata["pages"] = pages_info
    meta_path = os.path.join(output_dir, "metadata.json")
    with open(meta_path, "w", encoding="utf-8") as f:
        json.dump(metadata, f, indent=2, ensure_ascii=False)
    print(f"  Metadata: {meta_path}", file=sys.stderr)

    figures = extract_figures_info(pdf_path)
    figures_path = os.path.join(output_dir, "figures_info.json")
    with open(figures_path, "w", encoding="utf-8") as f:
        json.dump(figures, f, indent=2, ensure_ascii=False)
    print(f"  Figures: {figures_path} ({len(figures)} images found)", file=sys.stderr)

    # Summary to stdout
    summary = {
        "status": "success",
        "files_created": [text_path, tables_path, meta_path, figures_path],
        "page_count": metadata["page_count"],
        "total_chars": sum(p["char_count"] for p in pages_info),
        "tables_found": len(tables),
        "images_found": len(figures),
        "low_dpi_images": [
            f for f in figures
            if f.get("estimated_dpi", 999) < 150
        ],
    }
    print(json.dumps(summary, indent=2, ensure_ascii=False))


if __name__ == "__main__":
    main()
