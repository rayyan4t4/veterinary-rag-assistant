import json
from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from .auth import CurrentUser, admin_user, current_user
from .db import get_db
from .models import Animal
from .schemas import AnimalCreate, AnimalRead, AnimalUpdate, ChatRequest, ChatResponse, TriageRequest, TriageResult
from ai.agents.orchestrator import answer
from ai.safety.triage import assess_triage
from ingestion.pipeline import ingest

router = APIRouter(prefix="/api/v1")


@router.get("/animals", response_model=list[AnimalRead])
async def list_animals(user: CurrentUser = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return (await db.scalars(select(Animal).where(Animal.owner_id == user.id).order_by(Animal.created_at.desc()))).all()


@router.post("/animals", response_model=AnimalRead, status_code=201)
async def create_animal(payload: AnimalCreate, user: CurrentUser = Depends(current_user), db: AsyncSession = Depends(get_db)):
    animal = Animal(owner_id=user.id, **payload.model_dump())
    db.add(animal); await db.commit(); await db.refresh(animal)
    return animal


async def owned_animal(animal_id: str, user: CurrentUser, db: AsyncSession) -> Animal:
    animal = await db.scalar(select(Animal).where(Animal.id == animal_id, Animal.owner_id == user.id))
    if not animal: raise HTTPException(404, "Animal not found")
    return animal


@router.get("/animals/{animal_id}", response_model=AnimalRead)
async def get_animal(animal_id: str, user: CurrentUser = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await owned_animal(animal_id, user, db)


@router.put("/animals/{animal_id}", response_model=AnimalRead)
async def update_animal(animal_id: str, payload: AnimalUpdate, user: CurrentUser = Depends(current_user), db: AsyncSession = Depends(get_db)):
    animal = await owned_animal(animal_id, user, db)
    for key, value in payload.model_dump().items(): setattr(animal, key, value)
    await db.commit(); await db.refresh(animal); return animal


@router.delete("/animals/{animal_id}", status_code=204)
async def delete_animal(animal_id: str, user: CurrentUser = Depends(current_user), db: AsyncSession = Depends(get_db)):
    animal = await owned_animal(animal_id, user, db); await db.delete(animal); await db.commit()


@router.post("/triage", response_model=TriageResult)
async def triage(payload: TriageRequest, _: CurrentUser = Depends(current_user)):
    return assess_triage(payload.text, payload.language)


@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, _: CurrentUser = Depends(current_user), db: AsyncSession = Depends(get_db)):
    return await answer(payload, db)


@router.post("/admin/knowledge", status_code=202)
async def upload_knowledge(file: UploadFile = File(), metadata: str = Form("{}"), _: CurrentUser = Depends(admin_user), db: AsyncSession = Depends(get_db)):
    try: parsed = json.loads(metadata)
    except json.JSONDecodeError as exc: raise HTTPException(422, "Invalid metadata JSON") from exc
    try: return await ingest(db, file.filename or "upload", await file.read(), parsed)
    except ValueError as exc: raise HTTPException(422, str(exc)) from exc
