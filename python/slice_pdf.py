import fitz
import xml.etree.ElementTree as ET
from HersheyFonts import HersheyFonts
import re
import sys

ET.register_namespace('', 'http://www.w3.org/2000/svg')
ET.register_namespace('xlink', 'http://www.w3.org/1999/xlink')
ET.register_namespace('inkscape', 'http://www.inkscape.org/namespaces/inkscape')

# Initialize Hershey font once globally
hf = HersheyFonts()
hf.load_default_font('futural')

def pdf_to_svg(pdf_path, page_index=0):
    doc = fitz.open(pdf_path)
    if doc.page_count == 0:
        raise ValueError("PDF has no pages.")
    page = doc[page_index]
    page.set_rotation(180)
    svg_string = page.get_svg_image(matrix=fitz.Identity)
    doc.close()
    return svg_string

def parse_matrix(transform_str):
    m = re.match(r'matrix\(([^)]+)\)', transform_str)
    if not m:
        return [1, 0, 0, 1, 0, 0]
    return [float(v) for v in m.group(1).split(',')]

def apply_matrix(matrix, x, y):
    a, b, c, d, e, f = matrix
    return (a*x + c*y + e, b*x + d*y + f)

HERSHEY_EM = 35.0
HERSHEY_BASELINE = 9.0  # shift up by the descender amount

def hershey_char_to_path(char, matrix):
    try:
        strokes = list(hf.strokes_for_text(char))
    except Exception:
        return None

    if not strokes:
        return None

    d_parts = []
    for stroke in strokes:
        if not stroke:
            continue
        first = True
        for x, y in stroke:
            # Normalize to 0..1 space before applying PDF matrix and flip y axis
            nx, ny = x / HERSHEY_EM, -(y - HERSHEY_BASELINE) / HERSHEY_EM
            tx, ty = apply_matrix(matrix, nx, ny)
            if first:
                d_parts.append(f"M {tx:.3f} {ty:.3f}")
                first = False
            else:
                d_parts.append(f"L {tx:.3f} {ty:.3f}")

    return ' '.join(d_parts) if d_parts else None

def replace_text_with_hershey(svg_string):
    """
    Parse SVG, find all <use> elements with data-text attributes,
    replace them with Hershey single-stroke <path> elements.
    Leaves original element in place if no glyph is found.
    """
    root = ET.fromstring(svg_string)
    root.attrib['style'] = 'background-color: white'

    replacements = []  # (parent, old_elem, new_elem or None)

    for parent in root.iter():
        for child in list(parent):
            tag = child.tag.split('}')[-1]
            if tag == 'use' and 'data-text' in child.attrib:
                char = child.attrib['data-text']
                transform = child.attrib.get('transform', '')
                matrix = parse_matrix(transform) if transform else [1, 0, 0, 1, 0, 0]

                d = hershey_char_to_path(char, matrix)

                if d:
                    new_path = ET.Element('path')
                    new_path.attrib['d'] = d
                    new_path.attrib['fill'] = 'none'
                    new_path.attrib['stroke'] = 'black'
                    new_path.attrib['stroke-width'] = '1'
                    replacements.append((parent, child, new_path))
                else:
                    replacements.append((parent, child, None))

    for parent, old_elem, new_elem in replacements:
        if new_elem is not None:
            idx = list(parent).index(old_elem)
            parent.remove(old_elem)
            parent.insert(idx, new_elem)

    return ET.tostring(root, encoding='unicode', xml_declaration=True)

def process(pdf_path):
    print(f"Loading {pdf_path}...")
    svg = pdf_to_svg(pdf_path)

    print("Substituting Hershey glyphs...")
    svg_out = replace_text_with_hershey(svg)

    with open("current.svg", 'w', encoding='utf-8') as f:
        f.write(svg_out)

    print(f"Written to current.svg")

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python3 slice_pdf.py input.pdf")
        sys.exit(1)

    process(sys.argv[1])