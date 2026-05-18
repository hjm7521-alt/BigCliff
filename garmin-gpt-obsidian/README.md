# Garmin GPT Obsidian Weekly Reporter

## 프로젝트 목적
Garmin Connect의 최근 7일 건강/운동 데이터를 수집하고, OpenAI API 분석 결과를 포함한 Markdown 리포트를 생성해 Obsidian에 저장합니다. ChatGPT 프로젝트 `가민`에는 생성된 파일을 수동 업로드하여 참고합니다.

## 설치 방법
```bash
python -m venv .venv
.venv\\Scripts\\activate
pip install -r requirements.txt
```

## .env 설정 방법
1. `.env.example`를 `.env`로 복사
2. 값 입력

```env
GARMIN_EMAIL=
GARMIN_PASSWORD=
OPENAI_API_KEY=
OPENAI_MODEL=gpt-4.1-mini
OBSIDIAN_VAULT_PATH=E:/옵시디언/움직이는 황정민
OBSIDIAN_REPORT_DIR=건강 상태
TIMEZONE=Asia/Seoul
REPORT_LANGUAGE=ko
MOCK_MODE=false
```

## mock 모드 실행 방법
```bash
python src/main.py --mock
```

## 실제 Garmin 연결 실행 방법
```bash
python src/main.py
```

## 놓친 실행 자동 보완(일요일 20:00에 PC가 꺼져 있었던 경우)
- 작업 스케줄러에서 `예약된 시작을 놓친 후 가능한 빨리 작업 실행`을 활성화하세요.
- 이 프로그램은 실행 시점을 기준으로 `가장 최근 일요일`을 주간 종료일로 계산합니다.
- 따라서 월요일에 실행되더라도 전날 일요일 기준 주간 리포트가 생성됩니다.
- 같은 주차 리포트가 이미 있으면 중복 생성을 방지하기 위해 기본적으로 건너뜁니다.
- 강제 재생성이 필요하면 아래 명령을 사용하세요.

```bash
python src/main.py --force
```

## Obsidian 저장 경로 설정 방법
- `OBSIDIAN_VAULT_PATH`: Obsidian Vault 루트 경로
- `OBSIDIAN_REPORT_DIR`: Vault 내 상대 경로 (기본 `Garmin/Weekly Reports`)

예시(요청 경로):
- `OBSIDIAN_VAULT_PATH=E:/옵시디언/움직이는 황정민`
- `OBSIDIAN_REPORT_DIR=건강 상태`

이렇게 설정하면 최종 저장 위치는 아래와 같습니다.
- `E:\옵시디언\움직이는 황정민\건강 상태`

## Windows 작업 스케줄러 등록 방법
`docs/windows_task_scheduler.md` 참고

## ChatGPT 프로젝트 '가민' 수동 업로드 방법
`docs/chatgpt_project_manual_upload.md` 참고

## Garmin 로그인 실패 대처
- 이메일/비밀번호 재확인
- 2단계 인증/보안 챌린지 발생 가능
- 세션 만료 시 재로그인 필요
- 자세한 오류는 `logs/app.log` 확인

## OpenAI API 실패 대처
- API Key 확인
- 모델명 확인
- 네트워크/요금제/사용량 제한 확인
- 실패 시에도 리포트는 생성되며 분석 섹션에 실패 안내가 들어감

## 개인정보 보안 주의사항
- Garmin 계정, OpenAI API Key를 코드에 하드코딩하지 마세요.
- `.env`는 Git에 커밋하지 마세요.
- 로그에 민감정보가 노출되지 않도록 기본 로깅 포맷을 유지하세요.
