from enum import StrEnum
from uuid import UUID

from sqlalchemy import Enum, Float, ForeignKey, Integer, String, Text
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDTimestampMixin


class SourceType(StrEnum):
    pdf = "pdf"
    html = "html"
    csv = "csv"
    manual = "manual"


class DocumentStatus(StrEnum):
    uploaded = "uploaded"
    processing = "processing"
    indexed = "indexed"
    failed = "failed"


class KnowledgeBase(UUIDTimestampMixin, Base):
    __tablename__ = "knowledge_bases"
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    name: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text, default="")
    status: Mapped[str] = mapped_column(String(40), default="active")


class SourceDocument(UUIDTimestampMixin, Base):
    __tablename__ = "source_documents"
    knowledge_base_id: Mapped[UUID] = mapped_column(
        ForeignKey("knowledge_bases.id", ondelete="CASCADE"), index=True
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    title: Mapped[str] = mapped_column(String(300))
    source_type: Mapped[SourceType] = mapped_column(Enum(SourceType, name="source_type"))
    source_url: Mapped[str | None] = mapped_column(String(2048))
    file_path: Mapped[str | None] = mapped_column(String(1024))
    checksum: Mapped[str] = mapped_column(String(64), index=True)
    language: Mapped[str] = mapped_column(String(20), default="en")
    category: Mapped[str] = mapped_column(String(50), default="general")
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus, name="document_status"), default=DocumentStatus.uploaded
    )
    error_message: Mapped[str | None] = mapped_column(Text)


class DocumentChunk(UUIDTimestampMixin, Base):
    __tablename__ = "document_chunks"
    source_document_id: Mapped[UUID] = mapped_column(
        ForeignKey("source_documents.id", ondelete="CASCADE"), index=True
    )
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True
    )
    content: Mapped[str] = mapped_column(Text)
    chunk_index: Mapped[int] = mapped_column(Integer)
    token_count: Mapped[int] = mapped_column(Integer)
    metadata_: Mapped[dict[str, object]] = mapped_column("metadata", JSONB, default=dict)
    embedding: Mapped[list[float]] = mapped_column(ARRAY(Float), nullable=False)
