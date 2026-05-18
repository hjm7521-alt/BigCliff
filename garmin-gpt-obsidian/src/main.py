from __future__ import annotations

import argparse
import datetime as dt
import sys
from pathlib import Path

from zoneinfo import ZoneInfo

from config import load_config
from data_transformer import transform_raw_to_processed
from file_writer import write_json, write_markdown
from garmin_client import GarminClient
from gpt_analyzer import analyze_with_gpt
from logger import setup_logger
from markdown_report import generate_markdown_report


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Garmin 주간 리포트 생성기")
    parser.add_argument("--mock", action="store_true", help="Mock 데이터로 실행")
    parser.add_argument("--force", action="store_true", help="이미 생성된 주차 리포트가 있어도 강제 재생성")
    return parser.parse_args()


def compute_week_range(tz_name: str) -> tuple[dt.date, dt.date]:
    now = dt.datetime.now(ZoneInfo(tz_name)).date()
    # 주간 리포트 기준일은 '가장 최근 일요일'로 고정.
    # 예: 월요일 10:00에 실행되면 전날(일요일) 기준 리포트를 생성하여
    # 일요일 20:00 미실행 건을 보완(catch-up)할 수 있다.
    days_since_sunday = (now.weekday() + 1) % 7
    end = now - dt.timedelta(days=days_since_sunday)
    start = end - dt.timedelta(days=6)
    return start, end


def main() -> int:
    args = parse_args()
    project_root = Path(__file__).resolve().parents[1]
    config = load_config(project_root=project_root, cli_mock=args.mock)

    logger = setup_logger(project_root / "logs")
    logger.info("Program started. mock_mode=%s", config.mock_mode)

    start_date, end_date = compute_week_range(config.timezone)
    report_filename = f"{end_date.isoformat()}_Garmin_Weekly_Report.md"
    local_report_path = project_root / "reports" / report_filename

    if local_report_path.exists() and not args.force:
        logger.info("Report already exists. Skip generation: %s", local_report_path)
        print(f"이미 생성된 주간 리포트가 있어 건너뜁니다: {local_report_path}")
        return 0

    client = GarminClient(
        email=config.garmin_email,
        password=config.garmin_password,
        logger=logger,
        mock_mode=config.mock_mode,
    )

    try:
        client.login()
        raw_data = client.get_recent_7days_data(start_date=start_date, end_date=end_date)
    except Exception as exc:
        if not config.mock_mode:
            logger.error("Garmin data collection failed: %s", exc)
            print("Garmin 연결 실패. logs/app.log를 확인하세요.")
            return 1
        raise

    ts = dt.datetime.now(ZoneInfo(config.timezone)).strftime("%Y%m%d_%H%M%S")
    raw_path = project_root / "data" / "raw" / f"garmin_raw_{ts}.json"
    write_json(raw_path, raw_data)

    processed = transform_raw_to_processed(raw_data)
    processed_path = project_root / "data" / "processed" / f"garmin_processed_{ts}.json"
    write_json(processed_path, processed)

    if config.openai_api_key:
        try:
            gpt_analysis = analyze_with_gpt(
                api_key=config.openai_api_key,
                model=config.openai_model,
                processed=processed,
                language=config.report_language,
            )
        except Exception as exc:
            logger.error("OpenAI API call failed: %s", exc)
            gpt_analysis = "OpenAI API 호출 실패로 분석을 생성하지 못했습니다. 데이터와 로그를 확인하세요."
    else:
        gpt_analysis = "OPENAI_API_KEY가 설정되지 않아 GPT 분석을 생략했습니다."

    report_content = generate_markdown_report(processed=processed, gpt_analysis=gpt_analysis)
    write_markdown(local_report_path, report_content)

    if config.obsidian_vault_path:
        obsidian_path = config.obsidian_vault_path / config.obsidian_report_dir / report_filename
        write_markdown(obsidian_path, report_content)
        logger.info("Saved report to Obsidian: %s", obsidian_path)

    logger.info("Done. raw=%s processed=%s report=%s", raw_path, processed_path, local_report_path)
    print(f"완료: {local_report_path}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
