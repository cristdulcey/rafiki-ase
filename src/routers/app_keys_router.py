from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import get_db
from helpers.create_key import generate_symmetric_key, generate_uuid
from helpers.dependencies import validate_auth
from models.app_key import AppKey
from schemas.app_key_schema import (
    AppKeyCreate,
    AppKeyListResponse,
    AppKeyResponse,
    AppKeyUpdate,
)

router = APIRouter(
    prefix="/app-keys",
    tags=["App Keys"],
    dependencies=[Depends(validate_auth)],
)


@router.post("", status_code=status.HTTP_201_CREATED, response_model=AppKeyResponse)
async def create_app_key(data: AppKeyCreate, db: Session = Depends(get_db)):
    secret = generate_symmetric_key()

    app_key = AppKey(
        name=data.name,
        issuer=data.issuer,
        audience=data.audience,
        secret_key=secret,
        is_active=data.is_active if data.is_active is not None else True,
    )
    db.add(app_key)
    db.commit()
    db.refresh(app_key)
    return app_key


@router.get("", response_model=AppKeyListResponse)
async def list_app_keys(
    is_active: Optional[bool] = None, db: Session = Depends(get_db)
):
    query = db.query(AppKey)
    if is_active is not None:
        query = query.filter(AppKey.is_active == is_active)
    items = query.all()
    return AppKeyListResponse(items=items, count=len(items))


@router.get("/{key_id}", response_model=AppKeyResponse)
async def get_app_key(key_id: str, db: Session = Depends(get_db)):
    app_key = db.query(AppKey).filter(AppKey.id == key_id).first()
    if not app_key:
        raise HTTPException(status_code=404, detail="Key not found")
    return app_key


@router.patch("/{key_id}", response_model=AppKeyResponse)
async def update_app_key(key_id: str, data: AppKeyUpdate, db: Session = Depends(get_db)):
    app_key = db.query(AppKey).filter(AppKey.id == key_id).first()
    if not app_key:
        raise HTTPException(status_code=404, detail="Key not found")

    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(app_key, field, value)

    db.commit()
    db.refresh(app_key)
    return app_key


@router.delete("/{key_id}", status_code=status.HTTP_204_NO_CONTENT)
async def disable_app_key(key_id: str, db: Session = Depends(get_db)):
    app_key = db.query(AppKey).filter(AppKey.id == key_id).first()
    if not app_key:
        raise HTTPException(status_code=404, detail="Key not found")
    app_key.is_active = False
    db.commit()
    return None
