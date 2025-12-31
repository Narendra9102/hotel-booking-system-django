# 🏨 Hotel Room Booking System

**Django + Django Rest Framework (DRF)**

---

## 📌 Project Overview

This project is a **Hotel Room Booking System** built using **Django and Django Rest Framework (DRF)**.

The system allows users to:

* Search available hotel rooms
* Book rooms on an **hourly or daily** basis
* Prevent **overlapping (double) bookings**
* Perform booking lifecycle actions:

  * Check-in
  * Check-out
  * Cancel booking
* View booking history

The project supports:

* **REST APIs** (for testing via Postman/Thunder Client)
* **Django Templates UI** (simple web interface)

Both API and UI use the **same backend business logic**.

---

## 🧠 Architecture & Design (Important)

### Core Design Principle

> **All business rules are enforced on the backend and reused everywhere.**

### Layers Used

```
Client (API / Browser)
        |
        v
Views (API views / Template views)
        |
        v
Service Layer (BookingService)
        |
        v
Models (Room, Booking)
        |
        v
Database (SQLite)
```

### Why this architecture?

* Prevents duplicate logic
* Ensures consistency between API and UI
* Prevents double booking globally
* Easy to extend (React / Mobile app later)
* Interview-ready and clean separation of concerns

---

## 📁 Project Structure

```
hotel_booking/
├── manage.py
├── hotel_booking/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
│
├── rooms/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py
│   ├── urls.py
│   ├── admin.py
│   └── management/
│       └── commands/
│           └── populate_rooms.py   # Management command
│
├── bookings/
│   ├── models.py
│   ├── serializers.py
│   ├── views.py              # DRF APIs
│   ├── frontend_views.py     # Template views
│   ├── frontend_urls.py
│   ├── services.py           # Business logic
│   └── admin.py
│
├── templates/
│   ├── base.html
│   ├── login.html
│   ├── register.html
│   ├── dashboard.html
│   ├── rooms.html
│   ├── book_room.html
│   └── my_bookings.html
│
└── db.sqlite3
```

---

## ⚙️ Setup Instructions (After Cloning)

### 1️. Clone the Repository

```bash
git clone <repository-url>
cd hotel_booking
```

---

### 2️. Create Virtual Environment

```bash
python -m venv venv
```

Activate it:

**Windows**

```bash
venv\Scripts\activate
```

**Linux / macOS**

```bash
source venv/bin/activate
```

---

### 3️. Install Required Packages

Only **Django and DRF** are required:

```bash
pip install django djangorestframework
```

---

### 4️. Run Database Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

---

### 5️. Create Superuser (Admin)

```bash
python manage.py createsuperuser
```

---

### 6️. Populate Sample Room Data (IMPORTANT)

A **custom Django management command** is provided to insert sample room data into the database.

#### Command Details

**File location**

```
rooms/management/commands/populate_rooms.py
```

**Run command**

```bash
python manage.py populate_rooms
```

👉 This will automatically create sample rooms in `db.sqlite3`.

---

### 7️. Run the Server

```bash
python manage.py runserver
```

---

## 🌐 Application Access

### Web Interface (Templates)

| Page        | URL                                                                      |
| ----------- | ------------------------------------------------------------------------ |
| Login       | [http://127.0.0.1:8000/](http://127.0.0.1:8000/)                         |
| Register    | [http://127.0.0.1:8000/register/](http://127.0.0.1:8000/register/)       |
| Dashboard   | [http://127.0.0.1:8000/dashboard/](http://127.0.0.1:8000/dashboard/)     |
| Rooms       | [http://127.0.0.1:8000/rooms/](http://127.0.0.1:8000/rooms/)             |
| My Bookings | [http://127.0.0.1:8000/my-bookings/](http://127.0.0.1:8000/my-bookings/) |

---

### API Endpoints (DRF)

| Feature                | Method | Endpoint                            |
| ---------------------- | ------ | ------------------------------------|
| Search Available Rooms | GET    | `/api/rooms/search-available/`      |
| Check Availability     | GET    | `/api/bookings/check-availability/` |
| Create Booking         | POST   | `/api/bookings/`                    |
| My Bookings            | GET    | `/api/bookings/`                    |
| Check-In               | POST   | `/api/bookings/{id}/checkin/`       |
| Check-Out              | POST   | `/api/bookings/{id}/checkout/`      |
| Cancel Booking         | POST   | `/api/bookings/{id}/cancel/`        |

---

## 🔐 Authentication

* **Web UI** → Django session authentication
* **API** → Token authentication

**API Header Example**

```
Authorization: Token <your_token>
```

---

## 🚫 Double Booking Prevention (Key Logic)

A room **cannot be booked** if:

* There is an existing booking with status:

  ```
  pending, confirmed, checked_in
  ```
* AND the time overlaps:

  ```
  existing.start_time < new.end_time
  AND
  existing.end_time > new.start_time
  ```

This logic is implemented in:

```
bookings/services.py → BookingService.check_room_availability()
```

Used by:

* Booking API
* Template booking flow

✔ One rule, enforced everywhere

---

## 🧪 Example Workflow

1. Admin runs `populate_rooms`
2. User A books Room 202 (10:00–14:00)
3. User B tries booking Room 202 (11:00–13:00)

   * ❌ Blocked
4. User A checks out
5. User B books same room

   * ✅ Allowed

---

