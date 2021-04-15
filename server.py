from fastapi import FastAPI, Body, Depends, Path, status, HTTPException, Request
from fastapi.responses import RedirectResponse
from core.config import PSQL_URL, HOST, PORT, DEV, BOT_TOKEN, DOMAIN
from db import schemas, models, crud
from db.setup import get_db
from sqlalchemy.orm import Session
import uvicorn
from typing import List
import telebot
from telebot import apihelper
import time
import re

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
tg_bot = telebot.TeleBot(BOT_TOKEN)

app = FastAPI()

async def clearBody(request: Request):
    data = await request.json()
    req = {
        'chat_id': data.get('message').get('chat')['id'],
        'message':  data.get('message').get('text')
    }
    return req

@app.get('/test')
async def test_url():
    return {'ok':'works'}

@app.get('/urls', status_code=status.HTTP_200_OK, response_model= List[schemas.outPutShortURL], response_model_exclude_unset=True, tags=['URLs'])
async def listURLs(db: Session = Depends(get_db)):
    urls = crud.get_urls(db)
    urls = list(map(lambda ob: ob.__dict__,urls))
    return urls

@app.get('/urls/{s_url}', status_code=status.HTTP_200_OK, response_model= schemas.outPutShortURL, response_model_exclude_unset=True, tags=['URLs'])
async def singleURL(s_url:str = Path(..., min_length=8, max_length=8), db: Session = Depends(get_db)):
    short_url = crud.single_url(db, s_url)
    return short_url.__dict__

@app.post('/urls', status_code=status.HTTP_201_CREATED, response_model= schemas.outPutShortURL, response_model_exclude_unset=True, tags=['URLs'])
async def createURLs(request: schemas.createShortURL = Body(..., embed=False) , db: Session = Depends(get_db)):
    new_short_url = crud.create_url(db, request)['short_url']
    return new_short_url.__dict__

@app.get('/{s_url}', status_code=status.HTTP_301_MOVED_PERMANENTLY, tags=['Redirect'])
async def redirectURL(s_url:str = Path(..., min_length=8, max_length=8), request: Request = None, db: Session = Depends(get_db)):
    short_url = crud.single_url(db, s_url)
    crud.update_url(db, s_url, {'counter': short_url.counter+1 if 'TelegramBot' not in request.headers['user-agent'] else 0})
    return RedirectResponse(f'https://{short_url.base_url}')

@app.post(f'/{BOT_TOKEN}', status_code=status.HTTP_200_OK)
async def handleBotMessages(request = Depends(clearBody), db: Session = Depends(get_db)):
    if request['message'] == '/start':
        tg_bot.send_message(request['chat_id'], 'Wellcome')
        return ''
    if re.match(r'^(https:\/\/[a-z,A-Z,0-9,\-,_,.]+\.[a-z,A-Z]{2,4}[А-Я,а-я,a-z,A-Z,0-9,\-,_,\/,=,?,&]*|[a-z,A-Z,0-9,\-,_,.]+\.[a-z,A-Z]{2,4}[А-Я,а-я,a-z,A-Z,0-9,\-,_,\/,=,?,&]*)$',request['message']):
        if request['message'].startswith('https://'):
            request['message'] = request['message'].replace('https://','')
        if request['message'].startswith(DOMAIN):
            short_url = request['message'].replace(DOMAIN,'')[1:]
            try:
                result = crud.single_url(db, short_url)
                result = {
                    'short_url':result,
                    'new': False
                }
            except:
                reply_mes = "We don't have url like that"
                tg_bot.send_message(request['chat_id'], reply_mes)
                return ''
        else:
            short_url = schemas.createShortURL(base_url = request['message'])
            result = crud.create_url(db, short_url)
        if(result['new']):
            reply_mes = 'IT IS NEW URL\n'
        else:
            reply_mes = 'URL ALREADY EXISTS\n'
        result = result['short_url']
        reply_mes = f'{reply_mes}\nFROM: {DOMAIN}/{result.short}\n\nTO: {result.base_url}\n\nVISITS: {result.counter}'
        tg_bot.send_message(request['chat_id'], reply_mes)
        return ''
    return ''

if(__name__ == '__main__'):
    tg_bot.remove_webhook()
    time.sleep(0.1)
    tg_bot.set_webhook(url = f'https://dca5122ddbaa.ngrok.io/{BOT_TOKEN}', allowed_updates=['message'])
    uvicorn.run('server:app', host = HOST, port = PORT, reload = DEV)
    tg_bot.remove_webhook()