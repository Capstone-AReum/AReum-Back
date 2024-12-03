from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.models.source import Source, Album
from app.schemas.source import SourceBase, SourceDetail, GalleryResponse

def get_source(db: Session, source_id: int):
    return db.query(Source).filter(Source.id==source_id).first()

def get_album(db: Session, album_id: int):
    return db.query(Album).filter(Album.id==album_id).first()
    
def get_source_detail(db: Session, source_id: int):
    source=get_source(db=db, source_id=source_id)
    if not source:
        raise HTTPException(status_code=404, detail="No such source")
    album=get_album(db=db, album_id=source.album_id)
    if not album:
        raise HTTPException(status_code=404, detail="No such album")
    return SourceDetail(id=source.id, url=source.url, created_at=source.created_at, title=album.title)

def get_all_source(page: int, db: Session):
    skip=(page-1)*10
    total_count=db.query(Source).count()
    images=db.query(Source).order_by(Source.created_at.desc()).offset(skip).limit(10).all()

    image_list = [SourceBase(id=image.id, url=image.url, created_at=image.created_at) for image in images]
    return GalleryResponse(images=image_list, total_count=total_count, page=page, per_page=10)