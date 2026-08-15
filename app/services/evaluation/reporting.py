"""Transparent deterministic evaluation report generation."""

import json
from dataclasses import asdict, dataclass
from pathlib import Path


@dataclass(frozen=True)
class EvaluationResult:
    total: int
    recall_at_k: float
    citation_validity: float
    groundedness_heuristic: float
    abstention_rate: float
    latency_ms: float
    estimated_cost: float


def build_report(results: list[dict[str, object]]) -> EvaluationResult:
    total = len(results)
    if not total:
        return EvaluationResult(0, 0, 0, 0, 0, 0, 0)

    def metric(key: str) -> float:
        return sum(1 for item in results if bool(item.get(key))) / total

    return EvaluationResult(
        total,
        metric("retrieved_expected"),
        metric("valid_citations"),
        metric("grounded_heuristic"),
        metric("abstained"),
        sum(float(item.get("latency_ms", 0)) for item in results) / total,
        sum(float(item.get("estimated_cost", 0)) for item in results),
    )


def write_reports(result: EvaluationResult, directory: Path) -> tuple[Path, Path]:
    directory.mkdir(parents=True, exist_ok=True)
    data = directory / "report.json"
    markdown = directory / "report.md"
    data.write_text(json.dumps(asdict(result), indent=2) + "\n")
    markdown.write_text(
        "\n".join(
            [
                "# Evaluation report",
                "",
                f"Cases: {result.total}",
                "",
                f"- recall@k: {result.recall_at_k:.2%}",
                f"- citation validity: {result.citation_validity:.2%}",
                f"- groundedness heuristic (not objective): {result.groundedness_heuristic:.2%}",
                f"- abstention rate: {result.abstention_rate:.2%}",
                f"- mean latency: {result.latency_ms:.1f} ms",
                f"- estimated cost: {result.estimated_cost:.4f}",
                "",
            ]
        )
    )
    return data, markdown
