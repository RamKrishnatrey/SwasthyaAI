# SwasthyaAI

SwasthyaAI is a locally runnable application with a React/Vite frontend, a FastAPI backend, and a per-machine SQLite database.

## Requirements

- Windows 10/11
- Python 3.11 or 3.12 available as `python` in PowerShell
- Node.js LTS (includes `npm`)
- Internet access for the initial dependency installation. After setup, core local features run on the same computer; any configured external AI provider still needs internet and its own API key.

## Quick start (Windows)

Open PowerShell in the repository folder.

1. If PowerShell blocks local scripts, allow scripts for this terminal only:

   ```powershell
   Set-ExecutionPolicy -Scope Process Bypass
   ```

2. Install backend and frontend dependencies:

   ```powershell
   .\setup-local.ps1
   ```

3. Start the app:

   ```powershell
   .\run-local.ps1
   ```

Keep that terminal open. Open the frontend URL printed by Vite (typically `http://127.0.0.1:5173`). The backend runs at `http://127.0.0.1:8000`; its health endpoint is `http://127.0.0.1:8000/api/v1/health`. Press Ctrl+C to stop the frontend; the script also stops the backend it started.

If the frontend does not reach the backend, check its API base URL/configuration and ensure the backend health endpoint responds.

## Local database and data

- SQLite database path: `.local/swasthya.sqlite3`.
- The database schema is initialized automatically when a database-backed API endpoint is used.
- Every computer has its own local database. Cloning the repository does not copy your local records or accounts.
- Do not commit `.local/`, database files, real patient information, API keys, or `.env` files.

## Optional AI provider

The optional Gemini integration may require `GEMINI_API_KEY` in the environment. Each developer must configure their own key; never put a real key in GitHub. Features that use an external provider require internet access.

## Saved urgency models

The `artifacts/` directory includes experimental saved urgency-classification pipelines and evaluation metrics. These files are not automatically integrated into the existing agent. The README does not claim clinical validation: this project is not a medical device, and its outputs are not a diagnosis. Do not use it for real clinical decisions or enter real patient data. Emergency symptoms require contacting local emergency services.
