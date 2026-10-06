# ProofPathBench Zenodo release

ProofPathBench is a deterministic benchmark for a narrow reliability question: when a
tool-using language agent can choose between matched plans, does it select the plan that
produces stronger independent evidence that the requested external-state change occurred?

## Release scope

This frozen `v0.0.1` release contains the approved research paper, machine-readable
deposit and citation metadata, and a self-contained benchmark artifact. The benchmark
contains:

**Author:** Vamshi Krishna Madhavan, Independent Researcher  
**Contact:** <vamshi-madhavan@outlook.com>

- 96 synthetic scenarios across 8 domains;
- 384 task-treatment units;
- 768 deterministic no-fault plan executions; and
- 9 seeded failure classes.

No provider model was behaviorally evaluated in this release. Fixtures, deterministic
mock executions, and prospective power simulations are not empirical language-model
results. The included human-review materials are a blinded human construct-validation
protocol; the review has not been run, and the benchmark is not described as
human-validated.

## Files

- `PAPER.pdf` - the scientifically approved manuscript from the final research audit.
- `artifact/proofpathbench-artifact-v0.0.1.tar.gz` - frozen reproducibility artifact.
- `metadata.json` - Zenodo deposit metadata for a research preprint.
- `CITATION.cff` - software citation metadata with a publication-style preferred citation.
- `validation/manifest.json` - machine-derived release facts and file digests.
- `validation/RELEASE_VALIDATION.md` - results of the release and fresh-extraction checks.
- `CHECKSUMS.sha256` - deterministic SHA-256 list for the important release files.

## Public architecture

Zenodo is the permanent, citable frozen research release and eventual DOI authority.
GitHub is the canonical development/source repository. GitHub Pages is the interactive
explanatory website. A possible future arXiv deposit is prepared and preserved separately;
this Zenodo tree neither replaces nor modifies it.

The verified public source repository is
<https://github.com/Vamshi0104/proofpathbench>, and the project website is
<https://vamshi0104.github.io/proofpathbench/>. The release DOI is
<https://doi.org/10.5281/zenodo.23196925>. No arXiv identifier is invented here.

## Validate

From the repository root, rebuild and validate the complete release:

```bash
python3 zenodo/scripts/build_zenodo_release.py
```

Or validate an existing build without regenerating it:

```bash
python3 zenodo/scripts/validate_zenodo_release.py
```

The validator checks digests, counts, archive cleanliness, obvious secret/privacy
patterns, metadata, citation metadata, extraction, documented benchmark validation,
the 48-test Python suite, the prospective power output, and generated paper assets.

## Citation and DOI

The release DOI is recorded in `CITATION.cff`, deposit metadata, and the website's central
configuration. Follow `ZENODO_UPLOAD_GUIDE.md` when changing identifiers, and do not create
a second Zenodo record for the same version merely to obtain another DOI.

## Licenses

The software and benchmark artifact use Apache-2.0, as declared by the canonical
repository `LICENSE`. The repository does not currently declare a separate manuscript
content license. The author must confirm the intended paper/content license in the Zenodo
deposit; this release does not silently apply Apache-2.0 or CC BY 4.0 to the manuscript.
