import random
from backend.classifier import classify_questions_by_unit_from_pdf


# -------------------------
# END SEMESTER GENERATION
# -------------------------

def generate_endsem(pdf_path):
    """
    END SEMESTER FORMAT

    Part A:
    - 2 questions from each unit

    Part B:
    - 1 question from each unit
    - Each question has 2 choices
    - (2 unique questions per unit)

    Part C:
    - 1 question with 2 choices
    """

    units = classify_questions_by_unit_from_pdf(pdf_path)

    # ---------- PART A ----------
    partA = []
    for unit in units:
        if len(units[unit]["A"]) < 2:
            raise ValueError(f"UNIT {unit} has fewer than 2 Part-A questions")
        partA.extend(units[unit]["A"][:2])

    # ---------- PART B ----------
    partB = []
    for unit in units:
        if len(units[unit]["B"]) < 2:
            raise ValueError(f"UNIT {unit} has fewer than 2 Part-B questions")
        choices = units[unit]["B"][:2]
        partB.append({
            "unit": unit,
            "choice": choices
        })

    # ---------- PART C ----------
    # Pick ANY unit that has at least 2 Part C questions
    partC_unit = None
    for unit in units:
        if len(units[unit]["C"]) >= 2:
            partC_unit = unit
            break

    if not partC_unit:
        raise ValueError("No unit has 2 Part-C questions")

    partC = {
        "unit": partC_unit,
        "choice": units[partC_unit]["C"][:2]
    }

    return {
        "PartA": partA,
        "PartB": partB,
        "PartC": partC
    }


# -------------------------
# CAT GENERATION
# -------------------------

def generate_cat(pdf_path):
    """
    CAT FORMAT

    Part A:
    - 5 questions
    - 2 from units with >10 Part-A questions
    - 1 from unit with <=10 Part-A questions

    Part B:
    - 2 questions from 2 different units
    - Each question has 2 choices

    Part C:
    - 1 question with 2 choices
    - Unit must NOT be used in Part B
    """

    units = classify_questions_by_unit_from_pdf(pdf_path)

    # ---------- PART A ----------
    high_units = []
    low_units = []

    for unit in units:
        if len(units[unit]["A"]) > 10:
            high_units.append(unit)
        else:
            low_units.append(unit)

    if len(high_units) < 2 or len(low_units) < 1:
        raise ValueError("Insufficient unit distribution for CAT Part A")

    partA = []
    partA.extend(units[high_units[0]]["A"][:2])
    partA.extend(units[high_units[1]]["A"][:2])
    partA.append(units[low_units[0]]["A"][0])

    # ---------- PART B ----------
    if len(units) < 2:
        raise ValueError("Need at least 2 units for CAT Part B")

    used_units = random.sample(list(units.keys()), 2)
    partB = []

    for unit in used_units:
        if len(units[unit]["B"]) < 2:
            raise ValueError(f"UNIT {unit} has fewer than 2 Part-B questions")
        partB.append({
            "unit": unit,
            "choice": units[unit]["B"][:2]
        })

    # ---------- PART C ----------
    remaining_units = [u for u in units if u not in used_units]

    partC_unit = None
    for unit in remaining_units:
        if len(units[unit]["C"]) >= 2:
            partC_unit = unit
            break

    if not partC_unit:
        raise ValueError("No suitable unit found for CAT Part C")

    partC = {
        "unit": partC_unit,
        "choice": units[partC_unit]["C"][:2]
    }

    return {
        "PartA": partA,
        "PartB": partB,
        "PartC": partC
    }


# -------------------------
# ENTRY POINT
# -------------------------

def generate_papers(pdf_path, exam_type):
    if exam_type == "ENDSEM":
        return generate_endsem(pdf_path)
    elif exam_type == "CAT":
        return generate_cat(pdf_path)
    else:
        raise ValueError("Unsupported exam type")
