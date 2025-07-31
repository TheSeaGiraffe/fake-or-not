from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.controllers import predictions, users
from app.services.model import cleanup_model, init_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_model()
    yield
    cleanup_model()


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(predictions.router)
