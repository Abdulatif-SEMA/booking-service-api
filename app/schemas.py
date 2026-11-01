from datetime import date

from pydantic import BaseModel, ConfigDict, EmailStr, Field

from app.models import BookingStatus, Role


class UserCreate(BaseModel):
    email: EmailStr
    password: str = Field(min_length=6, max_length=72)


class UserOut(BaseModel):
    id: int
    email: EmailStr
    role: Role

    model_config = ConfigDict(from_attributes=True)


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RoomCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    description: str | None = Field(default=None, max_length=500)
    price_per_night: float = Field(gt=0)
    capacity: int = Field(ge=1)


class RoomOut(BaseModel):
    id: int
    name: str
    description: str | None
    price_per_night: float
    capacity: int

    model_config = ConfigDict(from_attributes=True)


class BookingCreate(BaseModel):
    room_id: int
    check_in: date
    check_out: date


class BookingOut(BaseModel):
    id: int
    room_id: int
    check_in: date
    check_out: date
    status: BookingStatus

    model_config = ConfigDict(from_attributes=True)