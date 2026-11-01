from fastapi import FastAPI

from app.database import Base, engine
from app import models  # noqa: F401
from app.routers import auth, bookings, rooms

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Booking Service API")
app.include_router(auth.router)
app.include_router(rooms.router)
app.include_router(bookings.router)


@app.get("/")
def root():
    return {"message": "API работает"}