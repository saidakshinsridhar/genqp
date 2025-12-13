import re

def classify_questions(text):
    parts = {"A": [], "B": [], "C": []}
    text = re.sub(r'\r', '\n', text)

    part_patterns = {
        "A": r'PART\s*[-–]?\s*A',
        "B": r'PART\s*[-–]?\s*B',
        "C": r'PART\s*[-–]?\s*C'
    }

    positions = {}
    for p, pat in part_patterns.items():
        m = re.search(pat, text, re.IGNORECASE)
        positions[p] = m.start() if m else None

    ordered = sorted((v, k) for k, v in positions.items() if v is not None)

    for i, (_, part) in enumerate(ordered):
        start = positions[part]
        end = ordered[i + 1][0] if i + 1 < len(ordered) else len(text)
        block = text[start:end]

        block = re.sub(r'\bCO\d.*|\bBlooms.*|\bLevel.*', '', block, flags=re.IGNORECASE)

        if part == "B":
            chunks = re.split(r'\bOR\b|\(\s*[ab]\s*\)', block, flags=re.IGNORECASE)
            for c in chunks:
                cleaned = re.sub(r'\s+', ' ', c).strip()
                if len(cleaned) > 80:
                    parts[part].append({
                        "id": f"{part}_{len(parts[part])}",
                        "text": cleaned
                    })

        else:
            qs = re.split(r'\n\s*(?:\d+\.|Q\d+|Question\s+\d+)', block, flags=re.IGNORECASE)
            for q in qs[1:]:
                cleaned = re.sub(r'\s+', ' ', q).strip()
                if len(cleaned) > 30:
                    parts[part].append({
                        "id": f"{part}_{len(parts[part])}",
                        "text": cleaned
                    })


    return parts
