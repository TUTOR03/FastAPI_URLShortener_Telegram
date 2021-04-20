from fastapi import APIRouter, Depends, status, Request
from core.config import BOT_TOKEN, DOMAIN, BOT_TOKEN
from db.setup import get_db
from sqlalchemy.orm import Session
from db import schemas, models, crud
import re

import telebot
from telebot import apihelper

apihelper.SESSION_TIME_TO_LIVE = 5 * 60
tg_bot = telebot.TeleBot(BOT_TOKEN)

router = APIRouter()

async def clearBody(request: Request):
    data = await request.json()
    req = {
        'chat_id': data.get('message').get('chat')['id'],
        'message':  data.get('message').get('text')
    }
    return req

@router.post(f'/{BOT_TOKEN}', status_code=status.HTTP_200_OK, include_in_schema=False)
async def handleBotMessages(request = Depends(clearBody), db: Session = Depends(get_db)):
    try:
        if request['message'] == '/start':
            tg_bot.send_message(request['chat_id'], 'Wellcome')
            return ''
        if re.compile('^(https:\/\/[a-z,A-Z,0-9,\-,_,.]+\.[a-z,A-Z]{2,4}[А-Я,а-я,a-z,A-Z,0-9,\-,_,\/,=,?,&]*|[a-z,A-Z,0-9,\-,_,.]+\.[a-z,A-Z]{2,4}[А-Я,а-я,a-z,A-Z,0-9,\-,_,\/,=,?,&]*)$').match(request['message']):
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
    except:
        pass
    return ''