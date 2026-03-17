"""Convert each page of a PDF file to a PNG image.

Dependencies:
    pip install pdf2image Pillow
    System: poppler-utils (provides pdftoppm used internally by pdf2image)
        - Linux:   sudo apt-get install poppler-utils
        - macOS:   brew install poppler
        - Windows: https://github.com/oschwartz10612/poppler-windows/releases

Usage:
    python convert_pdf_to_images.py <input_pdf> <output_directory>
"""

import os
import sys

from pdf2image import convert_from_path
from PIL import Image


def convert(pdf_path, output_dir, max_dim=1000):
    """Convert every page of *pdf_path* to a PNG saved in *output_dir*.

    Each image is scaled so that neither width nor height exceeds *max_dim*
    pixels, preserving the original aspect ratio.
    """
    # Ensure the input PDF file exists before proceeding
    if not os.path.isfile(pdf_path):
        print(f"Error: input file not found: {pdf_path}")
        sys.exit(1)

    # Create the output directory if it does not exist
    if not os.path.isdir(output_dir):
        try:
            os.makedirs(output_dir, exist_ok=True)
            print(f"Created output directory: {output_dir}")
        except OSError as exc:
            print(f"Error: cannot create output directory '{output_dir}': {exc}")
            sys.exit(1)

    # Render each PDF page to a PIL Image at 200 DPI (used by pdf2image/pdftoppm)
    try:
        images = convert_from_path(pdf_path, dpi=200)
    except Exception as exc:
        print(f"Error: failed to convert PDF to images: {exc}")
        sys.exit(1)

    # Scale and save each page as a PNG, keeping aspect ratio within max_dim
    for i, image in enumerate(images):
        width, height = image.size
        if width > max_dim or height > max_dim:
            scale_factor = min(max_dim / width, max_dim / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            # LANCZOS gives the best quality for downscaling; use the
            # compat alias so this works on both Pillow <9 and >=10.
            resample = getattr(Image, "Resampling", Image).LANCZOS
            image = image.resize((new_width, new_height), resample)

        image_path = os.path.join(output_dir, f"page_{i + 1}.png")
        image.save(image_path)
        print(f"Saved page {i + 1} as {image_path} (size: {image.size})")

    print(f"Converted {len(images)} pages to PNG images")


# CLI entry point: require exactly two arguments (input PDF and output directory)
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_pdf_to_images.py <input_pdf> <output_directory>")
        sys.exit(1)
    convert(sys.argv[1], sys.argv[2])
