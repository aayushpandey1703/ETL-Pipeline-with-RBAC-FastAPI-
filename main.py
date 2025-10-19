from fastapi import FastAPI
from fastapi.responses import JSONResponse
from models.database import engine,Base
from routes.user import route
from routes.auth import auth_router

app=FastAPI(
    title="my app",
    version="1.0.0",
    docs_url="/doc2",
    redoc_url="/redoc2"
)

@app.on_event("startup")
async def create_tables():
    async with engine.begin() as con:
        await con.run_sync(Base.metadata.create_all)


app.include_router(auth_router)
app.include_router(route)

