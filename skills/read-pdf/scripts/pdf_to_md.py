# /// script
# requires-python = ">=3.12,<4.0"
# dependencies = ["docling[easyocr]>=2.121.0", "torch", "torchvision"]
#
# [[tool.uv.index]]
# name = "pytorch-cuda"
# url = "https://download.pytorch.org/whl/cu130"
# explicit = true
#
# [tool.uv.sources]
# torch = { index = "pytorch-cuda" }
# torchvision = { index = "pytorch-cuda" }
# ///
"""PDF -> agent-readable Markdown via docling, with EasyOCR on the GPU.

Run with:  uv run --script pdf_to_md.py INPUT.pdf [options]
First run downloads torch(cu130) + docling/easyocr models -- several GB, minutes.
"""

import argparse
import logging
import sys
import time
from pathlib import Path


def parse_pages(spec: str) -> tuple[int, int]:
    lo, _, hi = spec.partition("-")
    lo, hi = int(lo), int(hi or lo)
    if hi < lo:
        raise argparse.ArgumentTypeError(f"reversed page range: {spec}")
    return (lo, hi)


def pick_out(pdf: Path, out: Path | None, images: bool) -> Path:
    """Where the Markdown lands. With images the run produces many files, so it gets
    its own directory; without them a single .md next to the source is less clutter."""
    if out and out.suffix.lower() == ".md":
        return out
    if out:
        return out / f"{pdf.stem}.md"
    return (pdf.with_suffix("") / f"{pdf.stem}.md") if images else pdf.with_suffix(".md")


