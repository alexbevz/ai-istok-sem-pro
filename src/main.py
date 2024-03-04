import uvicorn
from fastapi import FastAPI

from src.auth.router import userRouter, roleRouter, authRouter

app = FastAPI(root_path='/api/v0')

# app.include_router(router=roleRouter)
# app.include_router(router=userRouter)
app.include_router(router=authRouter)

if __name__ == '__main__':
    uvicorn.run(
        app="src.main:app",
        host='0.0.0.0',
        port=8000,
        reload=True,
        workers=8
    )
