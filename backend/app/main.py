from fastapi import FastAPI

from app.api.router import api_router

app = FastAPI(title="CyberGuard API")


@app.get("/")
async def root():
    return {"message": "CyberGuard API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}


app.include_router(api_router, prefix="/api/v1")