
import chatgpt.globals as globals

from utils.Logger import logger


async def write_token_file(token_file,token_list):
    try:           
        content = "\n".join(token_list).encode() + '\n'.encode()
        globals.dbx.files_upload(content, token_file, mode=globals.WriteMode('overwrite'))
    except Exception as e:
        logger.error(f"write file error.{str(e)}")

