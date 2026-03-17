---
name: read-pdf-document
description: Use this skill whenever the user wants to read or extract content from a PDF file. This includes extracting text, tables, metadata, or images from an existing PDF, and performing OCR on scanned PDFs to make their content readable. Can be invoked as a sub-skill by any skill that needs to process PDF documents. Do NOT use this skill for creating, modifying, merging, splitting, rotating, watermarking, encrypting, or filling PDF files.
license: Mixed open-source licenses. pypdf — BSD. pdfplumber — MIT. pypdfium2 — Apache/BSD. pdf2image — MIT. pytesseract — Apache-2.0. poppler-utils — GPL-2. qpdf — Apache-2.0. See references/ files for per-library details.
compatibility: Requires Python 3.8+. Python packages pypdf, pdfplumber, pdf2image. System packages poppler-utils (pdftotext, pdfimages, pdftoppm). Optional pytesseract and tesseract-ocr for OCR. Optional pypdfium2 for advanced rendering and fast text extraction.
---

# PDF Reading & Extraction Guide

## Overview

This guide covers reading and extracting content from existing PDF files using Python libraries and command-line tools.

## Prerequisites

Install the Python packages:

```bash
pip install pypdf pdfplumber pdf2image
```

For OCR support, also install:

```bash
pip install pytesseract
```

Install the required system packages:

