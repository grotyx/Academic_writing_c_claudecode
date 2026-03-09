#!/usr/bin/env python3
"""
PubMed Search & Evidence Registry Tool

Searches PubMed via NCBI E-utilities (no API key required, no external deps).

Usage:
    python search_pubmed.py search "query terms" [--max 20] [--sort relevance]
    python search_pubmed.py fetch 12345678 [12345679 ...]
    python search_pubmed.py doi 10.1234/xxxxx
    python search_pubmed.py related 12345678 [--max 10]

Output modes:
    --format table    : Summary table (default for search)
    --format evidence : evidence.md formatted entries (default for fetch/doi)
    --format json     : Raw JSON output
"""

import sys
import json
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
import argparse
import re
import time

BASE_URL = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
ID_CONVERTER_URL = "https://www.ncbi.nlm.nih.gov/pmc/utils/idconv/v1.0/"
RATE_LIMIT_DELAY = 0.34  # NCBI requests max 3/sec without API key


# ─── API Functions ───────────────────────────────────────────────

def search_pubmed(query, max_results=20, sort="relevance"):
    """Search PubMed, return (pmids, total_count)."""
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "term": query,
        "retmax": max_results,
        "retmode": "json",
        "sort": sort,
    })
    url = f"{BASE_URL}/esearch.fcgi?{params}"
    data = _fetch_json(url)
    result = data.get("esearchresult", {})
    return result.get("idlist", []), int(result.get("count", 0))


def fetch_articles(pmids):
    """Fetch detailed metadata for given PMIDs."""
    if not pmids:
        return []
    params = urllib.parse.urlencode({
        "db": "pubmed",
        "id": ",".join(pmids),
        "retmode": "xml",
    })
    url = f"{BASE_URL}/efetch.fcgi?{params}"
    xml_data = _fetch_bytes(url)
    root = ET.fromstring(xml_data)
    return [_parse_article(elem) for elem in root.findall(".//PubmedArticle")]


def find_related(pmid, max_results=10):
    """Find related articles for a given PMID."""
    params = urllib.parse.urlencode({
        "dbfrom": "pubmed",
        "db": "pubmed",
        "id": pmid,
        "linkname": "pubmed_pubmed",
        "retmode": "json",
        "retmax": max_results,
    })
    url = f"{BASE_URL}/elink.fcgi?{params}"
    data = _fetch_json(url)
    linksets = data.get("linksets", [])
    if linksets:
        links = linksets[0].get("linksetdbs", [])
        if links:
            link_list = links[0].get("links", [])[:max_results]
            return [str(lid) if isinstance(lid, str) else str(lid.get("id", "")) for lid in link_list]
    return []


def doi_to_pmid(doi):
    """Convert DOI to PMID."""
    # Try NCBI ID converter first
    params = urllib.parse.urlencode({"ids": doi, "format": "json"})
    try:
        data = _fetch_json(f"{ID_CONVERTER_URL}?{params}")
        records = data.get("records", [])
        if records and records[0].get("pmid"):
            return records[0]["pmid"]
    except Exception:
        pass
    # Fallback: search PubMed with DOI
    pmids, _ = search_pubmed(f'"{doi}"[DOI]', max_results=1)
    return pmids[0] if pmids else None


# ─── XML Parsing ─────────────────────────────────────────────────

def _parse_article(elem):
    """Parse PubmedArticle XML element into dict."""
    a = {}

    # PMID
    a["pmid"] = _findtext(elem, ".//PMID")

    # Title
    title_elem = elem.find(".//ArticleTitle")
    a["title"] = _itertext(title_elem)

    # Authors
    authors = []
    for au in elem.findall(".//Author"):
        ln = au.findtext("LastName", "")
        ini = au.findtext("Initials", "")
        if ln:
            authors.append(f"{ln} {ini}".strip())
    a["authors"] = authors
    a["first_author"] = authors[0].split()[0] if authors else "Unknown"

    # Journal
    ji = elem.find(".//Journal/JournalIssue")
    a["journal"] = _findtext(elem, ".//Journal/Title")
    a["journal_abbr"] = _findtext(elem, ".//Journal/ISOAbbreviation")
    a["volume"] = _findtext(ji, "Volume") if ji is not None else ""
    a["issue"] = _findtext(ji, "Issue") if ji is not None else ""

    # Year
    pub_date = ji.find("PubDate") if ji is not None else None
    if pub_date is not None:
        year = pub_date.findtext("Year", "")
        if not year:
            md = pub_date.findtext("MedlineDate", "")
            m = re.search(r"(\d{4})", md) if md else None
            year = m.group(1) if m else ""
        a["year"] = year
    else:
        a["year"] = ""

    # Pages
    a["pages"] = _findtext(elem, ".//MedlinePgn")

    # DOI
    doi_elem = elem.find(".//ArticleId[@IdType='doi']")
    if doi_elem is None:
        doi_elem = elem.find(".//ELocationID[@EIdType='doi']")
    a["doi"] = doi_elem.text.strip() if doi_elem is not None and doi_elem.text else ""

    # PMC ID
    pmc_elem = elem.find(".//ArticleId[@IdType='pmc']")
    a["pmc"] = pmc_elem.text.strip() if pmc_elem is not None and pmc_elem.text else ""

    # Abstract
    parts = []
    for ab in elem.findall(".//AbstractText"):
        label = ab.get("Label", "")
        text = _itertext(ab)
        parts.append(f"**{label}:** {text}" if label else text)
    a["abstract"] = "\n".join(parts)

    # Publication types
    a["pub_types"] = [pt.text for pt in elem.findall(".//PublicationType") if pt.text]

    # MeSH terms
    a["mesh"] = [m.text for m in elem.findall(".//MeshHeading/DescriptorName") if m.text]

    return a


