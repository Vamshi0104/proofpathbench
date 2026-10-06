# Zenodo release validation

**Release:** v0.0.1  
**Validator:** `zenodo/scripts/validate_zenodo_release.py`

| Check | Status | Evidence |
|---|---|---|
| Approved paper | PASS | `PAPER.pdf` is non-empty, parses as PDF, and is byte-identical to the final audited release PDF. |
| Metadata | PASS | JSON parses as a publication/preprint, contains the verified source/project URLs, and contains the configured Zenodo DOI `10.5281/zenodo.23196925`. |
| Citation metadata | PASS | CFF 1.2.0 parses and contains the matching DOI `10.5281/zenodo.23196925`. |
| Scientific counts | PASS | 96 scenarios, 8 domains, 384 units, 768 executions, and 9 failure classes match canonical reports. |
| Checksums | PASS | All listed SHA-256 values match. |
| Archive structure | PASS | Single safe archive root; required reproducibility files are present. |
| Archive cleanliness | PASS | No macOS metadata, AppleDouble entries, caches, VCS data, hidden files, or prohibited development output. |
| Secret/privacy scan | PASS | No obvious credential, private-key, authorization-header, local-path, or private/internal-URL pattern was found in distributed text. |
| Fresh extraction | PASS | Archive extracted in a new temporary directory; references and structure were checked. |
| Python tests | PASS (48/48) | Documented benchmark validation and the extracted suite were run. |
| Power/assets regeneration | PASS | Prospective power JSON and manuscript figures/tables regenerated without differences. |
| Human-validation labeling | PASS | Protocol is included and explicitly labeled not yet run. |
| Simulation/empirical labeling | PASS | No provider-model result is claimed; simulations and fixtures are labeled non-empirical. |

The pattern scan is a focused release check, not a credential-management audit. The
textual-integrity audit is public-source/local evidence, not a private-corpus plagiarism
certificate.
