from fastapi import FastAPI
from .auth.router import auth_router, register_router
from .tickets.router import router as tickets_router

app = FastAPI()

app.include_router(
    auth_router,
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    register_router,
    prefix="/auth",
    tags=["auth"],
)
app.include_router(
    tickets_router,
    prefix="/tickets",
    tags=["tickets"],
)