# ─── Formatting ──────────────────────────────────────────────────

def format_table(articles):
    """Format articles as a readable table."""
    lines = []
    lines.append(f"{'#':<4} {'PMID':<12} {'Year':<6} {'First Author':<16} {'Journal':<24} Title")
    lines.append("-" * 120)
    for i, a in enumerate(articles, 1):
        title = a["title"][:60] + ("..." if len(a["title"]) > 60 else "")
        journal = (a["journal_abbr"] or a["journal"])[:22]
        lines.append(
            f"{i:<4} {a['pmid']:<12} {a['year']:<6} {a['first_author']:<16} {journal:<24} {title}"
        )
    return "\n".join(lines)


def format_citation(a):
    """Format full citation string."""
    authors = a.get("authors", [])
    if len(authors) > 6:
        author_str = ", ".join(authors[:6]) + ", et al."
    elif len(authors) > 1:
        author_str = ", ".join(authors[:-1]) + ", " + authors[-1]
    else:
        author_str = authors[0] if authors else "Unknown"

    parts = [f"{author_str}. {a['title'].rstrip('.')}"]
    journal = a.get("journal_abbr") or a.get("journal", "")
    if journal:
        parts.append(f" {journal}. {a['year']}")
        if a.get("volume"):
            parts.append(f";{a['volume']}")
        if a.get("issue"):
            parts.append(f"({a['issue']})")
        if a.get("pages"):
            parts.append(f":{a['pages']}")
        parts.append(".")
    return "".join(parts)


def guess_study_design(pub_types):
    """Guess study design from publication types."""
    pt = " ".join(pub_types).lower()
    if "randomized" in pt or "clinical trial, phase" in pt:
        return "RCT"
    if "meta-analysis" in pt:
        return "Meta-analysis"
    if "systematic review" in pt:
        return "Systematic Review"
    if "review" in pt:
        return "Review"
    if "case reports" in pt:
        return "Case Report"
    if "comparative study" in pt:
        return "Comparative Study"
    if "cohort" in pt:
        return "Cohort Study"
    return "[TODO - study type, n=?, follow-up period]"


def format_evidence_entry(a, ref_num):
    """Format article as evidence.md entry."""
    fa = a["first_author"].lower()
    year = a["year"]
    citation = format_citation(a)
    design = guess_study_design(a.get("pub_types", []))

    entry = f"""### [{ref_num}] {a['first_author']} et al., {year}
- **Citation:** {citation}
- **DOI:** {a.get('doi', '')}
- **PMID:** {a.get('pmid', '')}
- **PDF:** knowledge/pdf/{fa}_{year}_KEYWORD.pdf

- **Study Design:** {design}
- **Objective:** [TODO]
- **Population:** [TODO]
- **Intervention/Method:** [TODO]

- **Main Findings:**
  - [TODO]

- **Key Points:**
  - [TODO]

- **Limitations:** [TODO]
- **Relevance:** [TODO]"""

    abstract = a.get("abstract", "")
    if abstract:
        entry += f"\n\n<!-- Abstract:\n{abstract}\n-->"

    return entry


def format_evidence_batch(articles, start_num=1):
    """Format multiple articles as evidence.md entries."""
    entries = []
    for i, a in enumerate(articles):
        entries.append(format_evidence_entry(a, start_num + i))
    return "\n\n---\n\n".join(entries)


# ─── Helpers ─────────────────────────────────────────────────────

def _fetch_json(url):
    with urllib.request.urlopen(url) as resp:
        return json.loads(resp.read())


def _fetch_bytes(url):
    with urllib.request.urlopen(url) as resp:
        return resp.read()


