from contextlib import asynccontextmanager
from sqlalchemy.orm import Session
from sqlalchemy import Column, String, Integer
from fastapi import FastAPI, Depends

from app.database import get_db, Base, engine

class Exapmle(Base):
    __tablename__="fileUrls"
    id=Column(Integer, primary_key=True, index=True)
    url=Column(String(255), unique=True, nullable=False)

Base.metadata.create_all(bind=engine)

#@asynccontextmanager
#async def lifespan(app: FastAPI):
#    from app import models
#    from app.database import engine

#    models.Base.metadate.create_all(bind=engine)

#    yield

#    pass

app = FastAPI()

@app.get("/health")
def healthCheck(db: Session = Depends(get_db)):
    new_entry = Exapmle(url=str("helath"))
    db.add(new_entry)
    db.commit()
    db.refresh(new_entry)
    return "I'm healthy!"
