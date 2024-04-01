import uvicorn
from fastapi import FastAPI

from src.auth.router import userRouter, roleRouter, authRouter

from src.semantic_proximity.router import spsRouter

from src.handler import exception_handlers


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
