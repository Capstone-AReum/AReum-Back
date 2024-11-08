from fastapi import FastAPI
from app.api.routes.rmback import router as rmback_router
app = FastAPI()

app.include_router(rmback_router)

@app.get("/health")
def healthCheck():
    return "I'm healthy!"
