from datetime import date, timedelta

from app import models


def register(client, email="user@example.com", password="123456"):
    return client.post(
        "/api/auth/register", json={"email": email, "password": password}
    )


def auth_headers(client, email="user@example.com", password="123456"):
    register(client, email, password)
    resp = client.post(
        "/api/auth/login", data={"username": email, "password": password}
    )
    return {"Authorization": f"Bearer {resp.json()['access_token']}"}


def make_admin(db, email):
    db.query(models.User).filter(models.User.email == email).update(
        {"role": models.Role.admin}
    )
    db.commit()


def test_register_success(client):
    resp = register(client)
    assert resp.status_code == 201
    data = resp.json()
    assert data["email"] == "user@example.com"
    assert data["role"] == "client"
    assert "password" not in data


def test_register_duplicate_email(client):
    register(client)
    resp = register(client)
    assert resp.status_code == 400


def test_login_wrong_password(client):
    register(client)
    resp = client.post(
        "/api/auth/login",
        data={"username": "user@example.com", "password": "wrong-password"},
    )
    assert resp.status_code == 401


def test_client_cannot_create_room(client):
    headers = auth_headers(client)
    resp = client.post(
        "/api/rooms",
        json={"name": "Люкс", "price_per_night": 80, "capacity": 2},
        headers=headers,
    )
    assert resp.status_code == 403


def test_booking_overlap(client, db):
    admin = auth_headers(client, "admin@example.com")
    make_admin(db, "admin@example.com")
    room = client.post(
        "/api/rooms",
        json={"name": "Люкс", "price_per_night": 80, "capacity": 2},
        headers=admin,
    ).json()

    guest = auth_headers(client, "guest@example.com")
    start = date.today() + timedelta(days=10)

    def book(check_in, check_out):
        return client.post(
            "/api/bookings",
            json={
                "room_id": room["id"],
                "check_in": str(check_in),
                "check_out": str(check_out),
            },
            headers=guest,
        )

    assert book(start, start + timedelta(days=5)).status_code == 201
    # пересечение дат
    assert book(start + timedelta(days=2), start + timedelta(days=4)).status_code == 409
    # заезд в день выезда предыдущего гостя
    assert book(start + timedelta(days=5), start + timedelta(days=7)).status_code == 201

    my = client.get("/api/bookings/my", headers=guest).json()
    assert len(my) == 2