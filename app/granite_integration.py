import json
import os
from dataclasses import dataclass, asdict
from typing import Any, Dict, List
from urllib import error, request


@dataclass
class TelemetryPoint:
    tire_wear: float
    lap_time_ms: int
    weather_status: str


def _fallback_recommendation(payload: Dict[str, Any]) -> str:
    tire_wear = float(payload["tire_wear"])
    lap_time_ms = int(payload["lap_time_ms"])
    weather = str(payload["weather_status"]).lower()

    if tire_wear >= 70 or "rain" in weather:
        return (
            "Pit now for fresh intermediates. "
            "Projected gain: 180-320 ms/lap over the next 5 laps."
        )
    if lap_time_ms > 93000:
        return (
            "Box within 2 laps for softs to recover pace. "
            "Projected gain: 90-140 ms/lap."
        )
    return "Stay out. Tire degradation is manageable and pace delta is under 60 ms/lap."


def _extract_granite_text(response_payload: Dict[str, Any]) -> str:
    candidates: List[Any] = response_payload.get("results", [])
    if candidates:
        candidate = candidates[0]
        generated = candidate.get("generated_text")
        if generated:
            return str(generated).strip()
    return "No recommendation returned by IBM Granite."


def granite_recommendation(payload: Dict[str, Any]) -> str:
    """
    Calls IBM Granite text generation API for pit strategy guidance.
    Falls back to local deterministic strategy logic if API credentials are missing
    or the API call fails.
    """
    api_key = os.getenv("IBM_GRANITE_API_KEY")
    api_url = os.getenv(
        "IBM_GRANITE_API_URL",
        "https://us-south.ml.cloud.ibm.com/ml/v1/text/generation?version=2023-05-29",
    )
    model_id = os.getenv("IBM_GRANITE_MODEL_ID", "ibm/granite-13b-instruct-v2")

    if not api_key:
        return _fallback_recommendation(payload)

    prompt = (
        "You are an F1 race strategist. Given telemetry, produce one concise pit "
        "recommendation and expected lap-time gain in milliseconds.\n"
        f"Telemetry: {json.dumps(payload)}"
    )
    granite_payload = {
        "model_id": model_id,
        "input": prompt,
        "parameters": {"max_new_tokens": 120, "decoding_method": "greedy"},
    }
    req = request.Request(
        api_url,
        data=json.dumps(granite_payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )

    try:
        with request.urlopen(req, timeout=15) as response:
            data = json.loads(response.read().decode("utf-8"))
            return _extract_granite_text(data)
    except (error.URLError, TimeoutError, json.JSONDecodeError, KeyError):
        return _fallback_recommendation(payload)


class LangflowGraniteStrategy:
    """
    Minimal integration object to connect a Langflow node output with IBM Granite.
    """

    def run(self, telemetry: TelemetryPoint) -> str:
        return granite_recommendation(asdict(telemetry))
