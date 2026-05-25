import unittest

from app.granite_integration import granite_recommendation


class GraniteIntegrationTests(unittest.TestCase):
    def test_recommendation_pit_now_on_high_tire_wear(self):
        recommendation = granite_recommendation(
            {"tire_wear": 78, "lap_time_ms": 92100, "weather_status": "clear"}
        )
        self.assertIn("Pit now", recommendation)

    def test_recommendation_stay_out_on_healthy_tires(self):
        recommendation = granite_recommendation(
            {"tire_wear": 30, "lap_time_ms": 91000, "weather_status": "clear"}
        )
        self.assertIn("Stay out", recommendation)


if __name__ == "__main__":
    unittest.main()
