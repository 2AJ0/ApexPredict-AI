from dataclasses import asdict
from datetime import datetime, timezone
from pathlib import Path
from typing import List

from fastapi import FastAPI
from fastapi.responses import HTMLResponse
from pydantic import BaseModel, Field

from app.granite_integration import LangflowGraniteStrategy, TelemetryPoint

app = FastAPI(title="ApexPredict AI")
strategy_engine = LangflowGraniteStrategy()
telemetry_store: List[dict] = []


class TelemetryIn(BaseModel):
    tire_wear: float = Field(ge=0, le=100)
    lap_time_ms: int = Field(gt=0)
    weather_status: str


@app.post("/telemetry")
def ingest_telemetry(point: TelemetryIn):
    telemetry = TelemetryPoint(
        tire_wear=point.tire_wear,
        lap_time_ms=point.lap_time_ms,
        weather_status=point.weather_status,
    )
    stored = asdict(telemetry)
    stored["received_at"] = datetime.now(timezone.utc).isoformat()
    telemetry_store.append(stored)
    return {"status": "ingested", "telemetry": stored}


@app.get("/recommendation")
def get_recommendation():
    if not telemetry_store:
        return {
            "recommendation": "No telemetry yet. Submit data to /telemetry to start optimization.",
            "latest_telemetry": None,
        }
    latest = telemetry_store[-1]
    recommendation = strategy_engine.run(
        TelemetryPoint(
            tire_wear=latest["tire_wear"],
            lap_time_ms=latest["lap_time_ms"],
            weather_status=latest["weather_status"],
        )
    )
    return {"recommendation": recommendation, "latest_telemetry": latest}


@app.get("/", response_class=HTMLResponse)
def dashboard():
    template_path = Path(__file__).parent / "templates" / "index.html"
    return template_path.read_text(encoding="utf-8")
