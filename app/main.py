from fastapi import FastAPI
from app.api.routes import modele, pifumodel  # pifumodel 추가

app = FastAPI()

# 3D 모델 생성 라우터 등록
app.include_router(modele.router)
app.include_router(pifumodel.router)  # pifumodel 라우터 추가

@app.get("/health")
def healthCheck():
    return "I'm healthy!"
