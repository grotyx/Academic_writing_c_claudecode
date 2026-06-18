# Author Response Markdown Template

> Copy this file to `drafts/revision/REV1/response_letter_REV1.md`.
> It is designed for `scripts/compile_response_docx.py`.

Use blank lines between blocks. Do not use tables, bullet lists, heading styles,
colored text, or manual indentation. Keep `[CHANGE]` blocks in the working
Markdown for ghost-revision verification; the DOCX compiler removes them by
default.

```markdown
# Point-by-point responses to reviewer comments

Reviewer #1:

[Paste the reviewer's general comment exactly as written.]

Comment 1) [Paste the reviewer comment exactly as written.]

[CHANGE]
comment_id: R1-C1
claim: [brief description of the manuscript change]
section: [section file, e.g. 04_methods]
expected_terms: [terms that should appear in the manuscript diff]
[/CHANGE]

Response: We thank the reviewer for this comment. [Answer in prose: appreciation, position, evidence or rationale, and action taken.]

Location: Page X, Line Y

Revised text:
"[Quote the revised manuscript text exactly as it appears in the revised manuscript.]"

Comment 2) [Paste the reviewer comment exactly as written.]

Response: We thank the reviewer for this helpful suggestion. [Response text.]

Location: [Section or page/line]

Revised text:
"[Revised manuscript text.]"

Reviewer closing:
We thank Reviewer #1 for reviewing the manuscript. We genuinely appreciate their constructive remarks and thank them for taking the time to review our article. We hope that the revised manuscript will meet their expectations.

Reviewer #2:

Comment 1) [Paste the reviewer comment exactly as written.]

Response: [Response text.]
```

DOCX formatting applied by the compiler:

| Markdown block | DOCX formatting |
|---|---|
| Title line beginning with `#` | Bold |
| `Reviewer #N:` | Bold |
| Reviewer comments and `Comment N)` paragraphs | Regular |
| `Response:` paragraph | Bold |
| `Location:` value | Bold, without the `Location:` label |
| Text after `Revised text:` | Bold, without the `Revised text:` label |
| `Reviewer closing:` value | Bold, without the `Reviewer closing:` label |
| `[CHANGE]` blocks | Removed by default |

Compile command:

```powershell
py scripts\check_revision_claims.py drafts\revision\REV1\response_letter_REV1.md --strict
```

If this prints `GATE PASS`, generate the DOCX:

```powershell
py scripts\compile_response_docx.py drafts\revision\REV1\response_letter_REV1.md
```

The default output is `output/revision/REV1/response_letter_REV1_YYMMDD.docx`
when the input is under `drafts/revision/REV1/`.
