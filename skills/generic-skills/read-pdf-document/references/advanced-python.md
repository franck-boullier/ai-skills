# Advanced Python Techniques

## pypdfium2 Library (Apache/BSD License)

pypdfium2 is a Python binding for PDFium (Chromium's PDF library). It's excellent for fast PDF rendering and image generation.

### Render PDF to Images

```python
import pypdfium2 as pdfium
from PIL import Image

pdf = pdfium.PdfDocument("document.pdf")

page = pdf[0]
bitmap = page.render(
    scale=2.0,
    rotation=0
)

img = bitmap.to_pil()
img.save("page_1.png", "PNG")

for i, page in enumerate(pdf):
    bitmap = page.render(scale=1.5)
    img = bitmap.to_pil()
    img.save(f"page_{i+1}.jpg", "JPEG", quality=90)
```

### Extract Text with pypdfium2

```python
import pypdfium2 as pdfium

pdf = pdfium.PdfDocument("document.pdf")
for i, page in enumerate(pdf):
    text = page.get_text()
    print(f"Page {i+1} text length: {len(text)} chars")
```

## pdfplumber Advanced Features

### Extract Text with Precise Coordinates

```python
import pdfplumber

with pdfplumber.open("document.pdf") as pdf:
    page = pdf.pages[0]

    chars = page.chars
    for char in chars[:10]:
        print(f"Char: '{char['text']}' at x:{char['x0']:.1f} y:{char['y0']:.1f}")

    bbox_text = page.within_bbox((100, 100, 400, 200)).extract_text()
```

### Advanced Table Extraction with Custom Settings

```python
import pdfplumber
import pandas as pd

with pdfplumber.open("complex_table.pdf") as pdf:
    page = pdf.pages[0]

    table_settings = {
        "vertical_strategy": "lines",
        "horizontal_strategy": "lines",
        "snap_tolerance": 3,
        "intersection_tolerance": 15
    }
    tables = page.extract_tables(table_settings)

    img = page.to_image(resolution=150)
    img.save("debug_layout.png")
```

## Extract Figures/Images with pypdfium2

```python
import pypdfium2 as pdfium
from PIL import Image

def extract_figures(pdf_path, output_dir):
    pdf = pdfium.PdfDocument(pdf_path)

    for page_num, page in enumerate(pdf):
        bitmap = page.render(scale=3.0)
        img = bitmap.to_pil()
        img.save(f"{output_dir}/page_{page_num+1}.png")
```

## Batch Text Extraction with Error Handling

```python
import os
import glob
from pypdf import PdfReader
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def batch_extract_text(input_dir):
    pdf_files = glob.glob(os.path.join(input_dir, "*.pdf"))

    for pdf_file in pdf_files:
        try:
            reader = PdfReader(pdf_file)
            text = ""
            for page in reader.pages:
                text += page.extract_text()

            output_file = pdf_file.replace('.pdf', '.txt')
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(text)
            logger.info(f"Extracted text from: {pdf_file}")

        except Exception as e:
            logger.error(f"Failed to extract text from {pdf_file}: {e}")
            continue
```

## Performance Optimization Tips

### For Text Extraction

- `pdftotext -bbox-layout` is fastest for plain text extraction
- Use pdfplumber for structured data and tables
- Avoid `pypdf.extract_text()` for very large documents

### For Image Extraction

- `pdfimages` is much faster than rendering pages
- Use low resolution for previews, high resolution for final output

### For Large PDFs

- Use streaming approaches instead of loading entire PDF in memory
- Process pages individually with pypdfium2

## License Information

- **pypdf**: BSD License
- **pdfplumber**: MIT License
- **pypdfium2**: Apache/BSD License
