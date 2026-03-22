# Spine GraphRAG: A Knowledge Graph-Enhanced Retrieval-Augmented Generation System for Evidence-Based Spine Surgery Literature Synthesis

**Draft Version**: 0.1 (2026-03-17)
**Target Journal**: Journal of Medical Internet Research (JMIR, IF ~7.0)
**Article Type**: Original Research (Systems & Methods)

---

## Abstract

**Background:** The volume of spine surgery literature has grown exponentially, with thousands of publications annually spanning degenerative diseases, deformity, trauma, tumor, and basic science. Clinicians face an increasing burden in synthesizing this evidence to inform surgical decision-making. Existing approaches---including keyword-based database searches, general-purpose retrieval-augmented generation (RAG) systems, and direct large language model (LLM) consultation---each exhibit fundamental limitations: keyword search lacks semantic understanding, vector-only RAG ignores structured medical knowledge, and direct LLM queries produce responses without verifiable evidence sources, risking hallucination.

**Objective:** This study aimed to develop and evaluate Spine GraphRAG, a knowledge graph-enhanced retrieval-augmented generation system that integrates a domain-specific graph database with vector embeddings and evidence-based ranking to support evidence-grounded spine surgery literature synthesis.

**Methods:** We constructed a unified Neo4j knowledge graph containing 638 peer-reviewed spine surgery publications organized into 699 interventions, 475 pathologies, 2,901 outcomes, and 210 anatomy nodes, linked by 22,985 typed relationships. A 735-code SNOMED-CT ontology with hierarchical IS_A relations enabled query expansion across the entity taxonomy. The system employed a three-component hybrid ranking formula combining semantic similarity (weight 0.4), authority scoring based on the Oxford Centre for Evidence-Based Medicine (OCEBM) hierarchy (weight 0.3), and graph relevance derived from ontological distance and relationship connectivity (weight 0.3). We evaluated four baseline systems---keyword search (B1), vector-only RAG (B2), direct LLM consultation (B3), and the full GraphRAG system (B4)---using an end-to-end answer quality framework adapted from RAGAS, comprising faithfulness, citation fidelity, answer relevancy, completeness, hallucination rate, and evidence level metrics. Twenty-nine clinical questions across five spine surgery subdomains were assessed via LLM-as-judge evaluation, with expert validation on a subset of 10--15 questions.

**Results:** [PENDING EXPERIMENT]

**Conclusions:** [PENDING EXPERIMENT -- expected to demonstrate that knowledge graph-enhanced retrieval with evidence-based ranking significantly improves the faithfulness, citation fidelity, and evidence quality of LLM-generated literature syntheses compared with keyword search, vector-only RAG, and direct LLM consultation in the spine surgery domain.]

**Keywords:** knowledge graph; retrieval-augmented generation; spine surgery; evidence-based medicine; natural language processing; SNOMED-CT; Neo4j

---

## 1. Introduction

### 1.1 The Evidence Synthesis Challenge in Spine Surgery

Spine surgery encompasses a broad range of procedures addressing degenerative disease, deformity correction, traumatic injury, tumor management, and fundamental biological questions regarding spinal biomechanics and fusion biology. The field produces thousands of peer-reviewed publications annually, spanning diverse study designs from randomized controlled trials and meta-analyses to case series and expert opinion [1,2]. For the practicing spine surgeon, maintaining current awareness of this evidence base---and synthesizing it to inform patient-specific clinical decisions---represents a substantial cognitive burden.

The challenge is compounded by the multidimensional nature of spine surgical decision-making. A single clinical question (e.g., "What is the evidence comparing transforaminal lumbar interbody fusion [TLIF] versus posterior lumbar interbody fusion [PLIF] for single-level lumbar degenerative disease?") may require integrating evidence across multiple outcome domains---clinical scores, radiographic parameters, complication rates, and cost-effectiveness---drawn from studies of varying methodological quality. Traditional approaches to evidence synthesis, such as systematic reviews, require months of manual effort and become outdated as new evidence accumulates [3].

### 1.2 Limitations of Existing Approaches

Three predominant approaches to automated medical literature retrieval and synthesis exist, each with recognized shortcomings.

First, **keyword-based search** systems such as PubMed rely on Boolean queries matched against indexed metadata fields. Although effective for broad retrieval, these systems lack semantic understanding: they cannot recognize that "unilateral biportal endoscopy" and "UBE" refer to the same intervention, nor can they infer that a study of "minimally invasive lumbar decompression" may be relevant to a query about "endoscopic spinal surgery." Moreover, keyword search provides no mechanism for ranking results by evidence quality or methodological rigor [4].

Second, **vector-based retrieval-augmented generation (RAG)** systems embed both queries and documents into high-dimensional vector spaces and retrieve candidates based on semantic similarity [5,6]. While vector search addresses the synonym problem, it treats all documents as unstructured text, discarding the structured relationships that are fundamental to medical knowledge---the connections between interventions, pathologies, anatomical sites, and clinical outcomes. A pure vector approach cannot traverse an evidence chain from intervention to pathology to outcome, nor can it preferentially surface higher-quality evidence.

