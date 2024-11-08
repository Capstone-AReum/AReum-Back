from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import get_db, Base
from app.models.models import Example

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app import models
    from app.database import engine

    models.Base.metadata.create_all(bind=engine)

    yield

    pass

app = FastAPI()

@app.get("/health")
def healthCheck(db: Session = Depends(get_db)):
    new_entry = Example(url=str("health"))
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return "I'm healthy!"
