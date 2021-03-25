from sqlalchemy.orm import Session
from . import models, schemas
from fastapi import HTTPException, status
from core.config import ENC_TABLE
import hashlib

def get_urls(db: Session):
    return db.query(models.ShortURL).all()

def single_url(db: Session, s_url: str):
    short_url = db.query(models.ShortURL).filter(models.ShortURL.short == s_url).first()
    if(not short_url):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    return short_url

def update_url(db: Session, s_url: str, request: schemas.updateShortURL):
    short_url = db.query(models.ShortURL).filter(models.ShortURL.short == s_url)
    if(not short_url.first()):
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND)
    short_url.update(request)
    db.commit()

def create_url(db: Session, request: schemas.createShortURL):
    base_url = request.base_url
    if(base_url.startswith('https://')):
        base_url = base_url.replace('https://','')
    short_url = db.query(models.ShortURL).filter(models.ShortURL.base_url == base_url).first()
    if(not short_url):
        hash_object = hashlib.sha512(base_url.encode()).hexdigest()
        num = int(hash_object, 16)
        short = ''
        base = len(ENC_TABLE)
        while num:
            short += ENC_TABLE[int(num % base)]
            num //= base
        short = short[::-1][:8]
        short_url = models.ShortURL(base_url = base_url, short = short)
        db.add(short_url)
        db.commit()
        db.refresh(short_url)
    return short_url