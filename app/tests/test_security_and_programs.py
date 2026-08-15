from app.core.security import (
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.services.programs import parse_program_csv


def test_password_and_token_round_trip():
    encoded = hash_password("long-enough-password")
    assert verify_password("long-enough-password", encoded)
    token = create_access_token(
        "00000000-0000-0000-0000-000000000001",
        "00000000-0000-0000-0000-000000000002",
        "viewer",
        "secret",
        30,
    )
    assert decode_access_token(token, "secret")["role"] == "viewer"


def test_csv_parses_programs():
    csv = (
        "name,degree_type,faculty,modality,duration_months,language,location,description\n"
        "Demo,Bachelor,Science,Online,36,English,Remote,Demo data\n"
    )
    assert parse_program_csv(csv)[0].name == "Demo"
