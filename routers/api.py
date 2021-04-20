from fastapi import APIRouter, Body, Depends, Path, status, HTTPException, Request
from fastapi.responses import RedirectResponse
from db.setup import get_db
from db import schemas, models, crud
from sqlalchemy.orm import Session
from typing import List

router = APIRouter()

@router.get('/urls', status_code=status.HTTP_200_OK, response_model= List[schemas.outPutShortURL], response_model_exclude_unset=True, tags=['URLs'])
async def listURLs(db: Session = Depends(get_db)):
    urls = crud.get_urls(db)
    urls = list(map(lambda ob: ob.__dict__,urls))
    return urls

@router.get('/urls/{s_url}', status_code=status.HTTP_200_OK, response_model= schemas.outPutShortURL, response_model_exclude_unset=True, tags=['URLs'])
async def singleURL(s_url:str = Path(..., min_length=8, max_length=8), db: Session = Depends(get_db)):
    short_url = crud.single_url(db, s_url)
    return short_url.__dict__

@router.post('/urls', status_code=status.HTTP_201_CREATED, response_model= schemas.outPutShortURL, response_model_exclude_unset=True, tags=['URLs'])
async def createURLs(request: schemas.createShortURL = Body(..., embed=False) , db: Session = Depends(get_db)):
    new_short_url = crud.create_url(db, request)['short_url']
    return new_short_url.__dict__

@router.get('/{s_url}', status_code=status.HTTP_301_MOVED_PERMANENTLY, tags=['Redirect'])
async def redirectURL(s_url:str = Path(..., min_length=8, max_length=8), request: Request = None, db: Session = Depends(get_db)):
    short_url = crud.single_url(db, s_url)
    crud.update_url(db, s_url, {'counter': short_url.counter+1 if 'TelegramBot' not in request.headers['user-agent'] else 0})
    return RedirectResponse(f'https://{short_url.base_url}')