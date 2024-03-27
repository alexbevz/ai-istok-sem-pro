import uvicorn
from fastapi import FastAPI

from src.auth.router import userRouter, roleRouter, authRouter

from src.semantic_proximity.router import spsRouter


description = """
Данное приложение пердставляет собой API для поиска семантической близости между различными данными с аворизацйией.
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
        "description": "Поиск семантической близости между различными данными с аворизацйией.",
    },
]

app = FastAPI(root_path='/api/v0',
              title="SemanticSerchApp",
              description=description,
              summary="Куку",
              version="0.0.1",
              terms_of_service="Some form",
              contact={
                  "name": "Исток",
                  "url": "https://istokmw.ru/",
                  "email": "Куку.istokmw.ru",
              },
              license_info={
                  "name": "Куку",
                  "identifier": "Куку",
              },
              openapi_tags=tags_metadata, )

app.include_router(router=roleRouter)
app.include_router(router=userRouter)
app.include_router(router=authRouter)

app.include_router(router=spsRouter)

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host='0.0.0.0',
        port=8000,
        # reload=True,
        # workers=8
    )
