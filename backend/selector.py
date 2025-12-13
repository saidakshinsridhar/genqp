import random

def reindex(part_list, prefix):
    out = []
    for i, q in enumerate(part_list):
        out.append({
            "id": f"{prefix}_{i}",
            "text": q["text"]
        })
    return out


import random

def generate_unit_test(parts):
    A = reindex(parts["A"], "A")
    B = reindex(parts["B"], "B")
    C = reindex(parts["C"], "C")

    a_qs = random.sample(A, 10)
    b_qs = random.sample(B, 2)
    c_qs = random.sample(C, 2)

    return {
        "QPA": {
            "A": a_qs[:5],
            "B": [b_qs[0]],
            "C": [c_qs[0]],
        },
        "QPB": {
            "A": a_qs[5:],
            "B": [b_qs[1]],
            "C": [c_qs[1]],
        }
    }
def generate_cat(parts):
    A = reindex(parts["A"], "A")
    B = reindex(parts["B"], "B")
    C = reindex(parts["C"], "C")

    a_qs = random.sample(A, 10)
    b_qs = random.sample(B, 4)
    c_qs = random.sample(C, 2)

    return {
        "QPA": {
            "A": a_qs[:5],
            "B": [{"choice": b_qs[:2]}],
            "C": [{"choice": c_qs[:1]}],
        },
        "QPB": {
            "A": a_qs[5:],
            "B": [{"choice": b_qs[2:]}],
            "C": [{"choice": c_qs[1:]}],
        }
    }


def generate_endsem(parts):
    A = reindex(parts["A"], "A")
    B = reindex(parts["B"], "B")
    C = reindex(parts["C"], "C")

    a_qs = random.sample(A, 20)
    b_qs = random.sample(B, 10)
    c_qs = random.sample(C, 2)

    return {
        "QPA": {
            "A": a_qs[:10],
            "B": [{"choice": b_qs[:2*i+2]} for i in range(5)],
            "C": [{"choice": c_qs[:1]}],
        },
        "QPB": {
            "A": a_qs[10:],
            "B": [{"choice": b_qs[2*i:2*i+2]} for i in range(5)],
            "C": [{"choice": c_qs[1:]}],
        }
    }
