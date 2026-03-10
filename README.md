# BE Social Media API

A fully featured REST API built with Django and Django REST Framework that simulates a real-world social media backend. It supports user management, post creation, a follow system, a personalized feed, likes, comments, and reposts.

---

## 🛠 Tech Stack

- **Python 3**
- **Django 4.2.7**
- **Django REST Framework**
- **JWT Authentication** (djangorestframework-simplejwt)
- **SQLite** (development database)
- **Whitenoise** (static files)
- **Django CORS Headers**

---

## 📁 Project Structure
```
BE-Social-Media-API/
├── apps/
│   ├── users/        # User model, authentication, follow system
│   ├── posts/        # Post CRUD, likes, comments, reposts
│   └── feed/         # Personalized feed and trending posts
├── socialmedia_api/  # Django project settings, urls, wsgi
├── manage.py
├── requirements.txt
└── .env
```

---

## ⚙️ Local Setup

### 1. Clone the repository
```bash
git clone https://github.com/deyonavoseh/BE-Social-Media-API.git
cd BE-Social-Media-API
```

### 2. Create and activate virtual environment
```bash
python -m venv venv
source venv/Scripts/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 4. Generate secret key and create .env file
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```
Create a `.env` file in the root folder:
```
SECRET_KEY=your_generated_key_here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1
```

### 5. Run migrations
```bash
python manage.py makemigrations users posts
python manage.py migrate
```

### 6. Create superuser
```bash
python manage.py createsuperuser
```

### 7. Start the server
```bash
python manage.py runserver
```

API is running at: `http://127.0.0.1:8000`

---

## 🔐 Authentication

This API uses **JWT (JSON Web Tokens)**. After logging in, include the token in every request:
```
Authorization: Bearer <your_access_token>
```

---

## 🧪 API Testing — Step by Step

All tests were performed using **Postman**.

---

### Step 1 — Register a User
**POST** `/api/users/register/`

Created a new user by sending a POST request with username, email, password and bio.
```json
{
    "username": "alice",
    "email": "alice@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!",
    "bio": "Hello I am Alice"
}
```
✅ Response: `201 Created` — returned the new user object with id, username, email and profile fields.

---

### Step 2 — Login and Get JWT Token
**POST** `/api/auth/login/`

Logged in with the registered user's email and password.
```json
{
    "email": "alice@example.com",
    "password": "SecurePass123!"
}
```
✅ Response: `200 OK` — returned an `access` token and a `refresh` token. The access token is used in all subsequent requests via the Authorization header as a Bearer Token.

---

### Step 3 — View Own Profile
**GET** `/api/users/me/`

Sent a GET request with the Bearer Token in the Authorization header.

✅ Response: `200 OK` — returned the authenticated user's full profile including:
- `id`, `username`, `email`, `bio`
- `followers_count: 0`
- `following_count: 0`
- `posts_count: 0`

---

### Step 4 — Create a Post
**POST** `/api/posts/`

Sent a POST request with the Bearer Token and post content.
```json
{
    "content": "My first post!"
}
```
✅ Response: `201 Created` — returned the full post object with id, user, content, likes count and comments count.

---

### Step 5 — View All Posts
**GET** `/api/posts/`

Sent a GET request to retrieve all posts in the system.

✅ Response: `200 OK` — returned a paginated list of all posts in reverse chronological order.

---

### Step 6 — Register a Second User
**POST** `/api/users/register/`

Registered a second user to test the follow system.
```json
{
    "username": "bob",
    "email": "bob@example.com",
    "password": "SecurePass123!",
    "password2": "SecurePass123!"
}
```
✅ Response: `201 Created`

---

### Step 7 — Follow a User
**POST** `/api/users/bob/follow/`

Using alice's Bearer Token, sent a POST request to follow bob.

✅ Response: `201 Created` — "Now following @bob"

The follow relationship was created in the database, and alice's `following_count` increased to 1.

---

### Step 8 — View Followers and Following
**GET** `/api/users/alice/following/`

Checked who alice is following.

✅ Response: `200 OK` — returned bob's profile in the list.

**GET** `/api/users/bob/followers/`

Checked who follows bob.

✅ Response: `200 OK` — returned alice's profile in the list.

---

### Step 9 — View Personalized Feed
**GET** `/api/feed/`

Using alice's token, fetched the feed which shows posts only from users alice follows.

✅ Response: `200 OK` — returned bob's posts in reverse chronological order. Confirmed that the feed only shows posts from followed users.

---

### Step 10 — Like a Post
**POST** `/api/posts/1/like/`

Sent a POST request to like a post.

✅ Response: `201 Created` — "Post liked." with updated `likes_count`.

---

### Step 11 — Comment on a Post
**POST** `/api/posts/1/comments/`
```json
{
    "content": "Great post!"
}
```
✅ Response: `201 Created` — returned the comment with user and timestamp.

---

### Step 12 — View Trending Posts
**GET** `/api/feed/trending/`

Fetched trending posts from the last 7 days ordered by most likes.

✅ Response: `200 OK` — returned posts sorted by like count.

---

### Step 13 — Unfollow a User
**DELETE** `/api/users/bob/follow/`

✅ Response: `200 OK` — "Unfollowed @bob"

---

### Step 14 — Delete a Post (Owner Only)
**DELETE** `/api/posts/1/`

Only the owner of the post can delete it. Trying to delete another user's post returns `403 Forbidden`.

✅ Response: `204 No Content`

---

## 📋 Full API Reference

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| POST | `/api/users/register/` | ❌ | Register new user |
| POST | `/api/auth/login/` | ❌ | Login and get JWT tokens |
| POST | `/api/auth/refresh/` | ❌ | Refresh access token |
| POST | `/api/auth/logout/` | ✅ | Logout and blacklist token |
| GET | `/api/users/me/` | ✅ | View own profile |
| PUT | `/api/users/me/` | ✅ | Update own profile |
| DELETE | `/api/users/me/` | ✅ | Delete own account |
| POST | `/api/users/me/change-password/` | ✅ | Change password |
| GET | `/api/users/` | ✅ | List all users |
| GET | `/api/users/<username>/` | ✅ | View a user's profile |
| POST | `/api/users/<username>/follow/` | ✅ | Follow a user |
| DELETE | `/api/users/<username>/follow/` | ✅ | Unfollow a user |
| GET | `/api/users/<username>/followers/` | ✅ | List user's followers |
| GET | `/api/users/<username>/following/` | ✅ | List user's following |
| GET | `/api/posts/` | ✅ | List all posts |
| POST | `/api/posts/` | ✅ | Create a post |
| GET | `/api/posts/<id>/` | ✅ | Get a single post |
| PUT | `/api/posts/<id>/` | ✅ owner | Update a post |
| DELETE | `/api/posts/<id>/` | ✅ owner | Delete a post |
| GET | `/api/posts/user/<username>/` | ✅ | All posts by a user |
| POST | `/api/posts/<id>/like/` | ✅ | Like a post |
| DELETE | `/api/posts/<id>/like/` | ✅ | Unlike a post |
| GET | `/api/posts/<id>/comments/` | ✅ | List comments on a post |
| POST | `/api/posts/<id>/comments/` | ✅ | Add a comment |
| DELETE | `/api/posts/<id>/comments/<id>/` | ✅ owner | Delete a comment |
| POST | `/api/posts/<id>/repost/` | ✅ | Repost a post |
| GET | `/api/feed/` | ✅ | View personalized feed |
| GET | `/api/feed/trending/` | ✅ | View trending posts |