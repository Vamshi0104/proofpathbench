# ProofPath interactive demo

A dependency-free, GitHub Pages-ready demonstration of the core ProofPathBench idea:
a successful mutation response is not the same thing as evidence that the requested state
was reached.

## What the demo shows

- Eight representative stateful domains from the benchmark.
- A direct plan that trusts the mutation response.
- A verified plan that checks readback, an operation ledger, or multiple sources.
- Deterministic simulations of normal execution and all nine canonical failure classes.
- A live paired simulation that recomputes immediately when risk, cost, sample
  size, seed, or scenario changes.
- Seeded outcome-distribution bars and live estimates of avoided false completions,
  verification overhead, and cost per avoided unsupported claim.
- A visible separation between tool response, authoritative state, and evaluator verdict.
- A six-dimension evidence comparison: independence, authority, specificity, freshness,
  linkage, and coverage.
- Direct paths to the release PDF, sanitized benchmark artifact, source configuration,
  eventual Zenodo DOI, and BibTeX/CFF citation metadata.

The demo is an explanatory simulator. It does **not** run language models, execute the
Python benchmark, or claim empirical results about any agent.

The interactive controls use the canonical pilot levels: failure risk `0%`, `5%`, or
`20%`, and verification premium `0%`, `10%`, `50%`, or `100%`.

## Run locally

From this directory:

```bash
python3 -m http.server 8000
```

Then open <http://localhost:8000>. Opening `index.html` directly also works because the
demo does not fetch local files or use ES modules.

## Test

The simulation engine has no runtime dependencies and uses Node's built-in test runner:

```bash
npm test
```

## Publish with GitHub Pages

The repository includes `.github/workflows/pages.yml`, which deploys this directory.

1. Push the repository to GitHub with `main` as the default branch.
2. Open **Settings → Pages** in the GitHub repository.
3. Under **Build and deployment**, choose **GitHub Actions** as the source.
4. Push to `main`, or run the workflow manually from the **Actions** tab.

The site will be available at <https://vamshi0104.github.io/proofpathbench/> after the
first successful deployment. Its canonical source is
<https://github.com/Vamshi0104/proofpathbench>.

## Structure

```text
docs/
├── index.html          # Semantic interface and content
├── styles.css          # Responsive visual system
├── data.js             # Curated benchmark scenario projection
├── engine.js           # Pure deterministic simulation logic
├── app.js              # DOM rendering and interaction layer
├── favicon.svg         # Site-specific icon
├── og-image.png        # 1200 × 630 social preview
├── site-config.js      # Verified repository URL and future Zenodo/arXiv identifiers
├── release-meta.js     # Generated test-count metadata
├── downloads/          # Release-generated paper, artifact, and citation files
├── package.json        # Local serve and test commands
└── tests/
    └── engine.test.cjs # Core behavioral tests
```

## Design choices

- **No build step:** fewer moving parts and a transparent deployment artifact.
- **No external assets:** fast, private, and usable offline.
- **Pure simulation engine:** deterministic behavior that can be tested separately from
  the interface.
- **Fair paired computation:** direct and verified plans receive the same seeded failure
  schedule, so their difference comes from evidence handling rather than random draws.
- **Progressive semantics:** native buttons, labels, tables, keyboard interaction,
  responsive layout, reduced-motion support, and visible focus styles.
- **Honest scope:** benchmark facts are distinguished from illustrative demo output.

## Extending the demo

Add scenarios to `data.js` using the existing compact shape. If you add a new evidence
mechanism, define its display name in `mechanisms` and update the visibility rule in
`engine.js`. Add a regression test for every new failure behavior.

The canonical benchmark manifests remain in `../benchmark/scenarios/`; the demo keeps a
small hand-curated projection so the published site stays simple and standalone.
Run `make release` from the repository root after changing the paper or artifact; the
release script refreshes everything under `downloads/` from canonical sources.

After Zenodo assigns the release DOI, set the bare DOI once in `site-config.js` as
`zenodoDoi`. The site then exposes the DOI link and adds it to the generated BibTeX.
