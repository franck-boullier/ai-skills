# Command-Line Reference

Advanced CLI operations using poppler-utils and related tools.

## poppler-utils Advanced Features

### Inspect Document Metadata

```bash
# Display title, author, page count, PDF version, and more
pdfinfo document.pdf

# Machine-readable output (key: value pairs)
pdfinfo -meta document.pdf
```

Use `pdfinfo` as a fast first step before deciding how to process a PDF — it
tells you the page count, whether the PDF is encrypted, and its creation date
without reading the entire file.

### Inspect Fonts

```bash
# List all fonts embedded in or used by the PDF
pdffonts document.pdf

# Output columns: name, type, encoding, emb (embedded?), sub (subset?), uni (unicode?)
```

Use `pdffonts` to diagnose text extraction problems. If fonts are **not
embedded** (`emb: no`) or lack unicode mappings (`uni: no`), text extraction
may return garbled characters and OCR is a better fallback.

### Extract Text with Bounding Box Coordinates

```bash
pdftotext -bbox-layout document.pdf output.xml
```

The XML output contains precise coordinates for each text element — useful for
structured data extraction.

### Advanced Image Conversion

```bash
# Convert to PNG images with specific resolution
pdftoppm -png -r 300 document.pdf output_prefix

# Convert specific page range with high resolution
pdftoppm -png -r 600 -f 1 -l 3 document.pdf high_res_pages

# Convert to JPEG with quality setting
pdftoppm -jpeg -jpegopt quality=85 -r 200 document.pdf jpeg_output
```

### Extract Embedded Images

```bash
# Extract all embedded images with metadata
pdfimages -j -p document.pdf page_images

# List image info without extracting
pdfimages -list document.pdf

# Extract images in their original format
pdfimages -all document.pdf images/img
```

## License Information

- **poppler-utils**: GPL-2 License
