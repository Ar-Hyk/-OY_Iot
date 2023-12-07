from dotenv import load_dotenv
import os
import uvicorn

load_dotenv(override=True)
from scr.log import logger

if __name__ == '__main__':
    uvicorn.run(app='main:api_server', host=os.getenv('API_HOST'), port=int(os.getenv('API_PORT')))
