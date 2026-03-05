"""
Application constants: colors, hierarchy rules, record type metadata.
"""

# Background colors for each record type (light theme)
COLORS_LIGHT = {
    "VER":    "#d4edda",
    "DOS":    "#cce5ff",
    "EXO":    "#fff3cd",
    "CPT":    "#e2d9f3",
    "ECR":    "#fde8d8",
    "MVT":    "#d1ecf1",
    "TVA":    "#f8d7da",
    "JOU":    "#d6eaf8",
    "TIERS":  "#fdfefe",
    "ECHMVT": "#eafaf1",
    "ANAMVT": "#fef9e7",
}

# Background colors for each record type (dark theme) — brighter for readability
COLORS_DARK = {
    "VER":    "#264d38",
    "DOS":    "#253d5e",
    "EXO":    "#4d4530",
    "CPT":    "#3d3455",
    "ECR":    "#4d3a2a",
    "MVT":    "#2a4048",
    "TVA":    "#4d2a33",
    "JOU":    "#2a3d50",
    "TIERS":  "#383838",
    "ECHMVT": "#2a4540",
    "ANAMVT": "#45432a",
}

# Foreground text colors for dark theme
TEXT_COLORS_DARK = {
    "VER":    "#a8e6cf",
    "DOS":    "#a8d4ff",
    "EXO":    "#ffe0a3",
    "CPT":    "#c9b8e8",
    "ECR":    "#ffc8a8",
    "MVT":    "#a8d8e6",
    "TVA":    "#e8a8b0",
    "JOU":    "#a8c8e8",
    "TIERS":  "#d0d0d0",
    "ECHMVT": "#a8e6d8",
    "ANAMVT": "#e6e0a8",
}

# Field type display colors
FIELD_TYPE_COLORS = {
    "Alpha": "#1a5276",
    "Num":   "#784212",
    "Date":  "#145a32",
}

FIELD_TYPE_COLORS_DARK = {
    "Alpha": "#7fb3d4",
    "Num":   "#d4a86a",
    "Date":  "#6ad4a8",
}

# ECR hierarchy definition
# Each type maps to its valid children types
HIERARCHY = {
    "VER":    ["DOS"],
    "DOS":    ["EXO"],
    "EXO":    ["CPT", "TVA", "JOU", "ECR"],
    "CPT":    ["TIERS", "ANACPT"],
    "ECR":    ["MVT"],
    "MVT":    ["ANAMVT", "ECHMVT"],
    "TVA":    [],
    "JOU":    [],
    "TIERS":  [],
    "ECHMVT": [],
    "ANAMVT": [],
}

# Hierarchy levels for indentation
HIERARCHY_LEVEL = {
    "VER":    0,
    "DOS":    1,
    "EXO":    2,
    "CPT":    3,
    "TVA":    3,
    "JOU":    3,
    "ECR":    3,
    "MVT":    4,
    "TIERS":  4,
    "ECHMVT": 5,
    "ANAMVT": 5,
}

# All known record types in display order
ALL_TYPES = ["VER", "DOS", "EXO", "CPT", "ECR", "MVT", "TVA", "JOU", "TIERS", "ECHMVT", "ANAMVT"]

# Light theme palette
THEME_LIGHT = {
    "bg":            "#f0f2f5",
    "toolbar_bg":    "#2c3e50",
    "toolbar_fg":    "white",
    "text_fg":       "#2c3e50",
    "text_muted":    "#7f8c8d",
    "text_secondary": "#95a5a6",
    "entry_bg":      "#ffffff",
    "entry_alt_bg":  "#f8f9fa",
    "status_bg":     "#2c3e50",
    "status_fg":     "#ecf0f1",
    "error_fg":      "#e74c3c",
    "success_fg":    "#2ecc71",
    "sash_bg":       "#dfe6e9",
    "header_bg":     "#2c3e50",
    "header_fg":     "white",
    "btn_open":      "#3498db",
    "btn_save":      "#27ae60",
    "btn_saveas":    "#8e44ad",
    "btn_apply":     "#27ae60",
    "btn_cancel":    "#e74c3c",
    "btn_validate":  "#e67e22",
    "btn_add":       "#2980b9",
    "btn_dup":       "#16a085",
    "btn_del":       "#c0392b",
    "btn_fg":        "#ffffff",
}

# Dark theme palette
THEME_DARK = {
    "bg":            "#1e1e2e",
    "toolbar_bg":    "#181825",
    "toolbar_fg":    "#cdd6f4",
    "text_fg":       "#cdd6f4",
    "text_muted":    "#a6adc8",
    "text_secondary": "#7f849c",
    "entry_bg":      "#313244",
    "entry_alt_bg":  "#2a2b3d",
    "status_bg":     "#181825",
    "status_fg":     "#bac2de",
    "error_fg":      "#f38ba8",
    "success_fg":    "#a6e3a1",
    "sash_bg":       "#313244",
    "header_bg":     "#181825",
    "header_fg":     "#cdd6f4",
    "btn_open":      "#3b6ea5",
    "btn_save":      "#2e7d46",
    "btn_saveas":    "#6c4fa0",
    "btn_apply":     "#2e7d46",
    "btn_cancel":    "#a83250",
    "btn_validate":  "#b36b2a",
    "btn_add":       "#2a7a9e",
    "btn_dup":       "#1f7a6a",
    "btn_del":       "#9e3a4a",
    "btn_fg":        "#ffffff",
}
