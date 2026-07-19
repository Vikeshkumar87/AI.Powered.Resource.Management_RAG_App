# Frontend React README

This document covers frontend setup, development, and build/deploy flow.

## Tech Stack

- React 19
- Vite

## Install Dependencies

```powershell
cd frontend-react
npm install
```

If `npm` is not available in your shell, use:

```powershell
& 'C:\Program Files\nodejs\npm.cmd' install
```

## Run Frontend in Development Mode

```powershell
npm run dev
```

Default URL: `http://localhost:5173`

In development, `/api/*` calls are proxied to backend `http://localhost:8000` by `vite.config.js`.

## Build Frontend for FastAPI Serving

```powershell
npm run build
```

Build output is generated in `frontend-react/dist`.

FastAPI serves this build at `http://127.0.0.1:8000/` when backend is running.

## Optional Preview

```powershell
npm run preview
```

## Common Workflow

1. Start backend from project root.
2. Start frontend dev server in `frontend-react`.
3. Develop and verify pages/components.
4. Run `npm run build` before production/backend-served usage.

## One-Command Startup

From repo root:

```powershell
powershell -NoProfile -ExecutionPolicy Bypass -File .\scripts\start-all.ps1 -FrontendMode dev
```
