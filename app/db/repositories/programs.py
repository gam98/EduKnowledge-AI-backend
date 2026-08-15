from typing import cast
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models.program import AcademicProgram
from app.schemas.programs import ProgramInput


class ProgramRepository:
    def __init__(self, session: AsyncSession, organization_id: UUID):
        self.session, self.organization_id = session, organization_id

    async def list(self) -> list[AcademicProgram]:
        return list(
            (
                await self.session.scalars(
                    select(AcademicProgram).where(
                        AcademicProgram.organization_id == self.organization_id
                    )
                )
            ).all()
        )

    async def get(self, program_id: UUID) -> AcademicProgram | None:
        return cast(AcademicProgram | None, await self.session.scalar(
            select(AcademicProgram).where(
                AcademicProgram.id == program_id,
                AcademicProgram.organization_id == self.organization_id,
            )
        ))

    async def create(self, data: ProgramInput) -> AcademicProgram:
        program = AcademicProgram(organization_id=self.organization_id, **data.model_dump())
        self.session.add(program)
        await self.session.flush()
        return program
