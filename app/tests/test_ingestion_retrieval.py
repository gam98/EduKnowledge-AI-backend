import asyncio
from uuid import uuid4

import pytest
from fastapi import HTTPException

from app.services.ingestion.validation import chunk_text, validate_upload, validate_url
from app.services.retrieval.embeddings import DeterministicEmbeddings
from app.services.retrieval.service import Evidence, retrieve


def test_rejects_non_allowlisted_url_and_invalid_type():
    with pytest.raises(HTTPException):
        validate_url("https://evil.example/a", {"institution.example"})
    with pytest.raises(HTTPException):
        validate_upload(b"data", "image/png")


def test_chunking_and_tenant_filtered_retrieval():
    assert len(chunk_text("word " * 500)) == 2

    async def run():
        embedder = DeterministicEmbeddings()
        query = (await embedder.embed(["admissions"]))[0]
        org = uuid4()
        other = uuid4()
        source = uuid4()
        items = [
            Evidence(uuid4(), source, org, "admissions", "general", "en", query),
            Evidence(uuid4(), source, other, "admissions", "general", "en", query),
        ]
        return retrieve(query, items, org)

    results = asyncio.run(run())
    assert len(results) == 1
