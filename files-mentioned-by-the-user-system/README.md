# Chess LMS

Production-oriented Chess Learning Management System built incrementally from the architecture in `outputs/Chess-LMS-Technical-Design.md`.

## Current Milestone

Milestones 1-3: project skeleton, database foundation, and authentication.

Included:

- FastAPI backend with health and readiness endpoints.
- Next.js frontend shell.
- Docker Compose development stack with PostgreSQL, Redis, Mailpit, API, and frontend.
- Environment variable examples.
- SQLAlchemy base models for organizations and users.
- Alembic migration wiring and first identity migration.
- Teacher/student registration.
- Login, access tokens, refresh token storage, refresh rotation, logout, and `/auth/me`.

## Local Development

Copy the development environment template:

```powershell
Copy-Item .env.development.example .env
```

Start the stack:

```powershell
docker compose --env-file .env -f docker-compose.yml -f docker-compose.dev.yml up --build
```

Useful URLs:

- Frontend: http://localhost:3000
- API health: http://localhost:8000/health
- API readiness: http://localhost:8000/ready
- API docs: http://localhost:8000/docs
- Mailpit: http://localhost:8025

## Backend Setup Without Docker

From `backend/`:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

Run migrations when PostgreSQL is available:

```powershell
alembic upgrade head
```

## Auth Smoke Test

Register a teacher:

```powershell
$body = @{
  email = "teacher@example.com"
  password = "StrongPass123"
  display_name = "Coach Demo"
} | ConvertTo-Json

$auth = Invoke-RestMethod `
  -Method Post `
  -Uri "http://localhost:8000/api/v1/auth/register/teacher" `
  -ContentType "application/json" `
  -Body $body

$auth.access_token
```

Fetch the current user:

```powershell
Invoke-RestMethod `
  -Method Get `
  -Uri "http://localhost:8000/api/v1/auth/me" `
  -Headers @{ Authorization = "Bearer $($auth.access_token)" }
```

Use the website flow:

1. Open http://localhost:3000
2. Click `Create account`
3. Register as teacher or student
4. Confirm you land on `/dashboard`

## Project Structure

```text
backend/
  app/
    main.py
    core/
      config.py
      logging.py
frontend/
  app/
    layout.tsx
    page.tsx
docker-compose.yml
docker-compose.dev.yml
```

## Next Milestone

Milestone 4 will add email verification and password reset.
