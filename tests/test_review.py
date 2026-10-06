import csv
import json
from pathlib import Path

from proofpath.review import FORM_FIELDS, _cohen_kappa, adjudicate_reviews


def test_cohen_kappa_perfect_and_imperfect() -> None:
    assert _cohen_kappa(["yes", "no"], ["yes", "no"]) == 1.0
    assert _cohen_kappa(["yes", "yes", "no", "no"], ["yes", "no", "yes", "no"]) == 0.0


def test_adjudication_accepts_complete_matching_reviews(
    tmp_path: Path, monkeypatch
) -> None:
    key_path = tmp_path / "key.json"
    key_path.write_text(
        json.dumps(
            {
                "items": [
                    {
                        "review_id": "review-1",
                        "expected_stronger_evidence_candidate": "X",
                    },
                    {
                        "review_id": "review-2",
                        "expected_stronger_evidence_candidate": "Y",
                    },
                ]
            }
        )
    )
    monkeypatch.setattr("proofpath.review.KEY_PATH", key_path)
    paths = []
    for name in ("one.csv", "two.csv"):
        path = tmp_path / name
        with path.open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=FORM_FIELDS)
            writer.writeheader()
            writer.writerow(
                {
                    "review_id": "review-1",
                    "semantic_equivalent": "yes",
                    "stronger_evidence_candidate": "X",
                    "wording_bias_candidate": "none",
                    "notes": "",
                }
            )
            writer.writerow(
                {
                    "review_id": "review-2",
                    "semantic_equivalent": "yes",
                    "stronger_evidence_candidate": "Y",
                    "wording_bias_candidate": "none",
                    "notes": "",
                }
            )
        paths.append(path)
    report = adjudicate_reviews(paths[0], paths[1])
    assert report["admission_ready_without_adjudication"] is True
    assert report["unanimous_accept_count"] == 2
