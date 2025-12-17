import re
import pdfplumber
import re


def split_by_unit(text):
    """
    Splits text into UNIT-wise blocks.
    Supports:
    - Unit I / Unit II / Unit III
    - UNIT – I / UNIT - II
    - I. <Unit Title>
    """

    unit_pattern = re.compile(
        r'(\bUNIT\s*[-–]?\s*(?:\d+|I|II|III|IV|V)\b|\b(?:I|II|III|IV|V)\.\s*[A-Z])',
        re.IGNORECASE
    )

    matches = list(unit_pattern.finditer(text))

    units = {}

    if not matches:
        return units

    for i, match in enumerate(matches):
        unit_raw = match.group(1)

        # Normalize unit name
        num = re.search(r'(\d+|I|II|III|IV|V)', unit_raw, re.IGNORECASE)
        unit_id = num.group(1).upper()
        unit_key = f"UNIT{unit_id}"

        start = match.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)

        units[unit_key] = text[start:end]

    return units
def fallback_split_by_unit_using_partA(text):
    """
    Fallback splitter when UNIT headings are implicit.
    Uses Part A question count windows (10 per unit).
    """

    # Roughly extract all Part A questions first
    part_a_candidates = re.split(
        r'\n\s*(?:\d+\.|Q\d+|Question\s+\d+)',
        text,
        flags=re.IGNORECASE
    )

    # Keep only meaningful questions
    part_a_questions = [
        q for q in part_a_candidates if len(q.strip()) > 30
    ]

    units = {}
    UNIT_SIZE = 10  # Part A questions per unit

    for i in range(0, len(part_a_questions), UNIT_SIZE):
        unit_index = i // UNIT_SIZE + 1
        unit_key = f"UNIT{unit_index}"
        units[unit_key] = "\n".join(
            part_a_questions[i:i + UNIT_SIZE]
        )

    return units


def split_questions(text):
    """
    Splits cleaned text into question blocks using numbering anchors.
    """
    lines = [l.strip() for l in text.split("\n") if l.strip()]

    questions = []
    current = ""

    q_start = re.compile(r'^(Q\.?\s*\d+|\d+[\.\)])\s*', re.IGNORECASE)

    for line in lines:
        if q_start.match(line):
            if current:
                questions.append(current.strip())
            current = q_start.sub("", line)
        else:
            if current:
                current += " " + line

    if current:
        questions.append(current.strip())

    return [q for q in questions if len(q) > 25]

def is_diagram_question(q):
    """
    Heuristic to detect diagram-based questions.
    """
    keywords = [
        "following graph",
        "following diagram",
        "given graph",
        "given figure",
        "draw",
        "illustrate",
        "show the graph",
        "cost matrix",
        "table below"
    ]
    q_lower = q.lower()
    return any(k in q_lower for k in keywords)


def split_by_part(text):
    """
    OCR-tolerant split for PART A / B / C.
    Matches 'Part A', 'Part B', 'Part C' even inside tables or lines.
    """
    import re

    pattern = re.compile(
        r'(?:^|\n).*?\bPART\s*([ABC])\b.*?(?:\n|$)',
        re.IGNORECASE
    )

    matches = list(pattern.finditer(text))
    parts = {}

    for i, m in enumerate(matches):
        part = m.group(1).upper()
        start = m.end()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        parts[part] = text[start:end]

    return parts



