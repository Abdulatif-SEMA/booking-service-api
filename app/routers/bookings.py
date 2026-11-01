from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app import models, schemas
from app.deps import get_current_user, get_db

router = APIRouter(prefix="/api/bookings", tags=["bookings"])


@router.post("", response_model=schemas.BookingOut, status_code=201)
def create_booking(
    data: schemas.BookingCreate,
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    if data.check_out <= data.check_in:
        raise HTTPException(400, "Дата выезда должна быть позже даты заезда")
    if data.check_in < date.today():
        raise HTTPException(400, "Нельзя бронировать на прошедшие даты")

    # блокируем строку номера, чтобы две брони одновременно не проскочили
    room = (
        db.query(models.Room)
        .filter(models.Room.id == data.room_id)
        .with_for_update()
        .first()
    )
    if room is None:
        raise HTTPException(404, "Номер не найден")

    conflict = (
        db.query(models.Booking)
        .filter(
            models.Booking.room_id == data.room_id,
            models.Booking.status == models.BookingStatus.active,
            models.Booking.check_in < data.check_out,
            models.Booking.check_out > data.check_in,
        )
        .first()
    )
    if conflict:
        raise HTTPException(409, "Номер занят на выбранные даты")

    booking = models.Booking(
        user_id=user.id,
        room_id=data.room_id,
        check_in=data.check_in,
        check_out=data.check_out,
    )
    db.add(booking)
    db.commit()
    db.refresh(booking)
    return booking


@router.get("/my", response_model=list[schemas.BookingOut])
def my_bookings(
    db: Session = Depends(get_db),
    user: models.User = Depends(get_current_user),
):
    return (
        db.query(models.Booking)
        .filter(
            models.Booking.user_id == user.id,
            models.Booking.status == models.BookingStatus.active,
        )
        .order_by(models.Booking.check_in)
        .all()
    )