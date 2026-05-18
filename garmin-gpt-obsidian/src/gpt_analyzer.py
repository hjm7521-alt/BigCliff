from __future__ import annotations

import json
from typing import Any

from openai import OpenAI


def build_analysis_prompt(processed: dict[str, Any], language: str = "ko") -> str:
    return f"""
당신은 러닝 코치이자 건강 데이터 해설가입니다.
아래 Garmin 주간 데이터를 바탕으로 {language}로 분석하세요.
반드시 의학적 진단처럼 단정하지 말고, 훈련 참고용 조언으로 작성하세요.

필수 분석 항목:
1) 이번 주 종합 컨디션
2) HRV 변화 해석
3) 수면과 훈련의 관계
4) 운동량 평가
5) 과훈련 위험도
6) 회복 필요성
7) 예상 기록 변화
8) 다음 주 훈련 방향
9) 주의해야 할 건강 신호

데이터(JSON):
{json.dumps(processed, ensure_ascii=False, indent=2)}
""".strip()


def analyze_with_gpt(api_key: str, model: str, processed: dict[str, Any], language: str = "ko") -> str:
    client = OpenAI(api_key=api_key)
    prompt = build_analysis_prompt(processed, language=language)

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": "당신은 신중한 피트니스 분석가입니다."},
            {"role": "user", "content": prompt},
        ],
        temperature=0.3,
    )

    return response.output_text.strip()
