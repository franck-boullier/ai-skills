"""Extract text from a PDF file and print it to stdout or save it to a file.

Tries pdfplumber first (preserves layout and handles complex PDFs better).
Falls back to pypdf if pdfplumber fails or returns empty output.
If both return empty output the PDF is likely scanned; the script exits with
a message directing the user to the OCR workflow.

Dependencies:
    pip install pdfplumber pypdf

Usage:
    python extract_text.py <input_pdf>
    python extract_text.py <input_pdf> <output_txt>
"""

import os
import sys


def _extract_with_pdfplumber(pdf_path):
    """Return extracted text using pdfplumber, or None on failure."""
    try:
        import pdfplumber  # noqa: PLC0415

        with pdfplumber.open(pdf_path) as pdf:
            pages = []
            for page in pdf.pages:
                page_text = page.extract_text() or ""
                pages.append(page_text)
        return "\n\n".join(pages)
    except Exception as exc:
        print(f"Warning: pdfplumber extraction failed ({exc}). Trying pypdf fallback.")
        return None


def _extract_with_pypdf(pdf_path):
    """Return extracted text using pypdf, or None on failure."""
    try:
        from pypdf import PdfReader  # noqa: PLC0415

        reader = PdfReader(pdf_path)
        if reader.is_encrypted:
            print("Error: PDF is password-protected. Decrypt it first with reader.decrypt('password').")
            sys.exit(1)
        pages = [page.extract_text() or "" for page in reader.pages]
        return "\n\n".join(pages)
    except Exception as exc:
        print(f"Error: pypdf extraction failed: {exc}")
        return None


def extract(pdf_path, output_path=None):
    """Extract text from *pdf_path* and write to *output_path* or stdout.

    Args:
        pdf_path:    Path to the source PDF file.
        output_path: Optional path for the output .txt file. If None, the
                     extracted text is printed to stdout.
    """
    if not os.path.isfile(pdf_path):
        print(f"Error: input file not found: {pdf_path}")
        sys.exit(1)

    text = _extract_with_pdfplumber(pdf_path)

    if text is None:
        text = _extract_with_pypdf(pdf_path)

    if text is None:
        print("Error: all extraction methods failed. The PDF may be corrupted.")
        sys.exit(1)

    if not text.strip():
        print(
            "Warning: no text extracted. The PDF may be image-based (scanned).\n"
            "Use the OCR workflow: python scripts/convert_pdf_to_images.py then pytesseract."
        )

    if output_path:
        try:
            with open(output_path, "w", encoding="utf-8") as f:
                f.write(text)
            print(f"Text saved to: {output_path}")
        except OSError as exc:
            print(f"Error: cannot write output file '{output_path}': {exc}")
            sys.exit(1)
    else:
        print(text)


if __name__ == "__main__":
    if len(sys.argv) not in (2, 3):
        print("Usage: extract_text.py <input_pdf> [output_txt]")
        sys.exit(1)

    input_pdf = sys.argv[1]
    output_txt = sys.argv[2] if len(sys.argv) == 3 else None
    extract(input_pdf, output_txt)
