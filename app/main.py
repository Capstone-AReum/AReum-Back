import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import source

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app import models
    from app.database import engine

    models.Base.metadata.create_all(bind=engine)

    yield

    pass

app = FastAPI(lifespan=lifespan)

app.include_router(source.router, prefix='/albums', tags=["albums"])

@app.get("/health")
def healthCheck():
    return "I'm healthy!"

if __name__=="__main__":
    uvicorn.run("router_example:app", host='0.0.0.0', port=8000, reload=True)