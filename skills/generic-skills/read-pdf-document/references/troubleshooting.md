# Troubleshooting Common Issues

## Encrypted PDFs

```python
from pypdf import PdfReader

try:
    reader = PdfReader("encrypted.pdf")
    if reader.is_encrypted:
        reader.decrypt("password")
except Exception as e:
    print(f"Failed to decrypt: {e}")
```

## Corrupted PDFs

```bash
# Use qpdf to check and repair
qpdf --check corrupted.pdf
qpdf --replace-input corrupted.pdf
```

## Text Extraction Returns Empty or Garbled Output

This usually means the PDF is image-based (scanned). Fall back to OCR:

```python
import pytesseract
from pdf2image import convert_from_path

def extract_text_with_ocr(pdf_path):
    images = convert_from_path(pdf_path)
    text = ""
    for i, image in enumerate(images):
        text += pytesseract.image_to_string(image)
    return text
```

## Garbled Characters Despite Text Being Present

The PDF may have embedded fonts without unicode mappings. Diagnose with `pdffonts`:

```bash
pdffonts document.pdf
```

Look at the `uni` column in the output. If it shows `no`, the font lacks unicode mappings and text extraction will produce garbled results. In this case, treat the PDF as if it were scanned and fall back to OCR even though the PDF contains vector text.

```bash
# Example output indicating a problematic font
name                             type              encoding         emb sub uni
-------------------------------- ----------------- ---------------- --- --- ---
ABCDEF+SomeFont                  Type 1C           Builtin          yes yes no
```

## pdf2image Fails Silently or Raises an Error

`pdf2image` relies on `pdftoppm` from poppler-utils internally. If poppler is not
installed or not on your PATH, the error message may be unhelpful. Verify that
poppler is available:

```bash
pdftoppm -v
```

If that command is not found, install poppler:

- **Linux:** `sudo apt-get install poppler-utils`
- **macOS:** `brew install poppler`
- **Windows:** Download from [poppler-windows releases](https://github.com/oschwartz10612/poppler-windows/releases), extract the archive, and add the `Library/bin` folder to your system PATH. Then restart your terminal.

## Windows: poppler Not Found After Installation

On Windows, adding a directory to PATH via the GUI requires reopening your terminal (or IDE) before the change takes effect. If `pdftoppm -v` still fails after updating PATH, you can pass the path directly to `convert_from_path`:

```python
from pdf2image import convert_from_path

images = convert_from_path(
    "document.pdf",
    poppler_path=r"C:\path\to\poppler\Library\bin"
)
```

## OCR Quality Is Poor

Poor OCR output is usually caused by low image resolution or missing language packs.

**Increase DPI when converting to images:**

```python
from pdf2image import convert_from_path
import pytesseract

# Use 300 DPI for good quality; 600 DPI for small or dense text
images = convert_from_path("scanned.pdf", dpi=300)
text = "".join(pytesseract.image_to_string(img) for img in images)
```

**Specify the correct language pack:**

```python
# Use a specific language (e.g. French)
text = pytesseract.image_to_string(image, lang="fra")

# Use multiple languages
text = pytesseract.image_to_string(image, lang="eng+fra")
```

Install additional Tesseract language packs:

```bash
# Linux
sudo apt-get install tesseract-ocr-fra

# macOS
brew install tesseract-lang
```

**Pre-process images for better accuracy** (convert to greyscale, increase contrast):

```python
from PIL import Image, ImageFilter, ImageEnhance

def preprocess(image):
    image = image.convert("L")                          # greyscale
    image = ImageEnhance.Contrast(image).enhance(2.0)  # boost contrast
    return image

text = pytesseract.image_to_string(preprocess(image))
```

## pdfplumber Hangs or Is Very Slow on Large PDFs

pdfplumber loads all page objects into memory. For large documents, process pages
individually and add a timeout guard:

```python
import pdfplumber

with pdfplumber.open("large.pdf") as pdf:
    for i, page in enumerate(pdf.pages):
        try:
            text = page.extract_text() or ""
            print(f"Page {i + 1}: {len(text)} chars")
        except Exception as e:
            print(f"Page {i + 1} failed: {e}")
            continue
```

For very large PDFs (hundreds of pages), prefer `pdftotext` (CLI) or `pypdfium2`
which use streaming approaches and are significantly faster.

## License Information

- **qpdf**: Apache License
- **pytesseract**: Apache License
- **Tesseract OCR**: Apache License
