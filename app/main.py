import uvicorn
from fastapi import FastAPI
from contextlib import asynccontextmanager

from app.api.routes import source
from app.api.routes import twodto3d

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app import models
    from app.database import engine

    models.Base.metadata.create_all(bind=engine)

    yield

    pass

app = FastAPI(lifespan=lifespan)

app.include_router(source.router, prefix='/albums', tags=["albums"])
app.include_router(twodto3d.router, prefix="/modeling", tags=["modeling"])

@app.get("/health")
def healthCheck():
    return "I'm healthy!"

if __name__=="__main__":
    uvicorn.run("router_example:app", host='0.0.0.0', port=8000, reload=True)