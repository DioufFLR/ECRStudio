"""
Hierarchical tree builder for ECR files.

Builds a parent-child tree structure from a flat list of ECR lines,
following the hierarchy: VER > DOS > EXO > (CPT|TVA|JOU|ECR) > (MVT|TIERS) > (ECHMVT|ANAMVT).
"""

from .parser import get_record_type, read_field
from .constants import HIERARCHY_LEVEL


class TreeNode:
    """A node in the ECR hierarchy tree."""

    def __init__(self, line_index, record_type, label):
        self.line_index = line_index
        self.record_type = record_type
        self.label = label
        self.children = []
        self.parent = None

    def add_child(self, child):
        child.parent = self
        self.children.append(child)


def build_tree(lines):
    """Build a hierarchical tree from ECR lines.

    Returns a list of root TreeNodes (typically just one VER node).
    """
    roots = []
    # Stack: list of (level, TreeNode)
    stack = []

    for i, line in enumerate(lines):
        rec_type = get_record_type(line)
        level = HIERARCHY_LEVEL.get(rec_type, 0)
        label = _make_label(line, rec_type)
        node = TreeNode(i, rec_type, label)

        if level == 0:
            roots.append(node)
            stack = [(0, node)]
        else:
            # Pop stack to find parent at a lower level
            while stack and stack[-1][0] >= level:
                stack.pop()
            if stack:
                stack[-1][1].add_child(node)
            else:
                roots.append(node)
            stack.append((level, node))

    return roots


def _make_label(line, rec_type):
    """Create a human-readable label for a tree node."""
    try:
        if rec_type == "VER":
            lib = read_field(line, 19, 30).strip()
            return f"VER — {lib}" if lib else "VER"
        elif rec_type == "DOS":
            num = read_field(line, 7, 8).strip()
            lib = read_field(line, 15, 30).strip()
            return f"DOS {num} — {lib}"
        elif rec_type == "EXO":
            debut = read_field(line, 7, 8).strip()
            fin = read_field(line, 15, 8).strip()
            return f"EXO {debut} - {fin}"
        elif rec_type == "CPT":
            num = read_field(line, 7, 10).strip()
            lib = read_field(line, 17, 30).strip()
            return f"CPT {num} — {lib}"
        elif rec_type == "ECR":
            jou = read_field(line, 7, 2).strip()
            date = read_field(line, 9, 8).strip()
            lib = read_field(line, 25, 30).strip()
            return f"ECR {jou} {date} — {lib}"
        elif rec_type == "MVT":
            cpt = read_field(line, 7, 10).strip()
            lib = read_field(line, 17, 30).strip()
            deb = read_field(line, 47, 13).strip()
            cre = read_field(line, 60, 13).strip()
            amounts = f"D:{deb}" if deb and deb != "0" * len(deb) else ""
            if cre and cre != "0" * len(cre):
                amounts += f" C:{cre}" if amounts else f"C:{cre}"
            return f"MVT {cpt} — {lib}  {amounts}".strip()
        elif rec_type == "TVA":
            code = read_field(line, 7, 2).strip()
            lib = read_field(line, 9, 30).strip()
            return f"TVA {code} — {lib}"
        elif rec_type == "JOU":
            code = read_field(line, 7, 2).strip()
            lib = read_field(line, 9, 30).strip()
            return f"JOU {code} — {lib}"
        elif rec_type == "TIERS":
            lib = read_field(line, 7, 30).strip()
            return f"TIERS — {lib}"
        elif rec_type == "ECHMVT":
            ttc = read_field(line, 7, 13).strip()
            ech = read_field(line, 30, 8).strip()
            return f"ECHMVT TTC:{ttc} Ech:{ech}"
        elif rec_type == "ANAMVT":
            code = read_field(line, 7, 6).strip()
            lib = read_field(line, 15, 40).strip()
            return f"ANAMVT {code} — {lib}"
        else:
            return f"{rec_type} — {line[6:50].strip()}"
    except Exception:
        return rec_type
