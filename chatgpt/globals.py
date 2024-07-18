import json
import os

from utils.clouddriver import dbx
from utils.Logger import logger

from dropbox.exceptions import ApiError
from dropbox.files import WriteMode


TOKENS_FILE = os.getenv("DATA_FOLDER", "/token.txt")
REFRESH_MAP_FILE = os.getenv("DATA_FOLDER", "/refresh_map.json")
ERROR_TOKENS_FILE = os.getenv("DATA_FOLDER", "/error_token.txt")
WSS_MAP_FILE = os.getenv("DATA_FOLDER", "/wss_map.json")

count = 0
token_list = []
error_token_list = []
refresh_map = {}
wss_map = {}


try:
    # 尝试获取文件元数据
    dbx.files_get_metadata(REFRESH_MAP_FILE)
    # 如果文件存在，下载文件，追加内容，然后重新上传
    _, res = dbx.files_download(REFRESH_MAP_FILE)           
    content = res.content.decode()
    refresh_map = json.loads(content)
except ApiError as e:
    if e.error.is_path() and e.error.get_path().is_not_found():
        # 如果文件不存在，创建并上传文件
        refresh_map = {}
    else:
        raise e

try:
    # 尝试获取文件元数据
    dbx.files_get_metadata(WSS_MAP_FILE)
    # 如果文件存在，下载文件，追加内容，然后重新上传
    _, res = dbx.files_download(WSS_MAP_FILE)           
    content = res.content.decode()
    wss_map = json.loads(content)
except ApiError as e:
    if e.error.is_path() and e.error.get_path().is_not_found():
        # 如果文件不存在，创建并上传文件
        wss_map = {}
    else:
        raise e
    
try:
    # 尝试获取文件元数据
    dbx.files_get_metadata(TOKENS_FILE)
    # 如果文件存在，下载文件，追加内容，然后重新上传
    _, res = dbx.files_download(TOKENS_FILE)
    conlist=res.content.decode().splitlines()
    token_list=[i for i in conlist if not i.startswith("#")]                    
except ApiError as e:
    if e.error.is_path() and \
            e.error.get_path().is_not_found():
        # 如果文件不存在，创建并上传文件
        dbx.files_upload(b'', TOKENS_FILE)
    else:
        raise e

try:
    # 尝试获取文件元数据
    dbx.files_get_metadata(ERROR_TOKENS_FILE)
    # 如果文件存在，下载文件，追加内容，然后重新上传
    _, res = dbx.files_download(ERROR_TOKENS_FILE)
    conlist=res.content.decode().splitlines()
    error_token_list=[i for i in conlist if not i.startswith("#")]                    
except ApiError as e:
    if e.error.is_path() and \
            e.error.get_path().is_not_found():
        # 如果文件不存在，创建并上传文件
        dbx.files_upload(b'', ERROR_TOKENS_FILE)
    else:
        raise e

if token_list:
    logger.info(f"Token list count: {len(token_list)}, Error token list count: {len(error_token_list)}")
