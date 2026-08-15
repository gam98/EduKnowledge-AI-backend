from app.services.evaluation.reporting import build_report, write_reports


def test_report_labels_heuristic_and_writes_files(tmp_path):
    report = build_report(
        [
            {
                "retrieved_expected": True,
                "valid_citations": True,
                "grounded_heuristic": True,
                "abstained": False,
                "latency_ms": 12,
                "estimated_cost": 0,
            }
        ]
    )
    data, markdown = write_reports(report, tmp_path)
    assert data.exists() and "not objective" in markdown.read_text()
