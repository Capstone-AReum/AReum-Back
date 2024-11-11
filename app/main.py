import uvicorn
from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import get_db
#from app.models.models import Example

from app.api.routes import upload

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models import models
    from app.database import engine

    models.Base.metadata.create_all(bind=engine)

    yield

    pass

app = FastAPI(lifespan=lifespan)

app.include_router(upload.router)

@app.get("/health")
def healthCheck(db: Session = Depends(get_db)):
#    new_entry = Example(url=str("health"))
#    db.add(new_entry)
#    db.commit()
#    db.refresh(new_entry)
    return "I'm healthy!"

if __name__=="__main__":
    uvicorn.run("router_example:app", host='0.0.0.0', port=8000, reload=True)