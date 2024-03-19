import uvicorn
from fastapi import FastAPI

from src.auth.router import userRouter, roleRouter, authRouter

from src.semantic_proximity.router import spsRouter


app = FastAPI(root_path='/api/v0')

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
