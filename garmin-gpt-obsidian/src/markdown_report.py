from __future__ import annotations

import datetime as dt
from typing import Any


def _format_or_none(value: Any, suffix: str = "") -> str:
    if value is None:
        return "데이터 없음"
    return f"{value}{suffix}"


def _pace_to_str(sec_per_km: float | None) -> str:
    if sec_per_km is None:
        return "데이터 없음"
    m = int(sec_per_km // 60)
    s = int(sec_per_km % 60)
    return f"{m}:{s:02d}/km"


def generate_markdown_report(processed: dict[str, Any], gpt_analysis: str) -> str:
    period = processed.get("period", {})
    start = period.get("start_date", "데이터 없음")
    end = period.get("end_date", "데이터 없음")
    created = dt.date.today().isoformat()
    summary = processed.get("weekly_summary", {})

    missing_lines = [f"- {m}" for m in processed.get("missing_fields", [])] or ["- 데이터 없음"]

    running_lines = []
    for activity in processed.get("activities", []):
        if activity.get("activityType", {}).get("typeKey") != "running":
            continue
        pace = None
        if activity.get("averageSpeed"):
            pace = 1000 / float(activity["averageSpeed"])
        running_lines.append(
            "- {date}, 거리 {distance}km, 페이스 {pace}, 평균 심박 {avg_hr}, 훈련 효과 {te}".format(
                date=str(activity.get("startTimeLocal", ""))[:10] or "데이터 없음",
                distance=round(float(activity.get("distance", 0) or 0) / 1000, 2),
                pace=_pace_to_str(pace),
                avg_hr=_format_or_none(activity.get("averageHR")),
                te=activity.get("trainingEffectLabel") or "데이터 없음",
            )
        )

    running_text = "\n".join(running_lines) if running_lines else "- 데이터 없음"

    md = f"""---
type: garmin-weekly-report
source: garmin-connect
created: {created}
period_start: {start}
period_end: {end}
tags:
  - garmin
  - running
  - health
  - weekly-report
---

### Garmin 주간 건강 및 훈련 리포트

**기간**
- {start} ~ {end}

**1. 종합 요약**
- 이번 주 컨디션 요약: 데이터 기반 종합 평가는 아래 GPT 분석 참고
- 가장 중요한 변화: HRV(심박변이도), 수면, 운동량의 상호작용 점검 필요
- 다음 주 핵심 관리 포인트: 회복과 강도 균형

**2. 건강 상태**
- HRV(심박변이도): 데이터 기반 상세는 GPT 분석 참고
- Resting Heart Rate(안정시 심박수): {_format_or_none(summary.get('avg_resting_hr'))}
- Stress(스트레스): 데이터 기반 상세는 GPT 분석 참고
- Body Battery(신체 에너지 지표): 데이터 기반 상세는 GPT 분석 참고
- 회복 상태: 데이터 기반 상세는 GPT 분석 참고

**3. 수면 분석**
- 평균 수면 시간: {_format_or_none(summary.get('avg_sleep_hours'), '시간')}
- 수면 점수: 데이터 기반 상세는 GPT 분석 참고
- 수면 부족 여부: GPT 분석 참고
- 훈련에 미친 영향: GPT 분석 참고

**4. 주간 운동량**
- 총 운동 횟수: {_format_or_none(summary.get('total_workouts'))}
- 총 운동 시간: {_format_or_none(summary.get('total_exercise_minutes'), '분')}
- 총 러닝 거리: {_format_or_none(summary.get('total_running_distance_km'), 'km')}
- 평균 페이스: {_pace_to_str(summary.get('avg_running_pace_sec_per_km'))}
- 평균 심박: 데이터 기반 상세는 GPT 분석 참고
- 고강도 운동 여부: {_format_or_none(summary.get('high_intensity_workouts'))}회

**5. 러닝 상세 분석**
{running_text}
- 장거리주 여부: GPT 분석 참고
- 회복주 여부: GPT 분석 참고
- 과부하 여부: GPT 분석 참고

**6. 예상 기록 및 퍼포먼스 변화**
- Garmin 예상 기록 데이터: {processed.get('garmin_predictions') or '데이터 없음'}
- VO2max(최대산소섭취량) 변화: 데이터 기반 상세는 GPT 분석 참고
- 퍼포먼스 개선 또는 저하 가능성: GPT 분석 참고

**7. GPT 분석**
{gpt_analysis}

**8. 다음 주 제안**
- 훈련 강도: GPT 분석 참고
- 회복 전략: GPT 분석 참고
- 수면 목표: GPT 분석 참고
- 러닝 계획 제안: GPT 분석 참고
- 주의할 점: GPT 분석 참고

**9. 데이터 누락 및 한계**
{chr(10).join(missing_lines)}
- Garmin 데이터 해석상 주의점: 기기 상태, 착용 습관, 알고리즘 업데이트에 따라 지표가 달라질 수 있음
- 의학적 진단이 아니라는 점: 이 리포트는 훈련 참고용이며 의료 진단을 대체하지 않음
"""
    return md
