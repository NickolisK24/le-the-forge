# Local Development

This guide covers the PowerShell path for running the app locally on Windows.

## Prerequisites

- Python 3.11 or newer. Python 3.11 is the production version.
- Node.js 20 or newer.
- Docker Desktop if you want Docker-managed PostgreSQL and Redis.

## Backend Environment

From the repo root:

```powershell
Copy-Item .env.example .env
```

If you use Docker Compose for PostgreSQL, keep:

```powershell
DATABASE_URL=postgresql://forge:forgedev@127.0.0.1:5433/the_forge
```

If you use a separately installed local PostgreSQL on the default port, use:

```powershell
DATABASE_URL=postgresql://forge:forgedev@127.0.0.1:5432/the_forge
```

Redis is optional for local startup. If Redis is not running, the backend falls back to in-memory rate limiting.

## Create the Backend Virtual Environment

```powershell
cd D:\Forge\le-the-forge
py -3.11 -m venv backend\.venv
.\backend\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
python -m pip install -r backend\requirements.txt
```

If Python 3.11 is not registered with `py`, use the Python launcher or full interpreter path available on your machine.

## Start PostgreSQL and Redis with Docker

```powershell
cd D:\Forge\le-the-forge
docker compose up -d db redis
docker compose ps
```

Docker Compose maps PostgreSQL to `127.0.0.1:5433` and Redis to `127.0.0.1:6379`.

Quick port checks:

```powershell
Test-NetConnection 127.0.0.1 -Port 5433
Test-NetConnection 127.0.0.1 -Port 6379
```

## Run Database Migrations and Seed Data

```powershell
cd D:\Forge\le-the-forge\backend
$env:FLASK_APP = "wsgi.py"
$env:FLASK_ENV = "development"
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m flask db upgrade
.\.venv\Scripts\python.exe -m flask seed
.\.venv\Scripts\python.exe -m flask seed-passives
```

If you run from the repo root, the Windows npm shortcuts are:

```powershell
npm run db:upgrade:win
npm run db:seed:win
```

## Start the Backend

```powershell
cd D:\Forge\le-the-forge\backend
$env:FLASK_APP = "wsgi.py"
$env:FLASK_ENV = "development"
$env:PYTHONPATH = "."
.\.venv\Scripts\python.exe -m flask run --port=5050 --debug
```

Repo-root shortcut:

```powershell
cd D:\Forge\le-the-forge
npm run dev:backend:win
```

The backend API should be available at:

```text
http://localhost:5050/api
```

## Test the Backend Health Endpoint

In a second PowerShell window:

```powershell
Invoke-RestMethod http://127.0.0.1:5050/api/health
```

Expected response includes:

```text
status: ok
version: 0.8.0
```

## Start the Frontend

Local frontend development should use the Vite proxy. Keep `frontend\.env.local` unset or set:

```powershell
VITE_API_BASE_URL=/api
```

Then start Vite:

```powershell
cd D:\Forge\le-the-forge\frontend
npm install
npm run dev
```

The frontend should be available at:

```text
http://localhost:5173
```

Proxy health check:

```powershell
Invoke-RestMethod http://127.0.0.1:5173/api/health
```

## Common Troubleshooting

### `FLASK_APP is not recognized`

That happens when Unix-style environment variable syntax is run through Windows npm. Use the PowerShell commands above or:

```powershell
npm run dev:backend:win
```

### Frontend proxies to the wrong backend port

Check `frontend\.env.local`. If it points at an old backend such as `http://127.0.0.1:5001/api`, replace it with:

```powershell
VITE_API_BASE_URL=/api
```

Then restart Vite.

### PostgreSQL connection refused

Check which database path you are using:

```powershell
Select-String -Path .env -Pattern "DATABASE_URL"
Test-NetConnection 127.0.0.1 -Port 5433
Test-NetConnection 127.0.0.1 -Port 5432
```

Use port `5433` for Docker Compose PostgreSQL, or `5432` for a separately installed local PostgreSQL.

### Redis unavailable warning

This warning is acceptable for local development:

```text
Redis unavailable for rate limiting - falling back to in-memory storage.
```

Start Redis with Docker Compose if you want to remove it:

```powershell
docker compose up -d redis
```

### Port 5050 already in use

```powershell
Get-NetTCPConnection -LocalPort 5050 -ErrorAction SilentlyContinue
```

Stop the process using that port, or start Flask on a different port and update the Vite proxy target.