def _findtext(elem, path, default=""):
    if elem is None:
        return default
    found = elem.findtext(path, default)
    return found.strip() if found else default


def _itertext(elem):
    if elem is None:
        return ""
    return "".join(elem.itertext()).strip()


# ─── CLI ─────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="PubMed Search & Evidence Registry Tool",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s search "endoscopic spine surgery outcomes"
  %(prog)s search "ACDF vs arthroplasty" --max 10 --sort pub_date
  %(prog)s fetch 35486828 33264437
  %(prog)s doi 10.1016/j.spinee.2023.01.005
  %(prog)s related 35486828 --max 5
        """,
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # search
    p_search = sub.add_parser("search", help="Search PubMed")
    p_search.add_argument("query", help="Search query")
    p_search.add_argument("--max", type=int, default=20, help="Max results (default: 20)")
    p_search.add_argument("--sort", default="relevance",
                          choices=["relevance", "pub_date", "author", "journal_name"],
                          help="Sort order")
    p_search.add_argument("--format", dest="fmt", default="table",
                          choices=["table", "evidence", "json"],
                          help="Output format")
    p_search.add_argument("--start-num", type=int, default=1,
                          help="Starting reference number for evidence format")

    # fetch
    p_fetch = sub.add_parser("fetch", help="Fetch articles by PMID")
    p_fetch.add_argument("pmids", nargs="+", help="PubMed IDs")
    p_fetch.add_argument("--format", dest="fmt", default="evidence",
                          choices=["table", "evidence", "json"])
    p_fetch.add_argument("--start-num", type=int, default=1,
                          help="Starting reference number")

    # doi
    p_doi = sub.add_parser("doi", help="Import article by DOI")
    p_doi.add_argument("dois", nargs="+", help="DOI(s)")
    p_doi.add_argument("--format", dest="fmt", default="evidence",
                          choices=["table", "evidence", "json"])
    p_doi.add_argument("--start-num", type=int, default=1,
                          help="Starting reference number")

    # related
    p_rel = sub.add_parser("related", help="Find related articles")
    p_rel.add_argument("pmid", help="Source PMID")
    p_rel.add_argument("--max", type=int, default=10, help="Max results")
    p_rel.add_argument("--format", dest="fmt", default="table",
                          choices=["table", "evidence", "json"])
    p_rel.add_argument("--start-num", type=int, default=1,
                          help="Starting reference number")

    args = parser.parse_args()

    try:
        if args.command == "search":
            pmids, total = search_pubmed(args.query, args.max, args.sort)
            if not pmids:
                print(f"No results found for: {args.query}", file=sys.stderr)
                sys.exit(1)
            print(f"Found {total} total results, showing {len(pmids)}:\n", file=sys.stderr)
            time.sleep(RATE_LIMIT_DELAY)
            articles = fetch_articles(pmids)
            _output(articles, args.fmt, args.start_num)

        elif args.command == "fetch":
            articles = fetch_articles(args.pmids)
            if not articles:
                print("No articles found for given PMIDs.", file=sys.stderr)
                sys.exit(1)
            _output(articles, args.fmt, args.start_num)

        elif args.command == "doi":
            pmids = []
            for doi in args.dois:
                pmid = doi_to_pmid(doi)
                if pmid:
                    pmids.append(pmid)
                    print(f"DOI {doi} -> PMID {pmid}", file=sys.stderr)
                else:
                    print(f"Could not resolve DOI: {doi}", file=sys.stderr)
                time.sleep(RATE_LIMIT_DELAY)
            if not pmids:
                sys.exit(1)
            articles = fetch_articles(pmids)
            _output(articles, args.fmt, args.start_num)

        elif args.command == "related":
            related_pmids = find_related(args.pmid, args.max)
            if not related_pmids:
                print(f"No related articles found for PMID: {args.pmid}", file=sys.stderr)
                sys.exit(1)
            print(f"Found {len(related_pmids)} related articles:\n", file=sys.stderr)
            time.sleep(RATE_LIMIT_DELAY)
            articles = fetch_articles(related_pmids)
            _output(articles, args.fmt, args.start_num)

    except urllib.error.URLError as e:
        print(f"Network error: {e}", file=sys.stderr)
        sys.exit(1)
    except ET.ParseError as e:
        print(f"XML parse error: {e}", file=sys.stderr)
        sys.exit(1)


def _output(articles, fmt, start_num):
    if fmt == "json":
        print(json.dumps(articles, indent=2, ensure_ascii=False))
    elif fmt == "evidence":
        print(format_evidence_batch(articles, start_num))
    else:
        print(format_table(articles))


if __name__ == "__main__":
    main()
