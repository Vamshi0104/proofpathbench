# Public-source similarity audit

**Date:** 2026-09-28  
**Scope:** the 18 Markdown files present in the repository at Gate 1.  
**Conclusion:** no evidence of copied long-form prose was found in this limited audit. This is not a Turnitin/iThenticate certificate and does not establish a literal 0% similarity score.

## Checks performed

### 1. Comparison with the supplied master prompt

- Markdown files checked: 18.
- Repository long sentences compared against long sentences in the supplied prompt using normalized character-sequence similarity.
- Threshold: similarity ratio at least 0.72 for passages of at least 10 words.
- Matches: **0**.
- Exact normalized eight-word sequences in repository prose: 7,755.
- Exact eight-word sequences also present in the prompt: **8 (0.10%)**.

The eight overlapping windows reduce to three expected items:

1. the user-specified `python -m proofpath ...` command sequence;
2. “do current tool using language agents preferentially select,” inherited from the requested RQ1;
3. “a verifiability aware planner will reduce false completion,” inherited from the example hypothesis.

These should be treated as user-provided project requirements, not as evidence that the generated explanatory prose was copied. If the material is published, the final human authors should nevertheless rewrite and own the phrasing of research questions and hypotheses.

### 2. Public-web exact-phrase spot checks

Distinctive phrases from the novelty criteria, benchmark definition, and pilot controls were searched in quotation marks, including:

- “behavioral benchmark of verification demand”;
- “The unit of analysis is the plan choice before outcome evidence is observed”;
- “the evidence set of P2 dominates P1”;
- “extra plan steps produce evidence only, not extra mutation capability”;
- “verification demand” with “tool-using agents”;
- “source independence, authority, freshness, specificity” with “agent.”

No relevant public source containing those passages was identified. Search engines may omit, normalize, or fail to index material, so absence from search results is not proof of originality.

### 3. Attribution review

The related-work matrix attributes each summarized method to a named record and links a primary source. One anonymous submission remains marked **UNVERIFIED** and is excluded from the bibliography. Paper titles, author names, venue metadata, technical method names, and short attributed descriptions are expected to match their sources and are not original prose claims.

## Expected similarity that should not be characterized as plagiarism

- paper titles, author names, identifiers, and BibTeX metadata;
- standard technical terms such as “postcondition verification,” “mixed-effects logistic regression,” and “authoritative state”;
- code, command lines, schema keys, configuration values, and mathematical symbols;
- standard license language;
- text explicitly supplied by the project owner and retained as requirements.

## Important limitations

- No access was available to Turnitin, iThenticate/Crossref Similarity Check, private dissertations, paywalled full-text corpora, or institutional student-paper repositories.
- Exact-phrase search does not reliably detect close paraphrase, translated copying, idea plagiarism, or unindexed sources.
- A low similarity score does not validate citations, scientific correctness, or authorship disclosure.
- The repository was generated with AI assistance and must not be represented as entirely human-written.

## Publication recommendation

Before submission, a human author should:

1. read and rewrite every substantive section in their own scholarly voice;
2. verify each related-work summary against the full paper;
3. use the institution's approved similarity service on the final manuscript;
4. inspect every flagged passage manually rather than treating a percentage as a verdict;
5. follow the target venue's AI-assistance disclosure policy.

## Final protocol-manuscript pass

**Date:** 2026-09-29  
**Artifact:** `output/pdf/proofpath_protocol.pdf`, extracted with Poppler.

The normalized manuscript text was compared with the complete supplied master prompt.
Among 3,867 unique manuscript eight-word sequences, the audit found **zero** exact
eight-word overlaps. It also found zero exact ten-word and twelve-word overlaps. A
sentence-level normalized character comparison found zero pairs at or above a 0.72
similarity ratio for sentences containing at least 12 normalized words.

This strengthens the limited evidence that the final protocol prose was not copied from
the supplied prompt. It still does not establish a universal 0% similarity score, detect
all paraphrase or idea reuse, or substitute for a private-corpus service such as
iThenticate or Turnitin. Bibliographic metadata, titles, technical terms, mathematics,
and standard methodological phrases remain expected sources of legitimate similarity.

## Benchmark-manuscript rewrite spot check

**Date:** 2026-10-05  
**Artifact:** revised benchmark manuscript rendered from `paper/arxiv/main.tex`.

After reframing the article as a benchmark-and-validation contribution, eight distinctive
passages from the rewritten abstract, methods, limitations, conclusion, and
reproducibility section were searched as exact quoted phrases on the public web. No
result containing any complete queried passage was found. The bibliography was also
rechecked against primary-source records, and the final build contains no undefined
citations.

This is a public-web spot check, not a plagiarism certificate. Search indexing is
incomplete and does not cover private student-paper databases, subscription similarity
corpora, translated copying, or close paraphrase. The final named author should still run
the submitted PDF through an institutional similarity service and review every match in
context.
