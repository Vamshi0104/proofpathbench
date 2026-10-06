"""Ground-truth outcomes and benchmark metrics."""

from proofpath.evaluation.metrics import proportion_metric, summarize_records, wilson_interval
from proofpath.evaluation.outcomes import OutcomeEvaluation, evaluate_outcome
from proofpath.evaluation.statistics import fit_primary_model, holm_adjust, records_dataframe

__all__ = [
    "OutcomeEvaluation",
    "evaluate_outcome",
    "fit_primary_model",
    "holm_adjust",
    "proportion_metric",
    "records_dataframe",
    "summarize_records",
    "wilson_interval",
]
