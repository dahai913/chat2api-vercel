import asyncio

from fastapi import HTTPException

from chatgpt.refreshToken import rt2ac
from utils.Logger import logger
from utils.config import authorization_list
import chatgpt.globals as globals


def get_req_token(req_token):
    if req_token in authorization_list:
        if globals.token_list:
            globals.count %= len(globals.token_list)
            while globals.token_list[globals.count] in globals.error_token_list:
                globals.count += 1
                globals.count %= len(globals.token_list)
            token = globals.token_list[globals.count]
            globals.count += 1
            return token
        else:
            return None
    else:
        return req_token


async def verify_token(req_token):
    if not req_token:
        if authorization_list:
            logger.error("Unauthorized with empty token.")
            raise HTTPException(status_code=401)
        else:
            return None
    else:
        if req_token.startswith("eyJhbGciOi") or req_token.startswith("fk-"):
            access_token = req_token
            return access_token
        elif len(req_token) == 45:
            try:
                access_token = await rt2ac(req_token, force_refresh=False)
                return access_token
            except HTTPException as e:
                raise HTTPException(status_code=e.status_code, detail=e.detail)
        else:
            return req_token
