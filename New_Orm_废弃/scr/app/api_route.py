from fastapi import APIRouter, Request
from __init__ import templates

route = APIRouter()


# 首页
@route.get('/')
def api_home(request: Request):
    return templates.TemplateResponse(
        "Home.html",
        {
            "request": request
        }
    )
