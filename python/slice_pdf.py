import fitz  # pymupdf
import xml.etree.ElementTree as ET
import re
import math


NS = {
    'svg': 'http://www.w3.org/2000/svg',
    'xlink': 'http://www.w3.org/1999/xlink'
}

PT_TO_MM = 0.352778

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

def parse_matrix(transform_str):
    """Extract a 6-value matrix from a transform attribute string."""
    m = re.match(r'matrix\(([^)]+)\)', transform_str)
    if not m:
        return [1, 0, 0, 1, 0, 0]
    return [float(v) for v in m.group(1).split(',')]

def apply_matrix(matrix, x, y):
    """Apply a 2D affine matrix [a,b,c,d,e,f] to a point (x, y)."""
    a, b, c, d, e, f = matrix
    return (a*x + c*y + e, b*x + d*y + f)

def parse_path_d(d_str):
    """
    Parse an SVG path `d` attribute into a list of (x, y) polylines.
    Returns a list of strokes, where each stroke is a list of (x, y) tuples.
    Handles M, L, C, Q, Z commands.
    """
    strokes = []
    current_stroke = []
    current_pos = (0, 0)

    tokens = re.findall(r'[MLCQZmlcqz]|[-+]?\d*\.?\d+(?:[eE][-+]?\d+)?', d_str)
    i = 0
    while i < len(tokens):
        cmd = tokens[i]
        i += 1

        if cmd == 'M':
            if current_stroke:
                strokes.append(current_stroke)
                current_stroke = []
            x, y = float(tokens[i]), float(tokens[i+1])
            i += 2
            current_pos = (x, y)
            current_stroke.append(current_pos)

        elif cmd == 'L':
            x, y = float(tokens[i]), float(tokens[i+1])
            i += 2
            current_pos = (x, y)
            current_stroke.append(current_pos)

        elif cmd == 'C':
            # Cubic bezier — sample midpoint and endpoint only (simplified)
            # cp1, cp2, endpoint
            cp1x, cp1y = float(tokens[i]), float(tokens[i+1])
            cp2x, cp2y = float(tokens[i+2]), float(tokens[i+3])
            ex, ey     = float(tokens[i+4]), float(tokens[i+5])
            i += 6
            # Subdivide into ~8 line segments
            x0, y0 = current_pos
            for t_step in range(1, 9):
                t = t_step / 8
                bx = (1-t)**3*x0 + 3*(1-t)**2*t*cp1x + 3*(1-t)*t**2*cp2x + t**3*ex
                by = (1-t)**3*y0 + 3*(1-t)**2*t*cp1y + 3*(1-t)*t**2*cp2y + t**3*ey
                current_stroke.append((bx, by))
            current_pos = (ex, ey)

        elif cmd == 'Q':
            # Quadratic bezier
            cpx, cpy = float(tokens[i]), float(tokens[i+1])
            ex, ey   = float(tokens[i+2]), float(tokens[i+3])
            i += 4
            x0, y0 = current_pos
            for t_step in range(1, 9):
                t = t_step / 8
                bx = (1-t)**2*x0 + 2*(1-t)*t*cpx + t**2*ex
                by = (1-t)**2*y0 + 2*(1-t)*t*cpy + t**2*ey
                current_stroke.append((bx, by))
            current_pos = (ex, ey)

        elif cmd == 'Z':
            if current_stroke:
                current_stroke.append(current_stroke[0])  # close path
                strokes.append(current_stroke)
                current_stroke = []

    if current_stroke:
        strokes.append(current_stroke)

    return strokes

