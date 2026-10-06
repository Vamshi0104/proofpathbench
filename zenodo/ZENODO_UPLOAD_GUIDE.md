# Zenodo upload guide

This release uses one manually deposited Zenodo record per ProofPathBench version. Do not
also enable automatic GitHub-Zenodo archiving for the same release unless the author has
deliberately chosen a separate-record strategy; doing both can create confusing duplicate
records and DOIs.

## Before upload

1. Run `python3 zenodo/scripts/build_zenodo_release.py` from the repository root.
2. Read `validation/RELEASE_VALIDATION.md` and `FINAL_ZENODO_READINESS.md`.
3. Read the exact `PAPER.pdf` and confirm the author name, contact information, AI-use
   disclosure, claims, and limitations.
4. Confirm the paper/content license. The software artifact is Apache-2.0; no separate
   manuscript license is currently declared. If the author chooses CC BY 4.0 for the
   paper, record that explicit decision before publication and configure the mixed
   licenses accurately in Zenodo.
5. Run an institutional similarity service on the exact final PDF if one is available,
   and manually review every match. The repository audit is not a Turnitin/iThenticate
   certificate and supplies no plagiarism percentage.

## Create and describe the record

1. Sign in to Zenodo, open the plus menu, and choose **New upload**.
2. Upload `PAPER.pdf` and `artifact/proofpathbench-artifact-v0.0.1.tar.gz`. The paper is
   the primary research object; the archive is its benchmark/reproducibility companion.
3. For **Resource type**, choose **Publication / Preprint**. This is a research preprint
   and benchmark release, not a peer-reviewed journal or conference article.
4. Enter the title exactly as it appears in `metadata.json` and `PAPER.pdf`.
5. Enter the creator exactly as shown in `metadata.json`: family name `Madhavan`, given
   names `Vamshi Krishna`, affiliation `Independent Researcher`. Do not add an ORCID
   unless the author supplies and verifies it.
6. Paste the description from `metadata.json`, preserving the explicit statement that
   no provider-model behavioral results are reported.
7. Enter version `0.0.1` and publication date `2026-10-06`.
8. Configure rights/licenses accurately. Apply Apache-2.0 to the software/benchmark
   artifact. Add the author-confirmed paper/content license as a separate license or
   rights statement; do not accept Zenodo's default without checking it.
9. Add the curated keywords from `metadata.json`; do not add unrelated search terms.
10. Under **Related works**, add `https://github.com/Vamshi0104/proofpathbench` as the
    related software/source repository and `https://vamshi0104.github.io/proofpathbench/`
    as the project documentation website, matching `metadata.json`. Do not invent an
    arXiv identifier.
11. Leave funding, grants, affiliations, and communities blank unless verified by the
    author.

## DOI, final validation, and publication

12. In **Digital Object Identifier**, answer that the upload does not already have a DOI.
13. If the DOI is needed before publication, choose **Get a DOI now!** in the Zenodo draft.
    Keep the draft: deleting it loses the reservation.
14. Insert the exact DOI returned by Zenodo—never a guessed value—into the local release
    metadata and citation files. Set `zenodoDoi` in `docs/site-config.js` to the bare DOI.
    Add it to the paper only if the author intentionally rebuilds the canonical manuscript;
    the existing approved PDF must not be silently edited.
15. Rerun `python3 zenodo/scripts/build_zenodo_release.py`. Confirm that validation passes
    and that the DOI shown locally is exactly the reserved DOI.
16. Re-upload the final `PAPER.pdf`, artifact archive, and any machine-readable metadata
    files intended for public download.
17. Choose **Preview** and inspect the file list, default PDF preview, title, author order,
    resource type, description, date, version, keywords, licenses, and related identifiers.
18. Verify again that the record does not claim peer review, completed human validation,
    or provider-model results.
19. Choose **Publish** only after the author approves the preview and rights selections.
20. Copy the final DOI from the published record and verify that it resolves to this exact
    release.
21. Update the GitHub README, repository `CITATION.cff`, and GitHub Pages `zenodoDoi`
    configuration with the real DOI; rerun repository and website checks. Use Zenodo's
    versioning feature for a later release instead of creating an unrelated duplicate.

Zenodo's current documentation describes the form labels **New upload**, **Resource
type**, **Digital Object Identifier**, **Get a DOI now!**, **Preview**, and **Publish**.
Form wording can change; if the live form differs, follow the equivalent current field and
recheck the preview before publication.
