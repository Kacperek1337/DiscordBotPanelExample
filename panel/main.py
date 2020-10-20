import json
import os
import urllib.parse
from typing import Optional

import psycopg2
import uvicorn
from fastapi import Cookie, FastAPI, Form, Request
from fastapi.templating import Jinja2Templates
from rauth import OAuth2Service
from starlette.responses import RedirectResponse

app = FastAPI()
templates = Jinja2Templates(directory='templates')

HOST = '127.0.0.1'
PORT = 8000

CONN = None


redirect_uri = f'http://{HOST}:{PORT}/discord'
discord = OAuth2Service(
    name='discord',
    client_id=os.getenv('CLIENT_ID'),
    client_secret=os.getenv('CLIENT_SECRET'),
    access_token_url='https://discord.com/api/oauth2/token',
    authorize_url='https://discord.com/api/oauth2/authorize',
    base_url='https://discord.com/api/'
)
authorize_url = discord.get_authorize_url(
        scope='identify',
        response_type='code',
        redirect_uri=redirect_uri
)


@app.get('/')
async def index(request: Request):
    return templates.TemplateResponse(
        'index.html',
        {
            'request': request
        }
    )


@app.get('/me')
async def me(
        request: Request,
        notice: Optional[str] = None,
        token: str = Cookie(None)):
    session = discord.get_session(token)
    response = session.get('users/@me')
    if response.status_code != 200:
        return RedirectResponse('/login')
    return templates.TemplateResponse(
        'me.html',
        {
            'request': request,
            **response.json(),
            'notice': notice
        }
    )


@app.post('/change_settings')
async def change_settings(msg: str = Form(...), token: str = Cookie(None)):
    session = discord.get_session(token)
    query = """
    INSERT INTO
    settings(user_id, message)
    VALUES(%s, %s)
    ON CONFLICT(user_id) DO
    UPDATE SET message = EXCLUDED.message
    """
    with CONN.cursor() as cursor:
        cursor.execute(
            query,
            (
                session.get('users/@me').json()['id'],
                msg,
            )
        )
    return RedirectResponse(
        '/me?notice=%s' % urllib.parse.quote('Settings changed!'),
        status_code=302)


@app.get('/login', status_code=301)
async def login(token: str = Cookie(None)):
    if discord.get_session(token).get(
        'users/@me'
    ).status_code != 200:
        return RedirectResponse(authorize_url)
    return RedirectResponse('/me')


@app.get('/logout')
async def logout(request: Request):
    response = templates.TemplateResponse(
        'logged_out.html',
        {
            'request': request
        }
    )
    response.delete_cookie('token')
    return response


@app.get('/discord')
async def discord_callback(request: Request, code: str):
    data = {
        'request': request
    }
    response = templates.TemplateResponse(
            'signed_in.html', data
        )
    try:
        response.set_cookie(
            key='token',
            value=discord.get_access_token(
                data={
                    'code': code,
                    'grant_type': 'authorization_code',
                    'redirect_uri': redirect_uri
                },
                decoder=json.loads
            ),
            httponly=True,
            secure=True
        )
    except KeyError:
        response = templates.TemplateResponse(
            'signed_in_exc.html', data
        )
    return response


if __name__ == '__main__':
    print('Connecting to database')
    CONN = psycopg2.connect("""
                            host=127.0.0.1
                            port=5432
                            dbname=bot_panel
                            user=postgres
                            password=password
                            """)
    CONN.autocommit = True
    print(f'Starting application on http:/{HOST}:{PORT}')
    uvicorn.run(app, host=HOST, port=PORT)
