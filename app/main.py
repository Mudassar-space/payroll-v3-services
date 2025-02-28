__author__ = "Muhammad Qasim Khan"
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi_pagination import add_pagination

from app.config import config
from app.controllers.router import router


DESCRIPTION = """
Payroll API helps you do manage Payroll data. 🚀

"""

app = FastAPI(title=config.PROJECT_NAME, description=DESCRIPTION)

# CORS
origins = ['https://localhost:3000', 'http://server']

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)


app.include_router(router)
add_pagination(app)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)

@app.get("/")
async def get_root():
    return {"message": "Payroll APIs version 0.1.0"}
