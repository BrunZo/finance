"""
PDF table extraction by section titles. Always uses explicit vertical lines from header row.
"""

MARGIN = 10


def find_text(
    pdf, text: str, ref_page: int | None = None, ref_bbox: dict | None = None
) -> tuple[int, dict] | None:
    """First occurrence of text after ref position, or None."""
    for page_idx, page in enumerate(pdf.pages):
        if ref_page is not None and page_idx < ref_page:
            continue
        matches = page.search(text)
        for m in matches:
            if ref_bbox is not None and page_idx == ref_page and m["top"] < ref_bbox["bottom"]:
                continue
            return (page_idx, m)
    return None


def _find_table_start(
    pdf, start: tuple[int, dict], end: tuple[int, dict], table_config: dict, margin: float
) -> tuple[int, float]:
    """
    Find where the table header row actually is (may be on next page after section title).
    Returns (page_idx, top) of the first occurrence of the first column header in the region.
    """
    page_a, bbox_a = start
    page_b, bbox_b = end
    left = table_config.get("left_columns") or []
    if not left:
        return (page_a, bbox_a["bottom"] + margin)
    first_header = left[0]
    for page_idx in range(page_a, page_b + 1):
        page = pdf.pages[page_idx]
        if page_idx == page_a:
            y0 = bbox_a["bottom"] + margin
            y1 = page.height
        elif page_idx == page_b:
            y0 = 0
            y1 = bbox_b["top"] - margin
        else:
            y0, y1 = 0, page.height
        if y0 >= y1:
            continue
        cropped = page.crop((0, y0, page.width, y1))
        matches = cropped.search(first_header)
        if matches:
            m = min(matches, key=lambda x: (x["top"], x["x0"]))
            return (page_idx, m["top"])
    return (page_a, bbox_a["bottom"] + margin)


def _explicit_vertical_lines(cropped_page, table_config: dict, offset: float) -> list[float]:
    """Build explicit_vertical_lines from first occurrence of each header. Uses param offset."""
    left = table_config.get("left_columns")
    right = table_config.get("right_columns")
    headers = left + right
    bboxes = []
    for h in headers:
        matches = cropped_page.search(h)
        m = min(matches, key=lambda x: (x["top"], x["x0"]))
        bboxes.append(m)
    lines = [bboxes[i]["x0"] for i in range(len(left))]
    if right:
        first_right_idx = len(left)
        lines.append(bboxes[first_right_idx]["x0"] + offset)
        lines.extend(bboxes[i]["x1"] for i in range(first_right_idx, len(bboxes)))
    return sorted(set(lines))


def extract_table_between(
    pdf,
    start: tuple[int, dict],
    end: tuple[int, dict],
    table_config: dict,
    *,
    margin: float = MARGIN,
    snap_tolerance: float = 10,
    offset: float = -10,
) -> list[list]:
    """Extract table between two section headers. Table may start on next page after title."""
    page_a, bbox_a = start
    page_b, bbox_b = end
    bottom = bbox_b["top"] - margin

    content_page, content_top = _find_table_start(pdf, start, end, table_config, margin)
    page_w = pdf.pages[content_page].width
    page_h = pdf.pages[content_page].height
    first_crop = pdf.pages[content_page].crop(
        (0, content_top, page_w, page_h if content_page != page_b else bottom)
    )
    lines = _explicit_vertical_lines(first_crop, table_config, offset)
    settings = {
        "vertical_strategy": "explicit",
        "explicit_vertical_lines": lines,
        "horizontal_strategy": "text",
        "snap_tolerance": snap_tolerance,
    }

    def extract(cropped):
        return cropped.extract_table(settings)

    rows = []
    if content_page == page_b:
        if content_top < bottom:
            t = extract(first_crop)
            if t:
                rows = t
    else:
        t = extract(first_crop)
        if t:
            rows.extend(t)
        for p in range(content_page + 1, page_b):
            t = pdf.pages[p].extract_table(settings)
            if t:
                rows.extend(t[1:] if rows else t)
        if bottom > 0:
            t = extract(pdf.pages[page_b].crop((0, 0, pdf.pages[page_b].width, bottom)))
            if t:
                rows.extend(t[1:] if rows else t)
    return rows
