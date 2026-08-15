from datetime import date
from uuid import UUID

from sqlalchemy import Boolean, ForeignKey, Integer, Numeric, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.db.base import Base, UUIDTimestampMixin


class AcademicProgram(UUIDTimestampMixin, Base):
    __tablename__ = "academic_programs"
    organization_id: Mapped[UUID] = mapped_column(
        ForeignKey("organizations.id", ondelete="CASCADE"), index=True, nullable=False
    )
    name: Mapped[str] = mapped_column(String(250), nullable=False)
    degree_type: Mapped[str] = mapped_column(String(100), nullable=False)
    faculty: Mapped[str] = mapped_column(String(150), nullable=False)
    modality: Mapped[str] = mapped_column(String(50), nullable=False)
    duration_months: Mapped[int] = mapped_column(Integer, nullable=False)
    language: Mapped[str] = mapped_column(String(50), nullable=False)
    location: Mapped[str] = mapped_column(String(150), nullable=False)
    tuition_amount: Mapped[float | None] = mapped_column(Numeric(12, 2), nullable=True)
    currency: Mapped[str | None] = mapped_column(String(3), nullable=True)
    application_deadline: Mapped[date | None] = mapped_column(nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    requirements: Mapped[dict[str, object]] = mapped_column(JSONB, default=dict, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