def svg_to_paths(svg_string):
    """
    Parse SVG string and return all strokes as lists of (x_mm, y_mm) tuples.
    Resolves <use> references to glyph symbols and applies transforms.
    """
    root = ET.fromstring(svg_string)

    # Grab page dimensions from viewBox for later use
    viewbox = root.attrib.get('viewBox', '0 0 842 595').split()
    page_w_pt = float(viewbox[2])
    page_h_pt = float(viewbox[3])

    # Build a symbol/glyph lookup table from <symbol> and <path id=...> defs
    glyph_table = {}
    for elem in root.iter():
        tag = elem.tag.split('}')[-1]
        if tag in ('symbol', 'path') and 'id' in elem.attrib:
            glyph_table[elem.attrib['id']] = elem

    all_strokes = []

    def process_element(elem, parent_matrix=None):
        if parent_matrix is None:
            parent_matrix = [1, 0, 0, 1, 0, 0]

        tag = elem.tag.split('}')[-1]
        transform = elem.attrib.get('transform', '')
        local_matrix = parse_matrix(transform) if transform else [1, 0, 0, 1, 0, 0]

        # Combine parent and local matrix
        # For simplicity: apply local on top of parent (chained)
        def combine(a, b):
            # a then b
            return [
                a[0]*b[0] + a[1]*b[2],
                a[0]*b[1] + a[1]*b[3],
                a[2]*b[0] + a[3]*b[2],
                a[2]*b[1] + a[3]*b[3],
                a[4]*b[0] + a[5]*b[2] + b[4],
                a[4]*b[1] + a[5]*b[3] + b[5],
            ]

        matrix = combine(parent_matrix, local_matrix)

        if tag == 'path' and 'd' in elem.attrib:
            raw_strokes = parse_path_d(elem.attrib['d'])
            for stroke in raw_strokes:
                transformed = [apply_matrix(matrix, x, y) for x, y in stroke]
                # Convert pt -> mm
                transformed_mm = [(x * PT_TO_MM, y * PT_TO_MM) for x, y in transformed]
                all_strokes.append(transformed_mm)

        elif tag == 'use':
            href = elem.attrib.get('{http://www.w3.org/1999/xlink}href', '')
            ref_id = href.lstrip('#')
            if ref_id in glyph_table:
                process_element(glyph_table[ref_id], matrix)

        else:
            for child in elem:
                process_element(child, matrix)

    process_element(root)

    return all_strokes, page_w_pt, page_h_pt

def distance(p1, p2):
    """Euclidean distance between two points."""
    return math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2)

def optimize_paths(strokes):
    """
    Reorder strokes using a nearest-neighbor greedy algorithm to minimize
    pen-up travel distance. Returns a reordered list of strokes.
    """
    if not strokes:
        return []

    remaining = list(strokes)
    ordered = []
    current_pos = (0, 0)  # start at origin

    while remaining:
        # Find the stroke whose start point is closest to current position
        best_idx = 0
        best_dist = float('inf')
        best_reversed = False

        for i, stroke in enumerate(remaining):
            d_start = distance(current_pos, stroke[0])
            d_end   = distance(current_pos, stroke[-1])

            if d_start < best_dist:
                best_dist = d_start
                best_idx = i
                best_reversed = False

            if d_end < best_dist:
                best_dist = d_end
                best_idx = i
                best_reversed = True

        stroke = remaining.pop(best_idx)
        if best_reversed:
            stroke = list(reversed(stroke))

        ordered.append(stroke)
        current_pos = stroke[-1]

    return ordered

def emit_gcode(strokes, page_w_pt, page_h_pt, output_path):
    """
    Walk optimized strokes and write a .gcode file.
    Mirrors coordinates for top-right origin.
    page_w_pt and page_h_pt are in points, converted to mm for mirroring bounds.
    """
    page_w_mm = page_w_pt * PT_TO_MM
    page_h_mm = page_h_pt * PT_TO_MM

    def mirror(x, y):
        return (page_w_mm - x, page_h_mm - y)

    with open(output_path, 'w') as f:
        f.write("; Generated by pdf2gcode\n")
        f.write("G21 ; units in mm\n")
        f.write("G90 ; absolute positioning\n")
        f.write("M05 ; pen up\n")

        for stroke in strokes:
            if len(stroke) < 2:
                continue

            # Travel to start of stroke
            x, y = mirror(*stroke[0])
            f.write(f"M05 ; pen up\n")
            f.write(f"G00 X{x:.3f} Y{y:.3f}\n")
            f.write(f"M03 ; pen down\n")

            # Draw the stroke
            for point in stroke[1:]:
                x, y = mirror(*point)
                f.write(f"G01 X{x:.3f} Y{y:.3f}\n")

        # End of file — lift pen and return home
        f.write("\nM05 ; pen up\n")
        f.write("G00 X0 Y0 ; return to origin\n")

    print(f"Written to {output_path}")
    
svg = pdf_to_svg("PenPlotter Drawing v12.pdf")
strokes, pw, ph = svg_to_paths(svg)
optimized = optimize_paths(strokes)
emit_gcode(optimized, pw, ph, "/home/arduino/ArduinoApps/penplotter/PlotJobs/output.gcode")