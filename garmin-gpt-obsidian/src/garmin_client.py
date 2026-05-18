from __future__ import annotations

import datetime as dt
import logging
from typing import Any


class GarminClient:
    def __init__(self, email: str, password: str, logger: logging.Logger, mock_mode: bool = False):
        self.email = email
        self.password = password
        self.logger = logger
        self.mock_mode = mock_mode
        self.client = None

    def login(self) -> None:
        if self.mock_mode:
            self.logger.info("Mock mode enabled. Skip Garmin login.")
            return

        try:
            from garminconnect import Garmin

            self.client = Garmin(self.email, self.password)
            self.client.login()
            self.logger.info("Garmin login succeeded.")
        except Exception as exc:
            self.logger.error("Garmin login failed. Possibly 2FA/session issue: %s", exc)
            raise

    def get_recent_7days_data(self, start_date: dt.date, end_date: dt.date) -> dict[str, Any]:
        if self.mock_mode:
            return self._mock_data(start_date, end_date)
        if self.client is None:
            raise RuntimeError("Garmin client not initialized. Call login() first.")

        daily = []
        activities = []
        missing = []

        for offset in range((end_date - start_date).days + 1):
            current = start_date + dt.timedelta(days=offset)
            date_str = current.isoformat()
            try:
                daily.append(
                    {
                        "date": date_str,
                        "sleep_hours": self._safe_wrapper(self.client.get_sleep_data, date_str, "sleep_hours", missing),
                        "sleep_score": self._safe_wrapper(self.client.get_sleep_score_data, date_str, "sleep_score", missing),
                        "hrv_status": self._safe_wrapper(self.client.get_hrv_data, date_str, "hrv_status", missing),
                        "resting_hr": self._safe_wrapper(self.client.get_rhr_day, date_str, "resting_hr", missing),
                        "stress": self._safe_wrapper(self.client.get_stress_data, date_str, "stress", missing),
                        "body_battery": self._safe_wrapper(self.client.get_body_battery, date_str, "body_battery", missing),
                        "steps": self._safe_wrapper(self.client.get_steps_data, date_str, "steps", missing),
                        "calories": self._safe_wrapper(self.client.get_stats, date_str, "calories", missing),
                        "vo2max": self._safe_wrapper(self.client.get_vo2max_data, date_str, "vo2max", missing),
                    }
                )
            except Exception as exc:
                self.logger.warning("Failed to fetch daily data for %s: %s", date_str, exc)

        try:
            activities = self.client.get_activities_by_date(start_date.isoformat(), end_date.isoformat())
        except Exception as exc:
            missing.append("activities")
            self.logger.warning("Failed to fetch activities: %s", exc)

        return {
            "meta": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat()},
            "daily": daily,
            "activities": activities,
            "garmin_predictions": None,
            "missing_fields": sorted(set(missing)),
        }

    def _safe_wrapper(self, func, date_str: str, field_name: str, missing: list[str]):
        try:
            return func(date_str)
        except Exception:
            missing.append(field_name)
            return None

    def _mock_data(self, start_date: dt.date, end_date: dt.date) -> dict[str, Any]:
        daily = []
        for i in range((end_date - start_date).days + 1):
            current = start_date + dt.timedelta(days=i)
            daily.append(
                {
                    "date": current.isoformat(),
                    "sleep_hours": 6.5 + (i % 3) * 0.4,
                    "sleep_score": 72 + i,
                    "hrv_status": {"status": "balanced", "value": 48 + i},
                    "resting_hr": 54 + (i % 2),
                    "stress": {"avg": 31 + i},
                    "body_battery": {"charged": 76 - i, "drained": 41 + i},
                    "steps": 9000 + i * 500,
                    "calories": 2250 + i * 40,
                    "vo2max": 50.0,
                }
            )

        activities = [
            {
                "activityName": "Easy Run",
                "activityType": {"typeKey": "running"},
                "startTimeLocal": (start_date + dt.timedelta(days=1)).isoformat() + " 07:00:00",
                "distance": 8000,
                "duration": 2700,
                "averageHR": 145,
                "maxHR": 168,
                "averageRunCadence": 166,
                "trainingEffectLabel": "Base",
                "averageSpeed": 2.96,
            },
            {
                "activityName": "Long Run",
                "activityType": {"typeKey": "running"},
                "startTimeLocal": (start_date + dt.timedelta(days=5)).isoformat() + " 06:30:00",
                "distance": 18000,
                "duration": 6660,
                "averageHR": 152,
                "maxHR": 176,
                "trainingEffectLabel": "Tempo",
                "averageSpeed": 2.7,
            },
        ]

        return {
            "meta": {"start_date": start_date.isoformat(), "end_date": end_date.isoformat(), "mock": True},
            "daily": daily,
            "activities": activities,
            "garmin_predictions": {
                "5k": "00:23:30",
                "10k": "00:49:40",
                "marathon": "03:58:00",
            },
            "missing_fields": ["recovery_time", "training_load"],
        }