def classify_questions(text):
    """
    OCR-safe classification based on question order and length.
    Works even when PART headers are missing or broken.
    """
    qs = split_questions(text)

    # Remove very short junk
    qs = [q for q in qs if len(q.strip()) > 25]

    # Preserve order, but also keep length info
    qs_with_len = [(q, len(q)) for q in qs]

    result = {"A": [], "B": [], "C": []}

    # Heuristics (tuned for Anna Univ style)
    A_COUNT = min(8, len(qs_with_len))   # short questions
    C_COUNT = min(2, len(qs_with_len) // 5)  # long problems

    partA = qs_with_len[:A_COUNT]
    partC = qs_with_len[-C_COUNT:]
    partB = qs_with_len[A_COUNT:-C_COUNT]

    for i, (q, _) in enumerate(partA):
        result["A"].append({
            "id": f"A_{i}",
            "text": q,
            "type": "diagram" if is_diagram_question(q) else "text"
        })

    for i, (q, _) in enumerate(partB):
        result["B"].append({
            "id": f"B_{i}",
            "text": q,
            "type": "diagram" if is_diagram_question(q) else "text"
        })

    for i, (q, _) in enumerate(partC):
        result["C"].append({
            "id": f"C_{i}",
            "text": q,
            "type": "diagram" if is_diagram_question(q) else "text"
        })

    return result


def classify_questions_by_unit(text):
    """
    Returns:
    {
      UNIT1: {A: [...], B: [...], C: [...]},
      UNIT2: {A: [...], B: [...], C: [...]},
      ...
    }
    """

    # Step 1: try explicit UNIT split
    units = split_by_unit(text)

    # Step 2: fallback if only one or none found
    if len(units) <= 1:
        units = fallback_split_by_unit_using_partA(text)

    # Step 3: classify each UNIT separately
    unit_wise_parts = {}

    for unit, unit_text in units.items():
        unit_parts = classify_questions(unit_text)
        unit_wise_parts[unit] = unit_parts

    return unit_wise_parts

def clean_and_merge_questions(lines):
    questions = []
    current = ""

    for line in lines:
        line = line.strip()

        # Skip metadata / noise
        if re.search(r'\bCO\d|\bK\d|\bBlooms|\bQuestions\b$', line, re.IGNORECASE):
            continue

        # New question starts
        if re.match(r'\d+\.', line):
            if current:
                questions.append(current.strip())
            current = line
        else:
            current += " " + line

    if current:
        questions.append(current.strip())

    return questions


def classify_questions_from_pdf(pdf_path):
    parts = {"A": [], "B": [], "C": []}
    current_part = None
    buffer = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = text.split("\n")

            for line in lines:
                line = line.strip()
                # Skip table header rows (VERY IMPORTANT)
                if re.search(r'Q\.?\s*No\s+Questions', line, re.IGNORECASE):
                    continue


                # Detect PART headers
                part_match = re.search(r'\bPART\s*([ABC])\b', line, re.IGNORECASE)
                if part_match:
                    # Flush buffer when switching part
                    if current_part and buffer:
                        q_text = " ".join(buffer).strip()
                        parts[current_part].append({
                            "id": f"{current_part}_{len(parts[current_part])}",
                            "text": q_text,
                            "type": "diagram" if is_diagram_question(q_text) else "text"
                        })
                        buffer = []

                    current_part = part_match.group(1).upper()
                    continue

                # Skip noise
                if re.search(r'\bCO\d|\bK\d|\bBlooms|\bQuestions\b$', line, re.IGNORECASE):
                    continue

                # New question starts
                if current_part and re.match(r'^(\d+[\.\)]|Q\.?\s*No\.?\s*\d*|Q\s*\d+)',line,re.IGNORECASE):

                    if buffer:
                        q_text = " ".join(buffer).strip()
                        parts[current_part].append({
                            "id": f"{current_part}_{len(parts[current_part])}",
                            "text": q_text,
                            "type": "diagram" if is_diagram_question(q_text) else "text"
                        })
                    buffer = [line]
                else:
                    if current_part and line:
                        buffer.append(line)

    # Flush remaining buffer
    if current_part and buffer:
        q_text = " ".join(buffer).strip()
        parts[current_part].append({
            "id": f"{current_part}_{len(parts[current_part])}",
            "text": q_text,
            "type": "diagram" if is_diagram_question(q_text) else "text"
        })

    return parts
def classify_questions_by_unit_from_pdf(pdf_path):
    import pdfplumber, re

    units = {}
    current_unit = None
    current_part = None
    buffer = []

    def flush():
        nonlocal buffer
        if current_unit and current_part and buffer:
            q_text = " ".join(buffer).strip()
            units[current_unit][current_part].append({
                "id": f"{current_part}_{len(units[current_unit][current_part])}",
                "text": q_text,
                "type": "diagram" if is_diagram_question(q_text) else "text"
            })
            buffer = []

    with pdfplumber.open(pdf_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            lines = text.split("\n")

            for line in lines:
                line = line.strip()

                # Detect UNIT
                unit_match = re.search(r'\bUNIT\s*[-–]?\s*(\d+|I|II|III|IV|V)\b', line, re.IGNORECASE)
                if unit_match:
                    current_unit = unit_match.group(1)
                    if current_unit not in units:
                        units[current_unit] = {"A": [], "B": [], "C": []}
                    current_part = None
                    buffer = []
                    continue

                # Detect PART
                part_match = re.search(r'\bPART\s*([ABC])\b', line, re.IGNORECASE)
                if part_match:
                    current_part = part_match.group(1).upper()
                    buffer = []
                    continue

                # Skip junk lines
                if re.search(r'Q\.?\s*No\s+Questions|CO\d|K\d|Blooms', line, re.IGNORECASE):
                    continue

                # New question start
                if current_unit and current_part and re.match(
                    r'^(\d+[\.\)]|Q\.?\s*No\.?\s*\d*|Q\s*\d+)',
                    line,
                    re.IGNORECASE
                ):
                    flush()
                    buffer = [line]
                else:
                    if current_unit and current_part and line:
                        flush()
                        buffer.append(line)

    flush()
    return units
