from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, UploadFile
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.v1.auth import session
from app.api.v1.dependencies import RequestContext, require_roles
from app.db.models.identity import Role
from app.db.repositories.programs import ProgramRepository
from app.schemas.programs import ProgramInput, ProgramResponse
from app.services.programs import compare_programs, parse_program_csv

router = APIRouter(prefix="/programs", tags=["programs"])
reader = Depends(require_roles(Role.admin, Role.editor, Role.viewer))
editor = Depends(require_roles(Role.admin, Role.editor))


@router.get("", response_model=list[ProgramResponse])
async def list_programs(context: RequestContext = reader, db: AsyncSession = Depends(session)):
    return await ProgramRepository(db, context.organization_id).list()


@router.post("", response_model=ProgramResponse, status_code=201)
async def create_program(
    payload: ProgramInput, context: RequestContext = editor, db: AsyncSession = Depends(session)
):
    p = await ProgramRepository(db, context.organization_id).create(payload)
    await db.commit()
    return p


@router.get("/{program_id}", response_model=ProgramResponse)
async def get_program(
    program_id: UUID, context: RequestContext = reader, db: AsyncSession = Depends(session)
):
    p = await ProgramRepository(db, context.organization_id).get(program_id)
    if p is None:
        raise HTTPException(404, "Program not found")
    return p


@router.post("/import-csv", response_model=list[ProgramResponse])
async def import_csv(
    file: UploadFile, context: RequestContext = editor, db: AsyncSession = Depends(session)
):
    if file.content_type not in {"text/csv", "application/csv"}:
        raise HTTPException(415, "Only CSV files are allowed")
    values = parse_program_csv((await file.read()).decode("utf-8"))
    repo = ProgramRepository(db, context.organization_id)
    programs = [await repo.create(value) for value in values]
    await db.commit()
    return programs


@router.post("/compare")
async def compare(
    ids: list[UUID], context: RequestContext = reader, db: AsyncSession = Depends(session)
):
    repo = ProgramRepository(db, context.organization_id)
    programs = []
    for program_id in ids:
        p = await repo.get(program_id)
        if p is None:
            raise HTTPException(404, "Program not found")
        programs.append(p)
    return {"programs": compare_programs(programs)}


@router.patch("/{program_id}", response_model=ProgramResponse)
async def update_program(
    program_id: UUID,
    payload: ProgramInput,
    context: RequestContext = editor,
    db: AsyncSession = Depends(session),
):
    p = await ProgramRepository(db, context.organization_id).get(program_id)
    if p is None:
        raise HTTPException(404, "Program not found")
    for key, value in payload.model_dump().items():
        setattr(p, key, value)
    await db.commit()
    return p


@router.delete("/{program_id}", status_code=204)
async def delete_program(
    program_id: UUID, context: RequestContext = editor, db: AsyncSession = Depends(session)
):
    p = await ProgramRepository(db, context.organization_id).get(program_id)
    if p is None:
        raise HTTPException(404, "Program not found")
    await db.delete(p)
    await db.commit()
