from fastapi import FastAPI
from api.tryon import router as tryon_router

app = FastAPI(title="Virtual Try-On Backend")

app.include_router(tryon_router, prefix="/tryon", tags=["Try-On"])

@app.get("/")
def health_check():
    return {"status": "Backend running successfully"}
