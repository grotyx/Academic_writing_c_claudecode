---
description: Search PubMed and register results in evidence.md
args: query
---

# PubMed Search & Evidence Registration

Search query: **$ARGUMENTS**

## Instructions

You have a Python script at `scripts/search_pubmed.py` that queries the NCBI E-utilities API directly (no MCP or API key needed).

### Step 1: Check current evidence.md

1. Read `knowledge/evidence.md` to find:
   - The next available reference number (check existing `### [N]` entries)
   - Already registered PMIDs (to avoid duplicates)
   - Previous search queries in the Search Log (to avoid redundant searches)

### Step 2: Search PubMed

Run the search script:
```bash
python3 scripts/search_pubmed.py search "$ARGUMENTS" --max 20
```

Show the results table to the user.

### Step 3: User Selection

Ask the user which articles to register. Options:
- Specific numbers: "1, 3, 5"
- Range: "1-5"
- All: "all"
- None: "none" (refine search)

### Step 4: Fetch & Register

For selected articles, run:
```bash
python3 scripts/search_pubmed.py fetch <PMID1> <PMID2> ... --format evidence --start-num <next_ref_num>
```

Then:
1. Review the generated evidence entries
2. Fill in [TODO] fields using the abstract (included as HTML comment)
   - **Study Design**: Extract from abstract (type, sample size, follow-up)
   - **Objective**: Extract from abstract
   - **Population**: Extract from abstract
   - **Intervention/Method**: Extract from abstract
   - **Main Findings**: Extract key results with specific numbers
   - **Key Points**: Relate to the current research topic
   - **Limitations**: Extract from abstract or note if not mentioned
   - **Relevance**: Suggest which manuscript section to use in (Introduction/Discussion/Methods)
3. Update the PDF filename's KEYWORD placeholder with an appropriate keyword
4. Append completed entries to `knowledge/evidence.md` (before "## Pending References")
5. Update the Search Log table with today's date, query, result count, and registered entries

### Alternative Commands

The script also supports:
- **Import by DOI**: `python3 scripts/search_pubmed.py doi <DOI>`
- **Import by PMID**: `python3 scripts/search_pubmed.py fetch <PMID>`
- **Find related articles**: `python3 scripts/search_pubmed.py related <PMID> --max 10`

### Important Rules

- **NEVER fabricate references** - only register what PubMed returns
- **Check for duplicates** before registering (match by PMID)
- **Fill [TODO] fields from abstract** - do not invent information not in the abstract
- **If no abstract available**, leave [TODO] and note "No abstract - needs manual review"
- Follow `docs/evidence_guide.md` formatting rules

Execute now with the provided query.
