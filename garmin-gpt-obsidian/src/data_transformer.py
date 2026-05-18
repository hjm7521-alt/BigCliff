from __future__ import annotations

from typing import Any



def _avg(values: list[float]) -> float | None:
    return round(sum(values) / len(values), 2) if values else None


def transform_raw_to_processed(raw: dict[str, Any]) -> dict[str, Any]:
    daily = raw.get("daily", [])
    activities = raw.get("activities", [])

    sleep_values = [float(d.get("sleep_hours")) for d in daily if isinstance(d.get("sleep_hours"), (int, float))]
    resting_hr_values = [float(d.get("resting_hr")) for d in daily if isinstance(d.get("resting_hr"), (int, float))]

    running_activities = [a for a in activities if a.get("activityType", {}).get("typeKey") == "running"]

    total_exercise_seconds = sum(float(a.get("duration", 0) or 0) for a in activities)
    total_running_distance_m = sum(float(a.get("distance", 0) or 0) for a in running_activities)

    avg_pace_sec_per_km_values = []
    for a in running_activities:
        dist = float(a.get("distance", 0) or 0)
        dur = float(a.get("duration", 0) or 0)
        if dist > 0 and dur > 0:
            avg_pace_sec_per_km_values.append((dur / dist) * 1000)

    high_intensity_count = 0
    for a in activities:
        te = str(a.get("trainingEffectLabel", "")).lower()
        avg_hr = a.get("averageHR")
        if te in {"tempo", "threshold", "vo2max", "anaerobic"} or (isinstance(avg_hr, (int, float)) and avg_hr >= 160):
            high_intensity_count += 1

    missing_fields = set(raw.get("missing_fields", []))

    return {
        "period": raw.get("meta", {}),
        "weekly_summary": {
            "total_workouts": len(activities),
            "total_exercise_minutes": round(total_exercise_seconds / 60, 1),
            "avg_sleep_hours": _avg(sleep_values),
            "avg_resting_hr": _avg(resting_hr_values),
            "total_running_distance_km": round(total_running_distance_m / 1000, 2),
            "avg_running_pace_sec_per_km": _avg(avg_pace_sec_per_km_values),
            "high_intensity_workouts": high_intensity_count,
        },
        "daily": daily,
        "activities": activities,
        "garmin_predictions": raw.get("garmin_predictions"),
        "missing_fields": sorted(missing_fields),
    }