- **Linux (Debian/Ubuntu):** `sudo apt-get install poppler-utils tesseract-ocr`
- **macOS:** `brew install poppler tesseract`
- **Windows:** Download poppler from [poppler releases](https://github.com/oschwartz10612/poppler-windows/releases) and add to PATH. Download Tesseract from [UB Mannheim](https://github.com/UB-Mannheim/tesseract/wiki).

For advanced rendering and fast text extraction (optional), also install:

```bash
pip install pypdfium2
```

## Quick Start

```python
from pypdf import PdfReader

# Read a PDF
reader = PdfReader("document.pdf")
print(f"Pages: {len(reader.pages)}")

# Extract text
text = ""
for page in reader.pages:
    text += page.extract_text()
```

## Python Libraries

### pypdf - Text and Metadata Extraction

#### Extract Text

```python
from pypdf import PdfReader

reader = PdfReader("document.pdf")
text = ""
for page in reader.pages:
    text += page.extract_text()
print(text)
```

#### Extract Metadata

```python
reader = PdfReader("document.pdf")
meta = reader.metadata
print(f"Title: {meta.title}")
print(f"Author: {meta.author}")
print(f"Subject: {meta.subject}")
print(f"Creator: {meta.creator}")
```

### pdfplumber - Text and Table Extraction

#### Extract Text with Layout

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    for page in pdf.pages:
        text = page.extract_text()
        print(text)
```

#### Extract Tables

```python
with pdfplumber.open("document.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        tables = page.extract_tables()
        for j, table in enumerate(tables):
            print(f"Table {j+1} on page {i+1}:")
            for row in table:
                print(row)
```

For advanced table extraction with custom settings, pandas export, and layout debugging, see [references/advanced-python.md](references/advanced-python.md).

## Command-Line Tools

### pdftotext (poppler-utils)

```bash
# Extract text
pdftotext input.pdf output.txt

# Extract text preserving layout
pdftotext -layout input.pdf output.txt

# Extract specific pages
pdftotext -f 1 -l 5 input.pdf output.txt  # Pages 1-5
```

## Common Tasks

### Extract Text from Scanned PDFs (OCR)

Use the provided script to convert PDF pages to images first:

```bash
python scripts/convert_pdf_to_images.py input.pdf output_dir/
```

Then run OCR on the resulting images:

```python
# Requires: pip install pytesseract pdf2image
import pytesseract
from pdf2image import convert_from_path

# Convert PDF to images
images = convert_from_path('scanned.pdf')

# OCR each page
text = ""
for i, image in enumerate(images):
    text += f"Page {i+1}:\n"
    text += pytesseract.image_to_string(image)
    text += "\n\n"

print(text)
```

### Extract Images

```bash
# Using pdfimages (poppler-utils)
pdfimages -j input.pdf output_prefix

# This extracts all images as output_prefix-000.jpg, output_prefix-001.jpg, etc.
```

## Choosing the Right Tool

Use this decision guide to pick the best approach for your task:

1. **Simple text extraction** (no tables, no layout matters) → use **pypdf**. It is lightweight and has no system dependencies.
2. **Text with layout or tables** → use **pdfplumber**. It preserves spatial structure and has the best table extraction.
3. **Scanned PDF or image-based PDF** → use **pytesseract** + **pdf2image**. Convert pages to images first, then run OCR.
4. **Metadata only** (title, author, creator) → use **pypdf**. Fastest path to document properties.
5. **Extract embedded images** → use **pdfimages** (CLI). Much faster than rendering pages.
6. **Batch processing or scripting** → use **pdftotext** (CLI). Ideal for shell pipelines and automation.

## Quick Reference

| Task               | Best Tool   | Command/Code                             |
|--------------------|-------------|------------------------------------------|
| Extract text       | pdfplumber  | `page.extract_text()`                    |
| Extract tables     | pdfplumber  | `page.extract_tables()`                  |
| Extract metadata   | pypdf       | `reader.metadata`                        |
| Extract text (CLI) | pdftotext   | `pdftotext -layout input.pdf output.txt` |
| OCR scanned PDFs   | pytesseract | Convert to image first                   |
| Extract images     | pdfimages   | `pdfimages -j input.pdf prefix`          |

## Example Outputs

These examples show what the extracted data actually looks like so you can validate your results.

### Text extraction output

Given a one-page PDF containing a short article, `page.extract_text()` returns a plain string:

```text
Annual Report 2024

Revenue grew by 12% year-on-year, reaching $4.2 billion.
Operating costs remained stable at $2.8 billion.
Net profit: $1.4 billion (+18% vs 2023).
```

### Table extraction output

Given a PDF page with a two-column table, `page.extract_tables()` returns a list of tables. Each table is a list of rows; each row is a list of cell strings:

```python
[
  [                                    # table 0
    ["Product",   "Units Sold"],       # header row
    ["Widget A",  "1,200"],
    ["Widget B",  "850"],
    ["Widget C",  "3,400"],
  ]
]
```

### Metadata extraction output

`reader.metadata` returns a dict-like object. Accessing its properties yields:

```python
{
  "title":   "Annual Report 2024",
  "author":  "Finance Team",
  "subject": "Corporate financials",
  "creator": "Microsoft Word",
}
```

## Edge Cases

- **Password-protected PDFs:** Use `reader.decrypt("password")` from pypdf before extracting content. See [references/troubleshooting.md](references/troubleshooting.md) for details.
- **Scanned PDFs with no extractable text:** If `page.extract_text()` returns empty or garbled output, the PDF is likely image-based. Fall back to OCR (see the "Extract Text from Scanned PDFs" section above).
- **Corrupted PDFs:** Use `qpdf --check file.pdf` to diagnose and `qpdf --replace-input file.pdf` to attempt repair. See [references/troubleshooting.md](references/troubleshooting.md).

## Output Format

When this skill is used as a **sub-skill** by another skill, return extracted
content as follows:

- **Text extraction** → return a Python `str` containing the full text. Do not
  write to a file unless the caller explicitly requests it.
- **Table extraction** → return a `list` of tables, where each table is a
  `list` of rows and each row is a `list` of cell strings.
- **Metadata extraction** → return a `dict` with keys such as `title`,
  `author`, `subject`, `creator`.
- **Image extraction** → save images to a directory supplied by the caller and
  return the list of output file paths.

When used **interactively** (user asks directly), display the result in the
conversation unless the user asks to save to a file.

## Next Steps

- For advanced Python techniques (pypdfium2, pdfplumber coordinates, batch processing), see [references/advanced-python.md](references/advanced-python.md)
- For advanced CLI operations (poppler-utils, image conversion), see [references/cli-reference.md](references/cli-reference.md)
- For troubleshooting (encrypted PDFs, corrupted files, OCR fallback), see [references/troubleshooting.md](references/troubleshooting.md)
- To extract text from a PDF (with pdfplumber/pypdf fallback), run [scripts/extract_text.py](scripts/extract_text.py)
- To convert PDF pages to images (e.g. for OCR), run [scripts/convert_pdf_to_images.py](scripts/convert_pdf_to_images.py)
