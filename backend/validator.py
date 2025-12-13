def validate_bank(parts, exam_type):
    """
    parts: dict with keys A, B, C
    exam_type: 'UNIT', 'CAT', 'ENDSEM'
    """

    req = {
        "UNIT":  {"A": 10, "B": 2,  "C": 2},
        "CAT":   {"A": 10, "B": 8,  "C": 4},
        "ENDSEM":{"A": 20, "B": 20, "C": 4},
    }

    if exam_type not in req:
        raise ValueError("Unknown exam type")

    for part in ["A", "B", "C"]:
        if len(parts.get(part, [])) < req[exam_type][part]:
            raise ValueError(
                f"Insufficient Part {part} questions for {exam_type} exam. "
                f"Required: {req[exam_type][part]}, Found: {len(parts.get(part, []))}"
            )

    return True
