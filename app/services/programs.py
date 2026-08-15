import csv
from collections.abc import Sequence
from io import StringIO

from fastapi import HTTPException

from app.schemas.programs import ProgramInput

REQUIRED = {
    "name",
    "degree_type",
    "faculty",
    "modality",
    "duration_months",
    "language",
    "location",
    "description",
}


def parse_program_csv(content: str) -> list[ProgramInput]:
    rows = list(csv.DictReader(StringIO(content)))
    if not rows or not REQUIRED.issubset(rows[0]):
        raise HTTPException(422, "CSV is missing required headers")
    try:
        return [
            ProgramInput.model_validate(
                {**row, "duration_months": int(row["duration_months"]), "requirements": {}}
            )
            for row in rows
        ]
    except (ValueError, TypeError) as exc:
        raise HTTPException(422, "CSV contains invalid program data") from exc


def compare_programs(programs: Sequence[object]) -> list[dict[str, object]]:
    if not 2 <= len(programs) <= 4:
        raise HTTPException(422, "Compare between 2 and 4 programs")
    return [
        {
            field: getattr(p, field)
            for field in (
                "id",
                "name",
                "degree_type",
                "faculty",
                "modality",
                "duration_months",
                "language",
                "location",
                "tuition_amount",
                "currency",
                "application_deadline",
            )
        }
        for p in programs
    ]
