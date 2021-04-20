from fastapi import FastAPI
from core.config import HOST, PORT, DEV, BOT_TOKEN, DOMAIN
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import time
from routers import api, tgbot
from routers.tgbot import tg_bot

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api.router)
app.include_router(tgbot.router)

@app.get('/test')
async def test_url():
    return {'ok':'works'}

if(__name__ == '__main__'):
    tg_bot.remove_webhook()
    time.sleep(0.1)
    tg_bot.set_webhook(url = f'https://{DOMAIN}/{BOT_TOKEN}', allowed_updates=['message'])
    uvicorn.run('server:app', host = HOST, port = PORT, reload = DEV)
    tg_bot.remove_webhook()
