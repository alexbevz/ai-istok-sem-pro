import uvicorn
from fastapi import FastAPI

from src.auth.router import userRouter, roleRouter, authRouter

from src.semantic_proximity.router import spsRouter

from src.handler import exception_handlers

from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)
from fastapi.staticfiles import StaticFiles

description = """
API для поиска семантической близости между текстами.
"""

tags_metadata = [
    {
        "name": "Роли",
        "description": "Просмотр и управление **ролями** пользователей",
    },
    {
        "name": "Пользователи",
        "description": "Управление пользователями",
        "externalDocs": {
            "description": "Ссылка",
            "url": "https://localhost/",
        },
    },
    {
        "name": "Авторизация",
        "description": "Авторизация пользователей",
    },
    {
        "name": "Семантическая близость",
        "description": "Поиск семантической близости между различными данными.",
    },
]

app = FastAPI(root_path='/api/v0',
              title="SemanticSearchApp",
              description=description,
              summary="Семантический поиск",
              version="0.0.1",
              terms_of_service="Some form",
              contact={
                  "name": "Исток",
                  "url": "https://istokmw.ru/",
              },
              openapi_tags=tags_metadata, )

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/docs", include_in_schema=False)
async def custom_swagger_ui_html():
    return get_swagger_ui_html(
        openapi_url=app.openapi_url,
        title=app.title + " - Swagger UI",
        oauth2_redirect_url=app.swagger_ui_oauth2_redirect_url,
        swagger_js_url="/static/swagger-ui-bundle.js",
        swagger_css_url="/static/swagger-ui.css",
    )

@app.get(app.swagger_ui_oauth2_redirect_url, include_in_schema=False)
async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()

@app.get("/redoc", include_in_schema=False)
async def redoc_html():
    return get_redoc_html(
        openapi_url=app.openapi_url,
        title=app.title + " - ReDoc",
        redoc_js_url="/static/redoc.standalone.js",
    )

app.include_router(router=roleRouter)
app.include_router(router=userRouter)
app.include_router(router=authRouter)

app.include_router(router=spsRouter)

app.exception_handlers = exception_handlers

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        # reload=True,
        # workers=8
    )
