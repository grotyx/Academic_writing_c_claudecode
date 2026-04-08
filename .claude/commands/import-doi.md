---
description: Import article by DOI and register in evidence.md
args: doi
---

# Import Article by DOI

DOI: **$ARGUMENTS**

## Instructions

### Step 1: Check evidence.md

Read `knowledge/evidence.md` to find the next reference number and check if this DOI is already registered.

### Step 2: Fetch Article

```bash
python3 scripts/search_pubmed.py doi $ARGUMENTS --format evidence --start-num <next_ref_num>
```

### Step 3: Complete & Register

1. Fill all [TODO] fields using the abstract
2. Update the PDF filename KEYWORD
3. Append to `knowledge/evidence.md` (before "## Pending References")
4. Update the Search Log: `| date | DOI: $ARGUMENTS | PubMed | 1건 | [N] registered |`

Follow `docs/evidence_guide.md` formatting rules. Never fabricate information.
