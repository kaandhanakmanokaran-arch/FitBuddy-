# FitBuddy – AI Fitness Plan Generator

FitBuddy is a FastAPI + SQLite + Jinja2 web application based on the supplied project documentation. It accepts a user's basic fitness information, generates a structured 7-day plan, provides a nutrition/recovery tip, and can revise the plan from feedback.

## Important implementation note

The supplied document names Gemini 1.5 Pro and Gemini Flash. Those model names are from an older Gemini generation. This implementation uses Google's current `google-genai` Python SDK and configurable current model names. By default both roles use `gemini-3.8-flash`; change `GEMINI_WORKOUT_MODEL` and `GEMINI_TIP_MODEL` in `.env` if your Google AI account exposes another supported model.

The app also has a safe local demo mode. If `GEMINI_API_KEY` is empty, the application uses deterministic demo content so you can test the full UI/database/API flow without an API key.

## Features

- FastAPI backend
- Jinja2 server-rendered frontend
- SQLite + SQLAlchemy persistence
- Gemini integration through `google-genai`
- 7-day workout generation
- Nutrition/recovery tip generation
- Feedback-based plan revision
- Admin-style all-users dashboard
- JSON API endpoints under `/api`
- Input validation and friendly error pages
- Local demo mode when Gemini is not configured
- Automated tests for health, validation, persistence and API flows

## Project structure

```text
FitBuddy/
├── app/
│   ├── __init__.py
│   ├── main.py
│   ├── config.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routes.py
│   ├── safety.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── gemini_client.py
│   │   ├── gemini_generator.py
│   │   ├── gemini_flash_generator.py
│   │   └── updated_plan.py
│   ├── templates/
│   │   ├── base.html
│   │   ├── index.html
│   │   ├── result.html
│   │   ├── all_users.html
│   │   └── error.html
│   └── static/
│       ├── css/style.css
│       └── js/app.js
├── tests/
│   ├── conftest.py
│   ├── test_health.py
│   ├── test_validation.py
│   └── test_web_flow.py
├── .env.example
├── .gitignore
├── requirements.txt
├── run.bat
├── run.sh
└── README.md
```

## Windows VS Code setup

1. Open this `FitBuddy` folder in VS Code.
2. Open **Terminal → New Terminal**.
3. Create the virtual environment:

```powershell
python -m venv .venv
```

4. Activate it:

```powershell
.venv\Scripts\Activate.ps1
```

If PowerShell blocks activation, use:

```powershell
.venv\Scripts\python.exe -m pip install --upgrade pip
```

and run all commands with `.venv\Scripts\python.exe`.

5. Install dependencies:

```powershell
python -m pip install -r requirements.txt
```

6. Create `.env` from `.env.example`:

```powershell
Copy-Item .env.example .env
```

7. For real Gemini generation, open `.env` and put your key in:

```text
GEMINI_API_KEY=your_key_here
```

For a first local test, you can leave it empty. The app will run in DEMO mode.

8. Start the server:

```powershell
python -m uvicorn app.main:app --reload
```

9. Open:

- App: http://127.0.0.1:8000
- API docs: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc
- Admin view: http://127.0.0.1:8000/view-all-users

## Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
cp .env.example .env
python -m uvicorn app.main:app --reload
```

## Test

With the virtual environment active:

```powershell
python -m pytest -q
```

## API examples

### Generate

`POST /api/workout`

JSON:

```json
{
  "username": "Demo User",
  "user_id": "demo-001",
  "age": 25,
  "weight": 65,
  "goal": "general wellness",
  "intensity": "medium"
}
```

### Update

`POST /api/feedback`

```json
{
  "user_id": "demo-001",
  "feedback": "Please add more flexibility work and keep one full rest day."
}
```

### Tip

`GET /api/tip/general%20wellness`

## Safety

FitBuddy is an educational wellness-planning application, not a medical diagnosis or treatment system. The generated plan should not be used to diagnose, treat, or manage a medical condition. The prompts explicitly avoid dangerous or extreme recommendations. For users under 18, the AI prompt focuses on general movement, wellbeing, recovery and healthy habits rather than weight-loss/body-composition targets.

## Troubleshooting

### `python` is not recognized

Install Python and reopen VS Code. Then verify:

```powershell
python --version
```

### Gemini errors

Check:

```text
GEMINI_API_KEY=...
```

and verify the selected model is available to your account. The app returns a friendly error and does not expose the key.

### Port already in use

```powershell
python -m uvicorn app.main:app --reload --port 8001
```

Then open http://127.0.0.1:8001.

### Reset the local database

Stop the server and delete `fitbuddy.db`. Start the server again; tables are recreated automatically.
