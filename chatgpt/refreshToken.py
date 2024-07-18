import json
import random
import time

from fastapi import HTTPException

from utils.Client import Client
from utils.Logger import logger
from utils.config import proxy_url_list
from utils.deletetoken import write_token_file
import chatgpt.globals as globals
from chatgpt.wssClient import save_wss_map


async def save_refresh_map(refresh_map):
    try:
        content = json.dumps(refresh_map).encode()
        globals.dbx.files_upload(content, globals.REFRESH_MAP_FILE, mode=globals.WriteMode('overwrite'))
    except Exception as e:
        raise e


async def rt2ac(refresh_token, force_refresh=False):
    if not force_refresh and (refresh_token in globals.refresh_map and int(time.time()) - globals.refresh_map.get(refresh_token, {}).get("timestamp", 0) < 5 * 24 * 60 * 60):
        access_token = globals.refresh_map[refresh_token]["token"]
        logger.info(f"refresh_token -> access_token from cache")
        return access_token
    else:
        try:
            access_token = await chat_refresh(refresh_token)
            globals.refresh_map[refresh_token] = {"token": access_token, "timestamp": int(time.time())}
            #await save_refresh_map(globals.refresh_map)
            logger.info(f"refresh_token -> access_token with openai: {access_token}")
            return access_token
        except HTTPException as e:
            raise HTTPException(status_code=e.status_code, detail=e.detail)


async def chat_refresh(refresh_token):
    data = {
        "client_id": "pdlLIX2Y72MIl2rhLhTE9VV9bN905kBh",
        "grant_type": "refresh_token",
        "redirect_uri": "com.openai.chat://auth0.openai.com/ios/com.openai.chat/callback",
        "refresh_token": refresh_token
    }
    oai_data={"refresh_token": refresh_token}
    client = Client(proxy=random.choice(proxy_url_list) if proxy_url_list else None)
    try:
        #r = await client.post("https://auth0.openai.com/oauth/token", json=data, timeout=5)
        r = await client.post("https://token.oaifree.com/api/auth/refresh", data=oai_data, timeout=5)
        if r.status_code == 200:
            access_token = r.json()['access_token']
            return access_token
        else:
            if "access_denied" in r.text or "invalid_grant" in r.text:
                await del_token(refresh_token)
                globals.count -= 1
            raise Exception(r.text[:100])
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        await client.close()
        del client


async def ac2rt(access_token):
    "从refresh_map里找access_token对应的refresh_token"
    '如果没找到,返回None,说明该access_token是用户上传的,非由refresh_token转化而来'
    for k, v in globals.refresh_map.items():
        if v["token"] == access_token:
            return k
    return None


async def del_token(token):
    if token in globals.refresh_map.keys():
        del globals.refresh_map[token]
        await save_refresh_map(globals.refresh_map)
    if token in globals.wss_map.keys():
        del globals.wss_map[token]
        await save_wss_map(globals.wss_map)
    if token in globals.token_list:
        globals.token_list.remove(token)
        await write_token_file(globals.TOKENS_FILE, globals.token_list)
    if token not in globals.error_token_list:
        globals.error_token_list.append(token)
        await write_token_file(globals.ERROR_TOKENS_FILE, globals.error_token_list)
