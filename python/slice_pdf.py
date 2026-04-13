import fitz  # pymupdf

def pdf_to_svg(pdf_path: str, page_index: int = 0) -> str:
    """
    Opens a PDF and returns page `page_index` as an SVG string.
    Defaults to page 1 (index 0). Any other pages are ignored.
    """
    doc = fitz.open(pdf_path)

    if doc.page_count == 0:
        raise ValueError("PDF has no pages.")

    page = doc[page_index]
    svg_string = page.get_svg_image(matrix=fitz.Identity)
    doc.close()

    return svg_string