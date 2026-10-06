"""Build manuscript figures and tables from frozen repository artifacts."""

from __future__ import annotations

import json
from collections import Counter
from pathlib import Path
from typing import Any

import matplotlib.pyplot as plt
import yaml

plt.rcParams["pdf.fonttype"] = 42
plt.rcParams["ps.fonttype"] = 42


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "paper"
FIGURES = PAPER / "figures"
TABLES = PAPER / "tables"


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _write(path: Path, text: str) -> None:
    path.write_text(text.rstrip() + "\n", encoding="utf-8")


def build_architecture_figure() -> None:
    fig, ax = plt.subplots(figsize=(7.1, 2.75))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    colors = {
        "agent": "#DCEBFA",
        "visible": "#FFF0CC",
        "truth": "#DDEFD8",
        "oracle": "#E9DDF3",
        "edge": "#334155",
    }

    def box(x: float, y: float, w: float, h: float, text: str, color: str) -> None:
        patch = plt.Rectangle(
            (x, y), w, h, facecolor=color, edgecolor=colors["edge"], linewidth=1.2
        )
        ax.add_patch(patch)
        ax.text(x + w / 2, y + h / 2, text, ha="center", va="center", fontsize=9)

    def arrow(
        x1: float,
        y1: float,
        x2: float,
        y2: float,
        label: str = "",
        *,
        label_dx: float = 0.0,
        label_dy: float = 0.035,
        label_ha: str = "center",
        label_va: str = "center",
        label_bbox: bool = True,
    ) -> None:
        ax.annotate(
            "",
            xy=(x2, y2),
            xytext=(x1, y1),
            arrowprops={"arrowstyle": "->", "lw": 1.25, "color": colors["edge"]},
        )
        if label:
            ax.text(
                (x1 + x2) / 2 + label_dx,
                (y1 + y2) / 2 + label_dy,
                label,
                ha=label_ha,
                va=label_va,
                fontsize=7.2,
                color=colors["edge"],
                bbox=(
                    {
                        "boxstyle": "round,pad=0.12",
                        "facecolor": "white",
                        "edgecolor": "none",
                        "alpha": 0.96,
                    }
                    if label_bbox
                    else None
                ),
                zorder=5,
            )

    # Deliberately reserve wide, uniform gutters between boxes.  Arrow labels live
    # inside these gutters, rather than extending into a neighboring node.
    box(0.02, 0.58, 0.16, 0.25, "Task + two\nmatched plans", colors["agent"])
    box(0.29, 0.58, 0.16, 0.25, "Immutable\nplan choice", colors["agent"])
    box(0.56, 0.58, 0.16, 0.25, "Tool-visible\nresponse", colors["visible"])
    box(0.82, 0.58, 0.16, 0.25, "Agent terminal\nclaim", colors["visible"])
    box(0.56, 0.10, 0.16, 0.25, "Authoritative\nworld state", colors["truth"])
    box(0.82, 0.10, 0.16, 0.25, "Evaluator +\noracle trace", colors["oracle"])

    arrow(0.18, 0.705, 0.29, 0.705, "select", label_dy=0.055)
    arrow(0.45, 0.705, 0.56, 0.705, "execute", label_dy=0.055)
    arrow(0.72, 0.705, 0.82, 0.705, "observe", label_dy=0.055)
    arrow(
        0.64,
        0.58,
        0.64,
        0.35,
        "may diverge",
        label_dx=-0.028,
        label_dy=0.0,
        label_ha="right",
    )
    arrow(0.72, 0.225, 0.82, 0.225, "score truth", label_dy=0.055)
    arrow(
        0.90,
        0.58,
        0.90,
        0.35,
        "compare",
        label_dx=-0.028,
        label_dy=0.0,
        label_ha="right",
    )

    ax.text(
        0.02,
        0.93,
        "Primary outcome is chosen before execution; tool response is not ground truth.",
        fontsize=10,
        weight="bold",
        color="#172033",
    )
    fig.tight_layout(pad=0.4)
    fig.savefig(
        FIGURES / "proofpath_architecture.pdf",
        bbox_inches="tight",
        metadata={"Creator": "ProofPathBench", "CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def build_power_figure(power: dict[str, Any]) -> None:
    instruction = power["instruction_contrast"]["power_grid"]
    factorial = power["factorial_effects"]["power_grid"]
    reps = [item["repetitions_per_presentation"] for item in instruction]

    series = {
        "Instruction contrast": [item["estimated_power"] for item in instruction],
        "Premium": [item["estimated_power"]["premium_scaled"] for item in factorial],
        "Premium x risk": [item["estimated_power"]["premium_by_risk"] for item in factorial],
        "Premium x severity": [
            item["estimated_power"]["premium_by_severity"] for item in factorial
        ],
    }
    styles = [
        ("#1769AA", "o", "-"),
        ("#2E8B57", "s", "-"),
        ("#C05621", "^", "--"),
        ("#7B2CBF", "D", "--"),
    ]

    fig, ax = plt.subplots(figsize=(4.3, 3.2))
    for (label, values), (color, marker, line) in zip(series.items(), styles, strict=True):
        ax.plot(reps, values, label=label, color=color, marker=marker, linestyle=line, lw=1.8)
    ax.axhline(0.8, color="#64748B", lw=1, ls=":", label="0.80 reference")
    ax.set_xticks(reps)
    ax.set_ylim(0, 1.03)
    ax.set_xlabel("Repetitions per presentation")
    ax.set_ylabel("Estimated prospective power")
    ax.grid(axis="y", alpha=0.25)
    ax.legend(frameon=False, fontsize=7.4, loc="lower right")
    fig.tight_layout()
    fig.savefig(
        FIGURES / "prospective_power.pdf",
        bbox_inches="tight",
        metadata={"Creator": "ProofPathBench", "CreationDate": None, "ModDate": None},
    )
    plt.close(fig)


def build_tables(
    runtime: dict[str, Any], power: dict[str, Any], config: dict[str, Any]
) -> None:
    scenario_paths = sorted((ROOT / "benchmark" / "scenarios").glob("ppb-*.json"))
    scenarios = [_load_json(path) for path in scenario_paths]
    domain_counts = Counter(item["domain"] for item in scenarios)
    mechanism_counts = Counter(
        next(
            plan["evidence_mechanism"]
            for plan in item["candidate_plans"]
            if plan["evidence_mechanism"] != "write_response"
        )
        for item in scenarios
    )

    composition_rows = [
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Domain & Base scenarios \\\\",
        "\\midrule",
    ]
    for domain, count in sorted(domain_counts.items()):
        composition_rows.append(f"{domain.title()} & {count} \\\\")
    composition_rows.extend(
        [
            "\\midrule",
            f"Total & {sum(domain_counts.values())} \\\\",
            "\\bottomrule",
            "\\end{tabular}",
        ]
    )
    _write(TABLES / "benchmark_composition.tex", "\n".join(composition_rows))

    validation = [
        ("Generated base scenarios", runtime["scenario_count"]),
        ("Split-plot treatment units", runtime["split_plot_unit_count"]),
        ("No-fault plan executions", runtime["no_fault_plan_executions"]),
        ("Injectable failure classes", len(runtime["forced_failure_results"])),
        ("Runtime validation errors", len(runtime["errors"])),
    ]
    validation_rows = [
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Deterministic check & Value \\\\",
        "\\midrule",
    ]
    validation_rows.extend(f"{label} & {value} \\\\" for label, value in validation)
    validation_rows.extend(["\\bottomrule", "\\end{tabular}"])
    _write(TABLES / "validation_summary.tex", "\n".join(validation_rows))

    factor_rows = [
        "\\begin{tabularx}{\\columnwidth}{@{}lX@{}}",
        "\\toprule",
        "Factor & Levels / role \\\\",
        "\\midrule",
        "Premium & 1.00, 1.10, 1.50, 2.00; within task \\\\",
        "Disclosed risk & 0, 0.05, 0.20; between task \\\\",
        "Severity & Low, high; between task \\\\",
        "Instruction & Vanilla, verify instruction \\\\",
        "Evidence & Readback, status lookup, multiple source; nuisance \\\\",
        f"Repetitions & {config['study']['repetitions_per_presentation']} per unit \\\\",
        "\\bottomrule",
        "\\end{tabularx}",
    ]
    _write(TABLES / "design_factors.tex", "\n".join(factor_rows))

    mechanism_rows = [
        "\\begin{tabular}{lr}",
        "\\toprule",
        "Evidence mechanism & Base scenarios \\\\",
        "\\midrule",
    ]
    for mechanism, count in sorted(mechanism_counts.items()):
        label = mechanism.replace("_", " ").title()
        mechanism_rows.append(f"{label} & {count} \\\\")
    mechanism_rows.extend(["\\bottomrule", "\\end{tabular}"])
    _write(TABLES / "mechanism_composition.tex", "\n".join(mechanism_rows))

    power_rows = [
        "\\begin{tabular}{rrrrr}",
        "\\toprule",
        "Rep. & Calls & Instr. & Premium & Risk / severity int. \\\\",
        "\\midrule",
    ]
    instruction_grid = power["instruction_contrast"]["power_grid"]
    factorial_grid = power["factorial_effects"]["power_grid"]
    for instruction_item, factorial_item in zip(
        instruction_grid, factorial_grid, strict=True
    ):
        estimates = factorial_item["estimated_power"]
        power_rows.append(
            f"{instruction_item['repetitions_per_presentation']} & "
            f"{instruction_item['total_registered_choice_calls']:,} & "
            f"{instruction_item['estimated_power']:.3f} & "
            f"{estimates['premium_scaled']:.3f} & "
            f"{estimates['premium_by_risk']:.3f} / "
            f"{estimates['premium_by_severity']:.3f} \\\\"
        )
    power_rows.extend(["\\bottomrule", "\\end{tabular}"])
    _write(TABLES / "power_summary.tex", "\n".join(power_rows))


def main() -> None:
    FIGURES.mkdir(parents=True, exist_ok=True)
    TABLES.mkdir(parents=True, exist_ok=True)
    runtime = _load_json(ROOT / "benchmark" / "runtime_validation_report.json")
    power = _load_json(ROOT / "research" / "power_analysis.json")
    config = yaml.safe_load((ROOT / "configs" / "pilot.yaml").read_text(encoding="utf-8"))
    build_architecture_figure()
    build_power_figure(power)
    build_tables(runtime, power, config)


if __name__ == "__main__":
    main()
