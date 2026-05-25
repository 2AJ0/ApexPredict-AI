# ApexPredict AI

ApexPredict AI is a Python-based motorsport strategy assistant for an F1 innovation challenge.  
It ingests live (mock) telemetry, evaluates race context, and produces pit-stop recommendations aimed at shaving off crucial lap-time milliseconds.

## Problem Statement

In modern Formula 1, race outcomes can hinge on tiny strategy decisions made under uncertainty.  
Teams need rapid recommendations that combine tire degradation, pace trend, and weather risk to decide:

- **Pit now**
- **Delay the stop by 1-2 laps**
- **Stay out and preserve track position**

ApexPredict AI demonstrates how AI-assisted strategy can support these decisions in real time.

## Technical Approach

### 1) FastAPI backend (telemetry + recommendations)

Implemented in `/home/runner/work/ApexPredict-AI/ApexPredict-AI/app/main.py`:

- `POST /telemetry`  
  Accepts mock telemetry payload:
  - `tire_wear` (0-100)
  - `lap_time_ms` (integer)
  - `weather_status` (string)
- `GET /recommendation`  
  Uses the most recent telemetry packet to generate a pit recommendation.
- `GET /`  
  Serves a lightweight dashboard.

### 2) IBM Granite integration (with Langflow-style strategy object)

Implemented in `/home/runner/work/ApexPredict-AI/ApexPredict-AI/app/granite_integration.py`:

- `granite_recommendation(payload)` calls IBM Granite via API when credentials are available:
  - `IBM_GRANITE_API_KEY`
  - `IBM_GRANITE_API_URL` (optional override)
  - `IBM_GRANITE_MODEL_ID` (optional override)
- If credentials are missing or the API call fails, the app uses deterministic fallback strategy logic so the demo still runs.
- `LangflowGraniteStrategy` provides a clean integration surface for Langflow node output.

Also included:

- `/home/runner/work/ApexPredict-AI/ApexPredict-AI/langflow_granite_integration.py`  
  A runnable integration script that takes telemetry arguments and prints prediction JSON.

### 3) Basic HTML + Tailwind dashboard

Implemented in `/home/runner/work/ApexPredict-AI/ApexPredict-AI/app/templates/index.html`:

- Simple telemetry input form
- Live recommendation panel
- Auto-refreshes recommendation every 5 seconds

## Why This Matters in Racing

Even a **50-150 ms per lap** pace swing can decide:

- Undercut/overcut success
- DRS train breakouts
- Late-race position changes

By combining telemetry with AI-generated strategy guidance, ApexPredict AI demonstrates a practical decision-support layer for race engineers and strategists.

## Run Locally

```bash
cd /home/runner/work/ApexPredict-AI/ApexPredict-AI
python -m pip install -r requirements.txt
uvicorn app.main:app --reload
```

Open:

- Dashboard: `http://127.0.0.1:8000/`
- API docs: `http://127.0.0.1:8000/docs`

## Optional: IBM Granite Configuration

Set environment variables before launching:

```bash
export IBM_GRANITE_API_KEY="your-token"
export IBM_GRANITE_API_URL="https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29"
export IBM_GRANITE_MODEL_ID="ibm/granite-13b-instruct-v2"
```

## Run Tests

```bash
cd /home/runner/work/ApexPredict-AI/ApexPredict-AI
python -m unittest discover -s tests -v
```
