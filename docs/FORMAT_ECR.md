# ECR File Format Reference

## Overview

ECR (Ecriture Comptable Recapitulative) is a fixed-width positional text format used to import accounting data.

## Encoding rules

| Rule | Value |
|------|-------|
| Encoding | ANSI (latin-1 / ISO 8859-1) |
| Line endings | `\r\n` (Windows) |
| Alpha fields | Left-aligned, space-padded to the right |
| Num fields | Right-aligned, zero-padded to the left |
| Date fields | Format `jjmmaaaa` (day-month-year), left-aligned |

Each line starts with a **6-character type code** identifying the record type.

## Hierarchy

```
VER  (required, exactly 1, first line)
└── DOS  (accounting folder)
    └── EXO  (fiscal year)
        ├── CPT  (chart of accounts, optional)
        │   ├── TIERS   (third party, optional)
        │   └── ANACPT  (analytical account, optional)
        ├── TVA  (VAT codes, optional)
        ├── JOU  (journals, optional)
        └── ECR  (journal entry)
            └── MVT  (movement / entry detail)
                ├── ANAMVT  (analytical movement, optional)
                └── ECHMVT  (payment schedule, optional)
```

## Record types

### VER — File header

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type ("VER") |
| 7 | 7 | Num | Yes | Minimum ISACOMPTA version |
| 14 | 4 | Num | Yes | Required zone |
| 18 | 1 | Num | No | Delete entries flag |
| 19 | 30 | Alpha | No | File label |
| 49 | 1 | Num | No | ANSI/ASCII type |

### DOS — Accounting folder

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type ("DOS") |
| 7 | 8 | Alpha | Yes | Folder number |
| 15 | 30 | Alpha | Yes | Folder label |
| 45 | 8 | Date | No | Last closing date |
| 53-58 | various | Num | No | Update flags |
| 59 | 2 | Num | No | Account size |

### EXO — Fiscal year

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type ("EXO") |
| 7 | 8 | Date | Yes | Start date |
| 15 | 8 | Date | Yes | End date |
| 36 | 3 | Alpha | No | Currency |

### CPT — Chart of accounts (54 fields)

Key fields:

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type ("CPT") |
| 7 | 10 | Alpha | Yes | Account number |
| 17 | 30 | Alpha | Yes | Label |
| 87 | 2 | Alpha | No | Account type |
| 119 | 2 | Alpha | No | VAT code |

### ECR — Journal entry (37 fields)

Key fields:

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type ("ECR") |
| 7 | 2 | Alpha | Yes | Journal code |
| 9 | 8 | Date | Yes | Entry date |
| 25 | 30 | Alpha | Yes | Entry label |
| 82 | 9 | Num | No | Entry code |

### MVT — Movement (40 fields)

Key fields:

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type ("MVT") |
| 7 | 10 | Alpha | Yes | Account |
| 17 | 30 | Alpha | No | Movement label |
| 47 | 13 | Num | No | Debit amount |
| 60 | 13 | Num | No | Credit amount |

### ECHMVT — Payment schedule (13 fields)

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type |
| 7 | 13 | Num | Yes | Total amount (TTC) |
| 30 | 8 | Date | Yes | Due date |

### JOU — Journal (15 fields)

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type |
| 7 | 2 | Alpha | Yes | Journal code |
| 9 | 30 | Alpha | Yes | Journal label |

### TVA — VAT code (20 fields)

| Position | Length | Type | Required | Description |
|----------|--------|------|----------|-------------|
| 1 | 6 | Alpha | Yes | Record type |
| 7 | 2 | Alpha | Yes | VAT code |
| 9 | 30 | Alpha | Yes | Label |
| 39 | 10 | Alpha | Yes | VAT account |
| 49 | 5 | Num | Yes | Rate |

For the complete field listing of all record types, refer to the `ecrstudio/structures.py` source file which contains the full ECR specification.
