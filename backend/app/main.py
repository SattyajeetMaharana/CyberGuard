from fastapi import FastAPI

app = FastAPI(title="CyberGuard API")


@app.get("/")
async def root():
    return {"message": "CyberGuard API is running"}


@app.get("/health")
async def health():
    return {"status": "healthy"}