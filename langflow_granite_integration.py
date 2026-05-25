import argparse
import json

from app.granite_integration import LangflowGraniteStrategy, TelemetryPoint


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Langflow-to-IBM-Granite pit strategy integration helper."
    )
    parser.add_argument("--tire-wear", type=float, required=True)
    parser.add_argument("--lap-time-ms", type=int, required=True)
    parser.add_argument("--weather-status", type=str, required=True)
    args = parser.parse_args()

    strategy = LangflowGraniteStrategy()
    recommendation = strategy.run(
        TelemetryPoint(
            tire_wear=args.tire_wear,
            lap_time_ms=args.lap_time_ms,
            weather_status=args.weather_status,
        )
    )
    print(
        json.dumps(
            {
                "input": {
                    "tire_wear": args.tire_wear,
                    "lap_time_ms": args.lap_time_ms,
                    "weather_status": args.weather_status,
                },
                "recommendation": recommendation,
            },
            indent=2,
        )
    )


if __name__ == "__main__":
    main()
