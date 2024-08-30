import uvicorn
import logging
from fastapi import FastAPI
from fastapi.responses import RedirectResponse
from app.api import auth, profile

app = FastAPI()

@app.get("/")
async def redirect_to_docs():
    return RedirectResponse(url="/docs")

app.include_router(auth.router)
app.include_router(profile.router)

if __name__ == "__main__":
#    logging.basicConfig(level=logging.DEBUG)
#    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="debug")
    uvicorn.run(app, host="0.0.0.0", port=8000)