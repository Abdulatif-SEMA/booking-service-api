from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_db, require_admin

router = APIRouter(prefix="/api/rooms", tags=["rooms"])


@router.get("", response_model=list[schemas.RoomOut])
def list_rooms(
    min_price: float | None = None,
    max_price: float | None = None,
    guests: int | None = None,
    check_in: date | None = None,
    check_out: date | None = None,
    db: Session = Depends(get_db),
):
    query = db.query(models.Room)

    if min_price is not None:
        query = query.filter(models.Room.price_per_night >= min_price)
    if max_price is not None:
        query = query.filter(models.Room.price_per_night <= max_price)
    if guests is not None:
        query = query.filter(models.Room.capacity >= guests)

    if check_in and check_out:
        if check_out <= check_in:
            raise HTTPException(400, "Дата выезда должна быть позже даты заезда")
        busy_rooms = select(models.Booking.room_id).where(
            models.Booking.status == models.BookingStatus.active,
            models.Booking.check_in < check_out,
            models.Booking.check_out > check_in,
        )
        query = query.filter(models.Room.id.not_in(busy_rooms))

    return query.order_by(models.Room.id).all()


@router.post("", response_model=schemas.RoomOut, status_code=201)
def create_room(
    data: schemas.RoomCreate,
    db: Session = Depends(get_db),
    _: models.User = Depends(require_admin),
):
    room = models.Room(**data.model_dump())
    db.add(room)
    db.commit()
    db.refresh(room)
    return room