def self_test() -> int:
    assert parse_pages("5") == (5, 5)
    assert parse_pages("3-7") == (3, 7)
    try:
        parse_pages("7-3")
        raise AssertionError("reversed range should be rejected")
    except argparse.ArgumentTypeError:
        pass
    p = Path("/docs/a.pdf")
    assert pick_out(p, None, False) == Path("/docs/a.md")
    assert pick_out(p, None, True) == Path("/docs/a/a.md")
    assert pick_out(p, Path("/out/b.md"), True) == Path("/out/b.md")
    assert pick_out(p, Path("/out"), True) == Path("/out/a.md")
    print("self-test ok")
    return 0


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("pdf", type=Path, nargs="?")
    p.add_argument("-o", "--out", type=Path, help="output .md, or a directory (default: <pdf stem>.md next to input)")
    p.add_argument("--images", action="store_true", help="extract figures as PNG; output then goes into its own directory")
    p.add_argument("--page-images", action="store_true", help="also render every full page as PNG (implies --images)")
    p.add_argument("--image-scale", type=float, default=2.0, help="rendered image resolution, 1.0 ~ 72 DPI (default 2.0)")
    p.add_argument("--lang", nargs="+", default=["pl", "en"], help="EasyOCR languages (default: pl en)")
    ocr = p.add_mutually_exclusive_group()
    ocr.add_argument("--full-ocr", action="store_true", help="OCR every page -- for scanned/photographed PDFs")
    ocr.add_argument("--no-ocr", action="store_true", help="digital-born PDF with a good text layer; much faster")
    p.add_argument("--pages", type=parse_pages, help="page range, e.g. 3-7 or 5")
    p.add_argument("--device", default="cuda", choices=["cuda", "cpu", "auto"])
    p.add_argument("--threads", type=int, default=8, help="docling worker threads (default 8); matters on --device cpu")
    p.add_argument("--self-test", action="store_true", help="check the argument/output-path logic and exit")
    args = p.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
    log = logging.getLogger("pdf_to_md")

    if args.self_test:
        return self_test()
    if args.pdf is None:
        p.error("the PDF argument is required")
    if not args.pdf.is_file():
        log.error("no such file: %s", args.pdf)
        return 2
    args.images = args.images or args.page_images

    from docling.datamodel.accelerator_options import AcceleratorDevice, AcceleratorOptions
    from docling.datamodel.base_models import ConversionStatus, InputFormat
    from docling.datamodel.pipeline_options import (
        EasyOcrOptions,
        OcrMode,
        PdfPipelineOptions,
        TableStructureOptions,
    )
    from docling.datamodel.settings import DEFAULT_PAGE_RANGE
    from docling.document_converter import DocumentConverter, PdfFormatOption
    from docling_core.types.doc import ImageRefMode

    # The point of this skill is GPU OCR: silently falling back to CPU turns a
    # 1-minute job into a 30-minute one, so say so instead of hiding it.
    import torch

    cuda = torch.cuda.is_available()
    if args.device == "cuda" and not cuda:
        log.error(
            "CUDA not available (torch %s). The CPU torch wheel got installed -- check that "
            "the [tool.uv.index] block at the top of this script matches your driver's CUDA "
            "version, and that this file has LF line endings (uv silently ignores the "
            "[tool.uv] block otherwise). Re-run with --device cpu to accept the slow path.",
            torch.__version__,
        )
        return 3
    device = {"cuda": AcceleratorDevice.CUDA, "cpu": AcceleratorDevice.CPU, "auto": AcceleratorDevice.AUTO}[args.device]

    opts = PdfPipelineOptions()
    opts.do_ocr = not args.no_ocr
    opts.do_table_structure = True
    opts.table_structure_options = TableStructureOptions(do_cell_matching=True)
    # use_gpu left as None on purpose: docling then derives it from accelerator_options.
    opts.ocr_options = EasyOcrOptions(
        lang=args.lang,
        mode=OcrMode.FULL_PAGE if args.full_ocr else OcrMode.PDF_AWARE_LAYOUT_REGIONS,
    )
    opts.accelerator_options = AcceleratorOptions(num_threads=args.threads, device=device)
    opts.images_scale = args.image_scale
    opts.generate_picture_images = args.images
    opts.generate_page_images = args.page_images

    log.info("device=%s ocr=%s mode=%s lang=%s images=%s",
             args.device, opts.do_ocr, opts.ocr_options.mode, args.lang, args.images)
    if args.device != "cpu" and cuda:
        log.info("gpu=%s", torch.cuda.get_device_name(0))

    conv = DocumentConverter(format_options={InputFormat.PDF: PdfFormatOption(pipeline_options=opts)})
    t0 = time.time()
    try:
        res = conv.convert(args.pdf, page_range=args.pages or DEFAULT_PAGE_RANGE)
    except Exception as e:  # encrypted, corrupt, or unsupported -- not a bug in this script
        log.error("conversion failed (encrypted or corrupt PDF?): %s", e)
        return 4
    if res.status == ConversionStatus.FAILURE:
        # Exit non-zero so a shell batch loop can tell this apart from a good run.
        log.error("conversion failed: %s", res.status)
        return 4
    if res.status != ConversionStatus.SUCCESS:
        log.warning("conversion status: %s -- some pages may be missing from the output", res.status)

    stem = args.pdf.stem
    out = pick_out(args.pdf, args.out, args.images)
    out.parent.mkdir(parents=True, exist_ok=True)

    # REFERENCED (never EMBEDDED): base64 blobs make the .md unreadable for the agent
    # that is supposed to consume it. A relative artifacts_dir keeps the links portable.
    res.document.save_as_markdown(
        out,
        artifacts_dir=Path(f"{stem}_artifacts") if args.images else None,
        image_mode=ImageRefMode.REFERENCED if args.images else ImageRefMode.PLACEHOLDER,
    )

    art = out.parent / f"{stem}_artifacts"
    n_pic = n_page = 0
    if args.images:
        art.mkdir(exist_ok=True)
        # Tables are not dumped as crops on purpose: they already survive as real
        # Markdown tables, and cropping them would force full-page rendering.
        if args.page_images:
            for page in res.document.pages.values():
                if page.image is None:
                    continue
                n_page += 1
                page.image.pil_image.save(art / f"page_{page.page_no:03d}.png", "PNG")
        # Count what actually landed on disk, not what the model claims: a picture
        # without a rendered image would otherwise inflate the number reported back.
        # Page renders are excluded by name, so leftovers from an earlier run don't count.
        n_pic = sum(1 for f in art.glob("*.png") if not f.name.startswith("page_"))

    text = out.read_text(encoding="utf-8")
    if args.images and "\\" in text:
        # docling writes the relative artifacts path with the OS separator; backslashes
        # break the links in every Markdown renderer, so normalise them.
        text = text.replace(stem + "_artifacts\\", stem + "_artifacts/")
        out.write_text(text, encoding="utf-8")

    log.info("wrote %s (%d chars, %d pages) in %.1fs",
             out, len(text), len(res.document.pages), time.time() - t0)
    if args.images:
        log.info("artifacts: %d figures, %d page images in %s", n_pic, n_page, art)
    if len(text.strip()) < 50:
        log.warning("output is nearly empty -- scanned PDF? retry with --full-ocr")
    return 0


if __name__ == "__main__":
    sys.exit(main())
