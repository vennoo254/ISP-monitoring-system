from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import SessionLocal

router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get('/', response_model=list[schemas.TargetOut])
def list_targets(db: Session = Depends(get_db)):
    return db.query(models.Target).all()

@router.post('/', response_model=schemas.TargetOut)
def create_target(payload: schemas.TargetCreate, db: Session = Depends(get_db)):
    exists = db.query(models.Target).filter(models.Target.address == payload.address).first()
    if exists:
        raise HTTPException(status_code=400, detail='target already exists')
    t = models.Target(name=payload.name, address=payload.address)
    db.add(t)
    db.commit()
    db.refresh(t)
    return t
