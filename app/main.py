from fastapi import FastAPI, Depends
from contextlib import asynccontextmanager
from sqlalchemy.orm import Session

from app.database import get_db
#from app.models.models import Example

from fastapi import UploadFile, File, HTTPException
from app.utils.s3_utils import upload_to_s3

@asynccontextmanager
async def lifespan(app: FastAPI):
    from app.models import models
    from app.database import engine

    models.Base.metadata.create_all(bind=engine)

    yield

    pass

app = FastAPI(lifespan=lifespan)

@app.get("/health")
def healthCheck(db: Session = Depends(get_db)):
#    new_entry = Example(url=str("health"))
#    db.add(new_entry)
#    db.commit()
#    db.refresh(new_entry)
    return "I'm healthy!"

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)) -> dict:
    try:
        file_url=upload_to_s3(file)
        return {"file_url": file_url}
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))