Third, **direct LLM consultation**---posing clinical questions directly to large language models such as GPT-4 or Claude without external knowledge retrieval---has gained widespread attention [7--11]. However, this approach presents critical limitations for clinical decision support. Aktan et al. demonstrated that multimodal LLMs achieved near-zero agreement (Cohen's kappa = 0.001--0.036) with expert spine surgeons on Lenke classification, compared with kappa = 0.913 among fellowship-trained specialists [12]. Kartal et al. reported only moderate agreement (kappa = 0.587--0.692) when LLMs were used for minimally invasive spine surgery triage decisions [7]. Fundamentally, direct LLM consultation produces responses without verifiable evidence sources, rendering clinical claims unauditable and exposing users to hallucination risk.

### 1.3 Knowledge Graphs for Medical Literature

Knowledge graphs offer a principled solution to the limitations of unstructured retrieval by representing medical entities and their relationships as typed nodes and edges within a graph database [13,14]. Lotz et al. demonstrated the feasibility of integrating GPT-3 with a knowledge graph for low back pain literature analysis, using similarity graphs to identify biopsychosocial patterns across studies [15]. However, their system was limited to a single pathological domain (low back pain), employed an older language model generation (GPT-3), and lacked formal ontology integration, evidence-level ranking, and multi-hop graph traversal capabilities.

More recently, Wu et al. introduced Medical Graph RAG, which augmented LLM responses with graph-structured medical knowledge across nine question-answering benchmarks [16]. The GraphRAG approach for chronic kidney disease demonstrated clinician-validated improvements in answer quality using combined LLM-as-judge and expert evaluation [17]. Cai et al. proposed LEAP, an LLM-enhanced system for automated phenotyping using ontology mapping, achieving substantial improvements in electronic health record phenotype classification [18]. These studies collectively establish the value of graph-structured knowledge for medical AI, yet none address the specific requirements of surgical literature synthesis: structured intervention comparison, evidence chain traversal across treatment-pathology-outcome relationships, and ontology-based query expansion using standardized medical terminologies.

### 1.4 Study Objective and Contributions

The purpose of this study was to develop and evaluate Spine GraphRAG, a knowledge graph-enhanced retrieval-augmented generation system for evidence-based spine surgery literature synthesis. The system makes four principal contributions:

1. **A unified single-store architecture** combining graph structure and vector embeddings within Neo4j, enabling hybrid queries that simultaneously leverage structured relationships and semantic similarity in a single database transaction.

2. **A three-component evidence-based ranking formula** that integrates semantic relevance, OCEBM evidence hierarchy-derived authority scoring, and graph-based relevance computed from ontological distance and relationship connectivity.

3. **Ontology-driven query expansion** using a 735-code SNOMED-CT mapping with hierarchical IS_A relations, enabling the system to automatically broaden searches from specific interventions to related procedures within the same taxonomic family.

4. **Evidence chain traversal** across typed graph relationships (Intervention --TREATS--> Pathology --AFFECTS--> Outcome), supporting automated surgical intervention comparison and multi-hop reasoning over the literature.

We hypothesized that Spine GraphRAG would achieve superior faithfulness, citation fidelity, and evidence quality compared with keyword search, vector-only RAG, and direct LLM consultation across clinical questions spanning all five spine surgery subdomains.

---

## 2. Methods

### 2.1 System Architecture Overview

Spine GraphRAG employs a single-store architecture in which Neo4j serves as the unified repository for both graph-structured relationships and vector embeddings (Figure 1). This design eliminates the synchronization overhead inherent in dual-store architectures that maintain separate graph and vector databases [19]. The system comprises four processing stages: (1) document ingestion via PDF parsing and LLM-based metadata extraction, (2) knowledge graph construction with entity normalization and relationship building, (3) hybrid retrieval combining graph traversal, vector similarity search, and ontology-based query expansion, and (4) evidence-based ranking and answer generation.

The technology stack consists of Neo4j 5.x (graph database with native HNSW vector index), Claude Haiku 4.5 (metadata extraction and answer generation), OpenAI text-embedding-3-large (3,072-dimensional embeddings), and a Python 3.10+ orchestration layer.

### 2.2 Document Ingestion and Metadata Extraction

#### 2.2.1 PDF Processing Pipeline

Source documents were ingested through a unified PDF processor that extracted raw text using PyMuPDF and segmented documents into semantically coherent chunks using a configurable text chunking strategy. Each document was processed through the following pipeline:

1. **Text extraction**: PDF pages were parsed with PyMuPDF, preserving section headers, tables, and figure captions where possible.
2. **LLM-based metadata extraction**: The full text was submitted to Claude Haiku 4.5 (temperature = 0.1) with a structured prompt requesting extraction of a SpineMetadata schema comprising: title, authors, journal, year, DOI, PMID, study design, evidence level (OCEBM classification), spine subdomain, sample size, follow-up duration, primary and secondary outcomes, interventions, pathologies, anatomical regions, key findings, main conclusion, and limitations.
3. **Text chunking**: Documents were segmented into overlapping chunks (default: 512 tokens with 64-token overlap) for granular vector retrieval.
4. **Embedding generation**: Each chunk and each paper-level abstract received a 3,072-dimensional embedding via OpenAI's text-embedding-3-large model.

#### 2.2.2 PubMed Enrichment

Bibliographic metadata was automatically enriched via the NCBI Entrez API, retrieving structured fields including MeSH terms, publication types, author affiliations, and citation counts. When PMID was unavailable, DOI-based and citation-matching fallbacks were employed. Concurrent processing (configurable up to 10 simultaneous requests) enabled efficient batch enrichment of large document collections.

### 2.3 Knowledge Graph Schema

The graph schema (Figure 2) was designed to capture the essential entities and relationships of spine surgery literature. Six core node types were defined:

**Core Nodes:**

| Node Type | Description | Count |
|-----------|-------------|-------|
| Paper | Individual publication with full bibliographic metadata, evidence level, and study design | 638 |
| Chunk | Text segment with vector embedding for semantic retrieval | 9,869 |
| Intervention | Surgical procedure or treatment modality (e.g., TLIF, laminectomy, UBE) | 699 |
| Pathology | Disease or condition (e.g., lumbar spinal stenosis, spondylolisthesis) | 475 |
| Outcome | Clinical outcome measure (e.g., VAS, ODI, fusion rate, complication rate) | 2,901 |
| Anatomy | Anatomical region (e.g., L4-L5, cervical spine, thoracolumbar junction) | 210 |

**Core Relationships:**

| Relationship | Source --> Target | Properties | Count |
|-------------|-----------------|------------|-------|
| TREATS | Intervention --> Pathology | — | 3,982 |
| AFFECTS | Intervention --> Outcome | direction, p_value, effect_size, confidence_interval | 13,527 |
| INVESTIGATES | Paper --> Intervention | — | 2,380 |
| IS_A | Entity --> Parent Entity | — | 3,096 |
| HAS_CHUNK | Paper --> Chunk | chunk_index, start_offset | 9,869 |
| LOCATED_AT | Pathology --> Anatomy | — | * |
| STUDIES | Paper --> Pathology | — | * |

*Counts marked with asterisk were not independently tallied.

Additional relationship types supported paper-to-paper connections (CITES, SUPPORTS, CONTRADICTS, EXTENDS) and extended entity relationships (CAUSES, HAS_RISK_FACTOR, PREDICTS, CORRELATES, USES_DEVICE).

### 2.4 Entity Normalization

Raw entity names extracted by the LLM exhibited substantial variation (e.g., "TLIF," "transforaminal lumbar interbody fusion," "Trans-foraminal LIF"). A two-stage normalization pipeline resolved these to canonical forms:

1. **Alias-based normalization**: A curated mapping of over 280 synonym variations across four entity types (interventions, pathologies, outcomes, anatomy) was applied via case-insensitive matching. This mapping resolved common abbreviations (UBE to biportal endoscopic spine surgery), regional naming conventions, and typographic variants.

2. **SNOMED-CT code assignment**: Each normalized entity was linked to a SNOMED-CT concept code from a domain-specific mapping of 735 codes (235 interventions, 231 pathologies, 200 outcomes, 69 anatomy terms). This mapping was manually curated by a fellowship-trained spine surgeon and constitutes the largest published SNOMED-CT mapping specific to spine surgery.

Entity normalization was critical for preventing duplicate nodes (e.g., "pedicle subtraction osteotomy" and "PSO" as separate entities) and enabling ontology-based query expansion.

### 2.5 IS_A Ontology and Query Expansion

Each SNOMED-CT-mapped entity was assigned a parent code establishing its position within a hierarchical taxonomy. For example:

```
Biportal Endoscopic Spine Surgery (BESS)
  IS_A → Endoscopic Spine Surgery
    IS_A → Minimally Invasive Spine Surgery
      IS_A → Spine Surgery (root)
```

This IS_A hierarchy was constructed for all four entity types (interventions, pathologies, outcomes, anatomy) with depths ranging from 1 to 5 levels. The hierarchy enabled ontology-driven query expansion: when a user queried for "endoscopic spine surgery," the system automatically expanded the search to include all child entities (UBE, uniportal endoscopy, percutaneous endoscopic lumbar discectomy, etc.) via Cypher graph traversal:

```cypher
MATCH (target:Intervention {name: $query_entity})
OPTIONAL MATCH (child)-[:IS_A*1..3]->(target)
WITH collect(child.name) + [target.name] AS expanded_entities
...
```

The expansion depth was configurable (default: 3 hops) and could be disabled for queries requiring exact-match precision.

### 2.6 Hybrid Search Architecture

Query processing followed a three-stage pipeline:

**Stage 1: Query Analysis.** The input natural language query was parsed to identify mentioned entities (interventions, pathologies, outcomes, anatomical regions) and query intent (single-intervention evidence, intervention comparison, complication analysis, or anatomical indication).

**Stage 2: Parallel Retrieval.** Three retrieval pathways executed concurrently:

- **Graph traversal**: Cypher queries matched identified entities against the knowledge graph, traversing TREATS, AFFECTS, INVESTIGATES, and IS_A relationships to identify relevant papers and their evidence chains. The graph traversal module supported multi-hop evidence chain extraction:

  ```
  Intervention -[TREATS]-> Pathology -[AFFECTS]-> Outcome
  ```

  For intervention comparison queries, the system identified shared and unique outcomes between two interventions for a given pathology, enabling structured head-to-head comparisons.

- **Vector similarity search**: The query was embedded using the same text-embedding-3-large model and searched against the Neo4j HNSW vector index over paper abstracts and text chunks. The HNSW index was configured with M = 16, efConstruction = 200, and ef = 100, using cosine similarity.

- **Ontology expansion**: IS_A relationships were traversed to expand the initial entity set, and expanded entities were used to augment both graph traversal and vector search result sets.

**Stage 3: Result Fusion.** Results from all retrieval pathways were merged by paper identifier, with each paper receiving scores from all applicable pathways.

### 2.7 Evidence-Based Ranking

The final ranking score for each retrieved paper was computed using a three-component weighted formula:

$$S_{final} = w_s \cdot S_{semantic} + w_a \cdot S_{authority} + w_g \cdot S_{graph}$$

where $w_s = 0.4$, $w_a = 0.3$, $w_g = 0.3$.

#### 2.7.1 Semantic Score ($S_{semantic}$)

The cosine similarity between the query embedding and the paper abstract embedding (both 3,072-dimensional, text-embedding-3-large):

$$S_{semantic} = \cos(\mathbf{q}, \mathbf{d}) = \frac{\mathbf{q} \cdot \mathbf{d}}{||\mathbf{q}|| \cdot ||\mathbf{d}||}$$

#### 2.7.2 Authority Score ($S_{authority}$)

The authority score integrated four sub-components reflecting the methodological strength of each paper:

$$S_{authority} = W_{evidence} \times W_{design} \times B_{recency} \times B_{sample} \times B_{citation}$$

where:

- **Evidence level weight** ($W_{evidence}$): Based on the OCEBM hierarchy, assigning weights from 1.0 (Level 1a: systematic review/meta-analysis) through 0.9 (Level 1b: RCT), 0.8 (Level 2a: cohort), 0.7 (Level 2b: case-control), 0.5 (Level 3: case series), 0.3 (Level 4: expert opinion), to 0.1 (Level 5: unknown/not applicable).

- **Study design weight** ($W_{design}$): Derived from MeSH publication types, ranging from 1.0 (meta-analysis, systematic review) through 0.9 (RCT) to 0.4 (case report).

- **Recency boost** ($B_{recency}$): A multiplier favoring recent publications: 1.2 (published within 2 years), 1.1 (3--5 years), 1.0 (6--10 years), 0.9 (>10 years).

- **Sample size boost** ($B_{sample}$): Logarithmic scaling from 1.0 (n < 10) to 1.3 (n >= 1,000).

- **Citation boost** ($B_{citation}$): Logarithmic scaling from 1.0 (<5 citations) to 1.3 (>=100 citations).

#### 2.7.3 Graph Relevance Score ($S_{graph}$)

The graph relevance score captured the structural proximity between query entities and each candidate paper within the knowledge graph:

$$S_{graph} = S_{ontology} + B_{relationship}$$

where:

- **Ontology distance score** ($S_{ontology}$): Based on the number of IS_A hops between the query entity and the matched entity: 1.0 (direct match, 0 hops), 0.7 (1 hop), 0.4 (2 hops), 0.2 (3+ hops).

- **Relationship bonus** ($B_{relationship}$): A fixed bonus of 0.3 awarded when a direct TREATS or AFFECTS relationship existed between the paper's investigated intervention and the query pathology or outcome.

Additional boost multipliers were applied for papers reporting key findings ($\times 1.2$), statistically significant results ($\times 1.1$), and improved outcome directions ($\times 1.2$).

### 2.8 Evidence Chain Traversal

For intervention comparison queries, the graph traversal search module constructed explicit evidence chains by traversing the knowledge graph:

```python
@dataclass
class EvidenceChainLink:
    source_node: str       # e.g., "TLIF"
    relationship: str      # e.g., "TREATS"
    target_node: str       # e.g., "Lumbar Spinal Stenosis"
    properties: dict       # e.g., {p_value: 0.023, effect_size: 0.45}

@dataclass
class InterventionComparison:
    intervention1: str
    intervention2: str
    pathology: str
    shared_outcomes: list[dict]     # Outcomes measured by both
    int1_only_outcomes: list[dict]  # Outcomes unique to intervention1
    int2_only_outcomes: list[dict]  # Outcomes unique to intervention2
    comparison_summary: str
```

The system identified papers investigating each intervention for the specified pathology, extracted their outcome measures and statistical properties from AFFECTS relationships, and produced a structured comparison of shared and unique outcomes with associated evidence levels.

### 2.9 Answer Generation

Retrieved and ranked papers were passed to Claude Haiku 4.5 as context for answer generation. The prompt instructed the model to:

1. Synthesize findings from the provided papers only (no external knowledge).
2. Cite each claim with the corresponding paper identifier (PMID or title).
3. Organize the response by outcome domain when multiple outcomes were relevant.
4. Indicate the evidence level of each cited study.
5. Acknowledge limitations and gaps in the available evidence.

This constrained generation approach ensured that all claims in the generated answer were traceable to specific papers within the knowledge graph.

### 2.10 Evaluation Design

#### 2.10.1 Baseline Systems

Four baseline configurations were compared:

| Baseline | Method | Rationale |
|----------|--------|-----------|
| B1: Keyword | Neo4j fulltext index only | Analogous to PubMed keyword search |
| B2: Vector-only (RAG) | Embedding similarity only (semantic = 1.0, authority = 0, graph = 0) | Standard RAG without graph structure |
| B3: LLM Direct | Claude Haiku 4.5 queried directly without knowledge graph | Equivalent to Kartal 2025, Najjar 2025 approach |
| B4: GraphRAG | Full system: 3-way ranking (0.4 / 0.3 / 0.3) + IS_A expansion | Proposed system |

Baselines B1, B2, and B4 used the same underlying Neo4j database of 638 papers. Baseline B3 relied solely on the LLM's parametric knowledge.

#### 2.10.2 Clinical Question Set

Twenty-nine clinical questions were developed spanning five spine surgery subdomains: degenerative (n = 10), deformity (n = 5), trauma (n = 5), tumor (n = 4), and basic science (n = 5). Questions were categorized into five types:

| Type | Description | Proportion |
|------|-------------|------------|
| T1: Single-intervention evidence | Evidence for a specific procedure | 25% |
| T2: Intervention comparison | Head-to-head treatment comparison | 30% |
| T3: Complication/prognosis | Risk factors and outcomes after surgery | 20% |
| T4: Anatomical indication | Best approach for a specific anatomical scenario | 15% |
| T5: Current evidence level | State of evidence for emerging techniques | 10% |

Example questions included: "What is the evidence comparing CDR versus ACDF for 2-level cervical disc disease?" (T2), "What are the risk factors for cage subsidence after MIS-TLIF?" (T3), and "What is the evidence for robotic-assisted spine surgery from recent RCTs?" (T5).

#### 2.10.3 Evaluation Metrics

We adopted an end-to-end answer quality evaluation framework inspired by RAGAS [20] and recent medical GraphRAG evaluation methodologies [16,17]. For each question, each baseline system produced a complete answer, which was then evaluated on six metrics:

**Phase A: Automated Evaluation (LLM-as-Judge)**

| Metric | Definition | Scale |
|--------|-----------|-------|
| Faithfulness | Proportion of claims in the answer that are supported by cited sources | 0.0--1.0 |
| Citation Fidelity | Proportion of cited papers that actually support the claims attributed to them | 0.0--1.0 |
| Answer Relevancy | Degree to which the answer addresses the clinical question | 0.0--1.0 |
| Completeness | Coverage of important clinical aspects relevant to the question | 0.0--1.0 |
| Hallucination Rate | Proportion of cited references that do not exist in the knowledge base (verified by automatic PMID lookup) | 0--100% |
| Evidence Level | Mean OCEBM evidence level of cited papers (lower = higher quality) | 1--7 |

For faithfulness and citation fidelity assessment, the LLM judge decomposed each answer into individual claims, identified the cited source for each claim, and verified whether the source's abstract or extracted metadata supported the claim. This claim-level decomposition followed the methodology described in RAGAS [20].

**Phase B: Expert Validation**

A subset of 10--15 questions was evaluated by fellowship-trained spine surgeons using three 5-point Likert scale metrics: clinical correctness, completeness, and clinical usefulness. Expert evaluators were blinded to which baseline system generated each answer.

#### 2.10.4 Ablation Studies

To quantify the contribution of individual system components, we conducted five ablation experiments:

| Ablation | Modification |
|----------|-------------|
| A1: No authority scoring | Set $w_a = 0$, redistribute to semantic ($w_s = 0.7$, $w_g = 0.3$) |
| A2: No graph relevance | Set $w_g = 0$, redistribute to semantic ($w_s = 0.7$, $w_a = 0.3$) |
| A3: No IS_A expansion | Disable ontology-based query expansion |
| A4: No evidence weighting | Set all evidence level weights to 1.0 (uniform) |
| A5: No recency/citation boost | Set all boost multipliers to 1.0 |

#### 2.10.5 Statistical Analysis

For Phase A metrics, mean scores and 95% confidence intervals were computed across the 29-question evaluation set for each baseline. Pairwise comparisons between B4 and each alternative baseline were conducted using paired Wilcoxon signed-rank tests with Bonferroni correction for multiple comparisons. Effect sizes were reported as rank-biserial correlations. For Phase B expert evaluation, inter-rater agreement was assessed using intraclass correlation coefficients (ICC, two-way random, absolute agreement). Between-system comparisons used the Wilcoxon signed-rank test on paired Likert ratings.

### 2.11 Dataset Characteristics

The knowledge graph was constructed from 638 peer-reviewed spine surgery publications with the following subdomain distribution:

| Subdomain | Papers | Proportion |
|-----------|--------|------------|
| Degenerative | 384 | 60.2% |
| Deformity | 91 | 14.3% |
| Basic Science | 55 | 8.6% |
| Tumor | 44 | 6.9% |
| Trauma | 29 | 4.5% |
| Other/Mixed | 35 | 5.5% |

The evidence level distribution of included papers reflected the typical composition of the spine surgery literature: Level 2b -- case-control studies (n = 273, 42.8%), Level 4 -- expert opinion (n = 138, 21.6%), Level 5 -- unknown (n = 68, 10.7%), Level 1a -- systematic review/meta-analysis (n = 67, 10.5%), Level 3 -- case series (n = 33, 5.2%), Level 1b -- RCT (n = 27, 4.2%), and Level 2a -- cohort (n = 27, 4.2%). Notably, 61.7% of papers had evidence levels of 2b or higher, indicating a substantial proportion of comparative evidence suitable for synthesis.

---

## 3. Results

### 3.1 System Performance

[PENDING EXPERIMENT]

*Expected content: Processing time benchmarks for document ingestion, query response latency, and graph construction throughput.*

### 3.2 End-to-End Answer Quality Comparison

[PENDING EXPERIMENT]

**Table 2. End-to-End Answer Quality: Four Baselines Across Six Metrics (n = 29 Questions)**

| Metric | B1: Keyword | B2: Vector RAG | B3: LLM Direct | B4: GraphRAG | *p* (B4 vs B2) | *p* (B4 vs B3) |
|--------|-------------|----------------|-----------------|--------------|-----------------|-----------------|
| Faithfulness | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Citation Fidelity | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Answer Relevancy | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Completeness | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Hallucination Rate (%) | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| Evidence Level (mean) | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

*Values presented as mean (95% CI). Lower evidence level values indicate higher-quality evidence. Pairwise comparisons by Wilcoxon signed-rank test with Bonferroni correction.*

### 3.3 Hallucination Analysis

[PENDING EXPERIMENT]

**Table 3. Hallucination Analysis: B3 (LLM Direct) vs B4 (GraphRAG)**

| Category | B3: LLM Direct | B4: GraphRAG |
|----------|-----------------|--------------|
| Total citations generated | [PENDING] | [PENDING] |
| Valid citations (PMID verified) | [PENDING] | [PENDING] |
| Fabricated references | [PENDING] | [PENDING] |
| Hallucination rate (%) | [PENDING] | [PENDING] |
| Unsupported factual claims | [PENDING] | [PENDING] |

*Expected finding: B4 hallucination rate near 0% (all citations from knowledge graph), B3 hallucination rate > 15%.*

### 3.4 Evidence Level Comparison

[PENDING EXPERIMENT]

**Figure 5. Distribution of Evidence Levels Among Cited Papers by Baseline System**

*Expected finding: B4 preferentially cites Level 1--2 evidence due to OCEBM-based authority weighting, whereas B1 and B2 show no evidence-level preference.*

### 3.5 Ablation Studies

[PENDING EXPERIMENT]

**Table 4. Ablation Study Results: Effect of Removing Individual Components**

| Configuration | Faithfulness | Citation Fidelity | Completeness | Evidence Level |
|--------------|-------------|-------------------|-------------|----------------|
| B4 (full system) | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| A1: No authority | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| A2: No graph relevance | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| A3: No IS_A expansion | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| A4: No evidence weighting | [PENDING] | [PENDING] | [PENDING] | [PENDING] |
| A5: No recency/citation boost | [PENDING] | [PENDING] | [PENDING] | [PENDING] |

*Expected finding: Removing authority scoring (A1) most degrades evidence level; removing IS_A expansion (A3) most degrades completeness.*

### 3.6 IS_A Ontology Expansion Effect

[PENDING EXPERIMENT]

**Table 5. IS_A Expansion ON vs OFF: Impact on Retrieval Breadth and Answer Quality**

| Metric | IS_A ON | IS_A OFF | Difference |
|--------|---------|----------|------------|
| Unique papers retrieved (mean) | [PENDING] | [PENDING] | [PENDING] |
| Unique interventions covered (mean) | [PENDING] | [PENDING] | [PENDING] |
| Completeness score | [PENDING] | [PENDING] | [PENDING] |
| Answer Relevancy score | [PENDING] | [PENDING] | [PENDING] |

### 3.7 Expert Validation

[PENDING EXPERIMENT]

**Table 6. Expert Evaluation: B3 (LLM Direct) vs B4 (GraphRAG) on 10--15 Clinical Questions**

| Metric (5-point Likert) | B3: LLM Direct | B4: GraphRAG | *p* |
|-------------------------|-----------------|--------------|-----|
| Clinical Correctness | [PENDING] | [PENDING] | [PENDING] |
| Completeness | [PENDING] | [PENDING] | [PENDING] |
| Clinical Usefulness | [PENDING] | [PENDING] | [PENDING] |

*Evaluated by [N] fellowship-trained spine surgeons, blinded to system identity. ICC for inter-rater agreement: [PENDING].*

### 3.8 Qualitative Case Example

[PENDING EXPERIMENT]

**Figure 6. Side-by-side comparison of B3 (LLM Direct) vs B4 (GraphRAG) responses to the question: "What is the evidence comparing TLIF versus PLIF for single-level lumbar degenerative spondylolisthesis?"**

*Expected to illustrate: B3 provides plausible but unverifiable claims with potential hallucinated references; B4 provides evidence-grounded synthesis with verified citations, evidence levels, and structured outcome comparison.*

---

## 4. Discussion

### 4.1 Principal Findings

[PENDING EXPERIMENT -- the following discussion will be revised based on actual results]

This study presents Spine GraphRAG, a knowledge graph-enhanced retrieval-augmented generation system designed for evidence-based spine surgery literature synthesis. The system integrates three retrieval modalities---semantic vector search, graph-structured relationship traversal, and SNOMED-CT ontology-based query expansion---within a single Neo4j database, applying an evidence-aware three-component ranking formula to prioritize methodologically rigorous evidence.

The principal technical contribution of this work lies in the unified architecture that treats graph structure and vector embeddings as complementary rather than competing retrieval paradigms. By encoding the relationships between interventions, pathologies, and outcomes as typed graph edges---and augmenting these with IS_A ontological hierarchies---the system enables retrieval capabilities that are fundamentally unavailable to either keyword-based or vector-only approaches: multi-hop evidence chain traversal, structured intervention comparison, and ontology-driven search expansion.

### 4.2 Comparison with Prior Work

The most directly comparable prior work is that of Lotz et al. [15], who combined GPT-3 with a knowledge graph for low back pain literature analysis. Spine GraphRAG extends this approach in several substantive ways. First, our system covers the full breadth of spine surgery subdomains (degenerative, deformity, trauma, tumor, and basic science) rather than a single pathological condition. Second, the incorporation of a 735-code SNOMED-CT ontology with hierarchical IS_A relations enables systematic query expansion---a capability absent from the Lotz system. Third, our evidence-based ranking formula explicitly weights methodological quality using the OCEBM hierarchy, whereas Lotz et al. relied solely on semantic similarity for result ordering. Fourth, the single-store Neo4j architecture avoids the complexity of maintaining separate databases for graph and vector operations.

Relative to the Medical Graph RAG system of Wu et al. [16], our work is distinguished by domain specificity. Wu et al. evaluated their system on general medical question-answering benchmarks (e.g., MedQA, PubMedQA), whereas Spine GraphRAG targets the specific clinical workflow of spine surgical decision-making, with domain-specific entity types, a curated ontology, and evaluation questions designed by spine surgery specialists.

The direct LLM consultation approach, represented by our B3 baseline and analogous to the methods of Kartal et al. [7], Najjar et al. [8], and Chan et al. [10], lacks the evidence traceability that knowledge graph-grounded retrieval provides. The poor inter-rater agreement reported by Aktan et al. [12] for LLM-based Lenke classification (kappa = 0.001--0.036) underscores the limitations of relying on LLM parametric knowledge alone for specialized surgical tasks. Our system addresses this limitation by constraining answer generation to evidence retrieved from a curated knowledge graph, ensuring that every clinical claim is traceable to a specific publication.

The LEAP system of Cai et al. [18] shares our commitment to ontology-based entity mapping but targets a different application (EHR phenotyping rather than literature synthesis). The ontology mapping methodology---using LLM-assisted matching followed by manual curation---is conceptually similar to our SNOMED-CT mapping workflow, suggesting that this hybrid approach may generalize across medical informatics applications.

### 4.3 The Value of Evidence-Based Ranking

A distinguishing feature of Spine GraphRAG is the integration of evidence quality into the retrieval ranking, which addresses a limitation shared by all prior RAG systems for medical literature. Standard RAG approaches rank documents by semantic similarity alone, treating a large meta-analysis and a single case report with equal weight if both discuss the query topic. Our three-component formula explicitly rewards higher-quality evidence through the authority score, which incorporates OCEBM evidence level weighting, study design assessment, sample size scaling, publication recency, and citation impact.

The OCEBM evidence level weights ($W_{evidence}$) range from 1.0 for Level 1a (systematic reviews and meta-analyses) to 0.1 for Level 5 (unknown or not applicable), creating a ten-fold scoring differential between the highest and lowest quality evidence. This weighting ensures that, for a given level of semantic relevance, a well-designed RCT will consistently rank above a case report, aligning the system's behavior with the principles of evidence-based medicine.

### 4.4 Clinical Implications

The ability to rapidly synthesize evidence across a curated knowledge graph has several practical implications for spine surgery practice. First, the system enables evidence-grounded responses to clinical questions within seconds, compared with the hours or days required for traditional literature review. Second, by providing explicit evidence chains (Intervention --TREATS--> Pathology --AFFECTS--> Outcome) with associated evidence levels, the system supports transparent clinical reasoning---users can inspect the source publications and assess the quality of supporting evidence independently.

Third, the intervention comparison capability addresses a particularly common clinical workflow: deciding between two surgical approaches for a specific pathology (e.g., TLIF versus PLIF for lumbar spondylolisthesis). By automatically identifying shared and unique outcomes across interventions, the system provides a structured comparison that would otherwise require manual cross-referencing of multiple publications.

Fourth, the ontology-driven query expansion reduces the risk of missing relevant evidence due to terminology variation. A query for "minimally invasive decompression" automatically retrieves evidence for UBE, microendoscopic discectomy, tubular retractor-assisted decompression, and other procedures classified under the same IS_A hierarchy, without requiring the user to enumerate these synonyms.

### 4.5 Limitations

This study has several limitations that should be acknowledged. First, the knowledge graph was constructed from 638 publications, which, while sufficient for system evaluation, represents a fraction of the total spine surgery literature. The subdomain distribution was uneven, with degenerative disease (60.2%) substantially overrepresented relative to trauma (4.5%) and tumor (6.9%). This imbalance may affect system performance for underrepresented subdomains, and future work should target a more balanced corpus.

Second, the LLM-based metadata extraction pipeline, while efficient, is imperfect. Entity extraction accuracy was not formally evaluated in this study, and extraction errors may propagate into the knowledge graph as incorrect or missing relationships. The entity normalization pipeline mitigates some of these errors but cannot fully compensate for upstream extraction failures.

Third, the evaluation relied primarily on LLM-as-judge assessment, which, despite growing adoption in the medical AI evaluation literature [16,17,21], may exhibit systematic biases. We mitigated this limitation through expert validation on a question subset, but the small number of expert evaluators limits the generalizability of Phase B results.

Fourth, the current system is limited to English-language publications and does not incorporate non-English literature or clinical guidelines published in other languages. The entity normalization module supports Korean-English synonym mapping for selected terms, but systematic multilingual support remains a direction for future development.

Fifth, the 735-code SNOMED-CT mapping, while the largest published for spine surgery, does not cover all possible terminology. Approximately [PENDING]% of LLM-extracted entities lacked SNOMED-CT codes, limiting ontology-based expansion for these terms. An LLM-based SNOMED proposer module has been developed to suggest mappings for unmapped terms, but its accuracy requires further validation.

Sixth, the evaluation question set of 29 questions, while spanning all five subdomains and five question types, is relatively small. A larger question set would provide greater statistical power for detecting performance differences between baselines, particularly for subgroup analyses by subdomain or question type.

### 4.6 Future Work

Several directions for future development are planned. First, the SNOMED-CT ontology and evaluation framework will be described in dedicated publications (Papers 2 and 6 in our research program). Second, the evidence chain traversal capability will be evaluated against published systematic reviews to assess whether automated evidence synthesis achieves clinically acceptable agreement with expert-conducted reviews (Paper 3). Third, a clinical decision support validation study with IRB approval will assess system utility in realistic clinical scenarios with fellowship-trained spine surgeons (Paper 4). Fourth, the knowledge graph will be expanded to include a broader and more balanced corpus, targeting at least 1,000 publications with improved subdomain coverage. Fifth, integration of real-time PubMed monitoring to automatically incorporate newly published evidence into the knowledge graph is under development.

---

## 5. Conclusions

[PENDING EXPERIMENT -- the following will be revised based on actual results]

Spine GraphRAG demonstrates a novel approach to medical literature synthesis that integrates knowledge graph structure, vector embeddings, and evidence-based ranking within a single-store Neo4j architecture. The system's three-component hybrid ranking formula, SNOMED-CT ontology-driven query expansion, and evidence chain traversal capabilities address fundamental limitations of keyword search, vector-only RAG, and direct LLM consultation for spine surgery evidence synthesis. This work establishes the architectural foundation for domain-specific knowledge graph-enhanced retrieval systems in surgical specialties.

---

## Figures and Tables

### Figure 1. Spine GraphRAG System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Document Ingestion                        │
│  PDF/Text ──→ PyMuPDF ──→ Claude Haiku 4.5 ──→ SpineMetadata│
│                              │                               │
│                    Entity Normalization                       │
│              (280+ aliases, 735 SNOMED-CT codes)             │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Neo4j Unified Store                             │
│  ┌─────────────────┐  ┌──────────────────────────────────┐  │
│  │  Graph Layer     │  │  Vector Layer                     │  │
│  │  • 638 Papers    │  │  • HNSW Index (3072d)             │  │
│  │  • 4,285 Entities│  │  • text-embedding-3-large         │  │
│  │  • 22,985 Rels   │  │  • 9,869 chunk embeddings         │  │
│  │  • 3,096 IS_A    │  │  • 638 abstract embeddings        │  │
│  └─────────────────┘  └──────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ▼
┌─────────────────────────────────────────────────────────────┐
│              Hybrid Retrieval + Ranking                      │
│                                                              │
│  Query ──→ ┌─ Graph Traversal (TREATS, AFFECTS, IS_A)       │
│            ├─ Vector Similarity (HNSW cosine search)         │
│            └─ Ontology Expansion (IS_A hierarchy)            │
│                         │                                    │
│                         ▼                                    │
│  S_final = 0.4·S_semantic + 0.3·S_authority + 0.3·S_graph   │
│                         │                                    │
│                         ▼                                    │
│  Ranked Results ──→ Claude Haiku 4.5 ──→ Evidence-Grounded   │
│                                          Answer with         │
│                                          Citations           │
└─────────────────────────────────────────────────────────────┘
```

*Figure 1. Overview of the Spine GraphRAG system architecture. Documents are processed through an LLM-based extraction pipeline, normalized using domain-specific alias mappings and SNOMED-CT codes, and stored in a unified Neo4j database containing both graph structure and vector embeddings. At query time, three retrieval pathways execute in parallel, and results are ranked using a three-component formula integrating semantic similarity, evidence-based authority, and graph structural relevance.*

### Figure 2. Knowledge Graph Schema

*[To be created as a professional diagram showing node types (Paper, Intervention, Pathology, Outcome, Anatomy, Chunk) and relationship types (TREATS, AFFECTS, INVESTIGATES, IS_A, HAS_CHUNK, LOCATED_AT, STUDIES) with example instances.]*

### Figure 3. Radar Chart: Baseline Comparison

*[PENDING EXPERIMENT -- Radar chart showing 4 baselines x 6 metrics]*

### Figure 4. Ablation Study Results

*[PENDING EXPERIMENT -- Bar chart showing metric changes when each component is removed]*

### Figure 5. Evidence Level Distribution by Baseline

*[PENDING EXPERIMENT -- Box plot showing OCEBM level distribution of cited papers per baseline]*

### Figure 6. Case Comparison: B3 vs B4

*[PENDING EXPERIMENT -- Side-by-side answer comparison]*

### Table 1. Dataset Characteristics

| Characteristic | Value |
|---------------|-------|
| Total papers | 638 |
| Total text chunks | 9,869 |
| Intervention nodes | 699 |
| Pathology nodes | 475 |
| Outcome nodes | 2,901 |
| Anatomy nodes | 210 |
| TREATS relationships | 3,982 |
| AFFECTS relationships | 13,527 |
| IS_A relationships | 3,096 |
| INVESTIGATES relationships | 2,380 |
| SNOMED-CT mappings | 735 (I:235, P:231, O:200, A:69) |
| Embedding dimensions | 3,072 (text-embedding-3-large) |
| Clinical questions | 29 (5 subdomains, 5 types) |

---

## References

1. Fehlings MG, Tetreault L, Nater A, et al. The aging of the global population: the changing epidemiology of disease and spinal disorders. *Neurosurgery*. 2015;77(Suppl 4):S1-S5.

2. Buser Z, Brodke DS, Youssef JA, et al. Synthetic bone graft versus autograft or allograft for spinal fusion: a systematic review. *J Neurosurg Spine*. 2016;25(4):509-516.

3. Borah R, Brown AW, Capers PL, Kaiser KA. Analysis of the time and workers needed to conduct systematic reviews of medical interventions using data from the PROSPERO registry. *BMJ Open*. 2017;7(2):e012545.

4. Falagas ME, Pitsouni EI, Malietzis GA, Pappas G. Comparison of PubMed, Scopus, Web of Science, and Google Scholar: strengths and weaknesses. *FASEB J*. 2008;22(2):338-342.

5. Lewis P, Perez E, Piktus A, et al. Retrieval-augmented generation for knowledge-intensive NLP tasks. *Advances in Neural Information Processing Systems*. 2020;33:9459-9474.

6. Gao Y, Xiong Y, Gao X, et al. Retrieval-augmented generation for large language models: a survey. *arXiv preprint arXiv:2312.10997*. 2023.

7. Kartal I, et al. Performance of large language models in minimally invasive spine surgery triage decisions. *Spine*. 2025. [Exact citation to be verified]

8. Najjar A, et al. ChatGPT versus multidisciplinary team in cauda equina syndrome surgical decision-making. *Spine*. 2025. [Exact citation to be verified]

9. Tuncer O, et al. Comparison of multiple AI models for spinal neurosurgical and physiotherapy decision-making. 2026. [Exact citation to be verified]

10. Chan A, et al. LLM-assisted SINS calculation for spinal metastasis. *Spine*. 2025. [Exact citation to be verified]

11. Prasad SS, et al. LLM assessment of imaging appropriateness in back pain. 2025. [Exact citation to be verified]

12. Aktan A, et al. Reliability of multimodal LLMs in Lenke classification of adolescent idiopathic scoliosis. *Spine*. 2025. [Exact citation to be verified]

13. Hogan A, Blomqvist E, Cochez M, et al. Knowledge graphs. *ACM Computing Surveys*. 2021;54(4):1-37.

14. Chandak P, Huang K, Zitnik M. Building a knowledge graph to enable precision medicine. *Sci Data*. 2023;10(1):67.

15. Lotz JC, et al. Knowledge-organizing technologies for evidence-based back pain research. *JOR Spine*. 2023. [Exact citation to be verified]

16. Wu L, et al. Medical Graph RAG: towards safe medical large language model via graph retrieval-augmented generation. *Proceedings of the 63rd Annual Meeting of the Association for Computational Linguistics (ACL)*. 2025.

17. [Authors]. GraphRAG for chronic kidney disease: clinician and LLM-as-Judge evaluation. *medRxiv preprint*. 2025.

18. Cai T, et al. LEAP: LLM-enhanced automated phenotyping using HPO ontology mapping. *J Am Med Inform Assoc*. 2026. [Exact citation to be verified]

19. Robinson I, Webber J, Eifrem E. *Graph Databases: New Opportunities for Connected Data*. 2nd ed. O'Reilly Media; 2015.

20. Es S, James J, Espinosa-Anke L, Schockaert S. RAGAS: automated evaluation of retrieval augmented generation. *arXiv preprint arXiv:2309.15217*. 2023.

21. Zheng L, Chiang WL, Sheng Y, et al. Judging LLM-as-a-Judge with MT-Bench and Chatbot Arena. *Advances in Neural Information Processing Systems*. 2023;36.

22. Khalsa AS, et al. AI-assisted literature synthesis for surgical site infection risk calculation in spine surgery. *Spine*. 2026. [Exact citation to be verified]

23. Mani S, et al. Multimodal NLP approaches for perioperative safety in spine surgery. 2025. [Exact citation to be verified]

24. Kanani S, et al. LLM-based extraction of compression fracture data from radiology reports. 2025. [Exact citation to be verified]

25. Park SH, et al. LLM classification of tumor treatment response from spine MRI reports. 2025. [Exact citation to be verified]

26. Muthu S, et al. AI and machine learning in cervical myelopathy: a scoping review. 2026. [Exact citation to be verified]

27. Pan A, et al. AI-simplified operative reports for patient comprehension. 2025. [Exact citation to be verified]

---

## Supplementary Materials

*Planned supplementary content:*

- **Supplement 1**: Complete list of 29 clinical evaluation questions with subdomain and type classifications.
- **Supplement 2**: SNOMED-CT mapping statistics and IS_A hierarchy depth distribution.
- **Supplement 3**: Full ablation study results across all metrics.
- **Supplement 4**: Example evidence chains for 5 representative queries.
- **Supplement 5**: LLM-as-judge prompt templates for each evaluation metric.

---

## Author Contributions

**SMP**: Conceptualization, system design and implementation, knowledge graph construction, SNOMED-CT ontology curation, evaluation framework design, data analysis, manuscript drafting. **[Co-authors to be added]**: [Contributions to be specified].

## Funding

[To be specified]

## Conflicts of Interest

[To be specified]

## Data Availability

The evaluation question set, SNOMED-CT mapping, and evaluation code will be made publicly available upon publication. The full knowledge graph database cannot be shared due to copyright restrictions on the underlying publications, but the graph schema, ontology, and system code will be released as open-source software.

---

*End of Draft v0.1*
