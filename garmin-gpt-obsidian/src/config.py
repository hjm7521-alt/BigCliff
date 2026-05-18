from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv


@dataclass
class AppConfig:
    garmin_email: str
    garmin_password: str
    openai_api_key: str
    openai_model: str
    obsidian_vault_path: Path
    obsidian_report_dir: str
    timezone: str
    report_language: str
    mock_mode: bool
    project_root: Path



def _to_bool(value: str | None, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "y", "on"}


def load_config(project_root: Path, cli_mock: bool = False) -> AppConfig:
    env_path = project_root / ".env"
    load_dotenv(dotenv_path=env_path, override=False)

    mock_mode = cli_mock or _to_bool(os.getenv("MOCK_MODE"), default=False)

    return AppConfig(
        garmin_email=os.getenv("GARMIN_EMAIL", ""),
        garmin_password=os.getenv("GARMIN_PASSWORD", ""),
        openai_api_key=os.getenv("OPENAI_API_KEY", ""),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        obsidian_vault_path=Path(os.getenv("OBSIDIAN_VAULT_PATH", "")).expanduser(),
        obsidian_report_dir=os.getenv("OBSIDIAN_REPORT_DIR", "Garmin/Weekly Reports"),
        timezone=os.getenv("TIMEZONE", "Asia/Seoul"),
        report_language=os.getenv("REPORT_LANGUAGE", "ko"),
        mock_mode=mock_mode,
        project_root=project_root,
    )
