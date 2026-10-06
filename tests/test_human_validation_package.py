import csv
import importlib.util
import json
from pathlib import Path


MODULE_PATH = Path("research/human_validation/analyze_reviews.py")
SPEC = importlib.util.spec_from_file_location("human_validation", MODULE_PATH)
assert SPEC is not None and SPEC.loader is not None
MODULE = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(MODULE)


def test_blinded_sample_is_complete_balanced_and_key_free(tmp_path: Path) -> None:
    private_manifest = tmp_path / "blinding_manifest.json"
    MODULE.generate(private_manifest=private_manifest)
    packet = json.loads(Path("research/human_validation/sampled_items.json").read_text())
    manifest = json.loads(private_manifest.read_text())
    assert packet["sample_size"] == 32
    assert len(packet["items"]) == len(manifest["items"]) == 32
    public_text = json.dumps(packet)
    assert "scenario_id" not in public_text
    assert "expected_evidence_dominant_candidate" not in public_text
    assert "evidence_profile" not in public_text
    assert {item["expected_evidence_dominant_candidate"] for item in manifest["items"]} == {"X", "Y"}
    assert sum(item["expected_evidence_dominant_candidate"] == "X" for item in manifest["items"]) == 16


def test_review_form_has_one_blank_row_per_item() -> None:
    with Path("research/human_validation/review_form.csv").open(newline="") as stream:
        rows = list(csv.DictReader(stream))
    assert len(rows) == 32
    assert len({row["review_id"] for row in rows}) == 32
    assert all(not row["reviewer_id"] for row in rows)


def test_kappa_implementations() -> None:
    assert MODULE._kappa(["a", "b"], ["a", "b"]) == 1.0
    assert MODULE._kappa(["none", "weak", "strong"], ["none", "weak", "strong"], ("none", "weak", "strong", "uncertain")) == 1.0
