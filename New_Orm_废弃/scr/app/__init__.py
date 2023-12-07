from fastapi import APIRouter
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from api_route import route

view = APIRouter()
# 模板文件配置
templates = Jinja2Templates(directory="./templates")
# # 静态文件配置
view.mount('/static', StaticFiles(directory='./static'), name='static')
# 解决FastAPI跨域问题
view.include_router(route)
