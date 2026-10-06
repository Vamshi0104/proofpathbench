# ProofPathBench

ProofPathBench is an implemented research benchmark for asking whether a tool-using
language agent chooses a plan that produces independent evidence of an external-state
change. It separates the tool-visible response, authoritative state, and evaluator-only
oracle trace so that a reported success is never treated as ground truth.

## Release status

The release contains 96 synthetic scenarios across eight domains, 384 task-treatment
units, 768 deterministic no-fault plan executions, and nine seeded failure classes. All
48 benchmark validation tests pass. The blinded human-validation protocol is prepared but
has not been run. No provider model was evaluated, and this release makes no behavioral
claim about any language model.

The interactive website is an eight-scenario explanatory projection. Its outputs are
local deterministic simulations, not empirical model results.

## What is novel

The benchmark isolates an ex-ante choice between matched plans before either plan runs.
The plans pursue the same goal and differ in the evidence path and its disclosed simulated
cost/latency. This distinguishes willingness to obtain outcome evidence from post-failure
detection, recovery, general tool capability, or a safeguard imposed by the runtime.

## Contents

- `benchmark/scenarios/`: 96 typed scenario manifests and their hash index.
- `benchmark/specification.md`: construct, evidence, failure, and outcome semantics.
- `proofpath/`: generator, mock environment, fault injector, evaluator, and analysis code.
- `configs/pilot.yaml`: proposed split-plot evaluation and preregistration gates.
- `research/power_analysis.json`: prospective power simulation, not observed results.
- `research/human_validation/`: fixed blinded protocol and blank reviewer materials.
- `research/citation_audit.md`: source-by-source bibliography verification.
- `research/textual_integrity_audit.md`: bounded public-source similarity review.
- `paper/main.tex`: canonical manuscript source.
- `docs/`: dependency-free static GitHub Pages website and browser simulation.

Private answer keys and raw runs are excluded from the public research archive. Fixture
smoke records are non-empirical and cannot enter confirmatory analysis.

## Validate and reproduce

Use Python 3.11 or newer. Install the pinned project requirements, then run:

```bash
python3 -m pip install -r requirements.txt
python3 -m proofpath.benchmark.validate
python3 -m proofpath.validate_benchmark --config configs/pilot.yaml
python3 -m pytest -q
```

Regenerate the benchmark before validation only when intentionally changing its design:

```bash
python3 -m proofpath.benchmark.generate
```

Regenerate the committed figures and tables:

```bash
python3 paper/build_assets.py
```

Build the PDF when `latexmk` and a LaTeX distribution are available:

```bash
make draft
```

Build and extract-test the deterministic research archive:

```bash
make artifact
```

## Run and deploy the website

```bash
cd docs
python3 -m http.server 8000
```

Open `http://localhost:8000`. Run `npm test` in `docs/` for the browser-engine suite.
The site has no runtime dependencies, analytics, cookies, backend, or external service.
The GitHub Pages workflow publishes the self-contained `docs/` directory after release
checks pass. See `docs/README.md` for setup and `docs/site-config.js` for the public
repository URL and eventual arXiv identifier. The canonical public source repository is
<https://github.com/Vamshi0104/proofpathbench>, and the project website is
<https://vamshi0104.github.io/proofpathbench/>.

The downloadable research archive intentionally contains research code, manuscript
source, tests, protocols, and validation records rather than the GitHub Pages deployment
directory. Website files are available in the public repository.

## Cite

No arXiv identifier is fabricated in this release. Until one is assigned, use:

```bibtex
@misc{madhavan2026proofpathbench,
  author = {Vamshi Krishna Madhavan},
  title = {ProofPathBench: A Benchmark for Verifiability-Aware Planning by Tool-Using Language Agents},
  year = {2026},
  note = {Version 0.0.1; benchmark software and manuscript; source: https://github.com/Vamshi0104/proofpathbench}
}
```

Machine-readable metadata is in `CITATION.cff`.
The frozen Zenodo release is available at <https://doi.org/10.5281/zenodo.23196925>.

## Author

Vamshi Krishna Madhavan — Independent Researcher  
Contact: <vamshi-madhavan@outlook.com>

## License

ProofPathBench is released under the Apache License 2.0; see `LICENSE`.
