"""環境変数からの設定読み込み。

Beds24 / PriceLabs の認証情報は `.env` に置き、`load_settings()` 経由でのみ
参照する(`.env.example` を元に各自 `.env` を作成すること)。
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    beds24_base_url: str
    beds24_refresh_token: str | None
    pricelabs_base_url: str
    pricelabs_api_key: str | None


def load_settings() -> Settings:
    return Settings(
        beds24_base_url=os.getenv("BEDS24_BASE_URL", "https://beds24.com/api/v2"),
        beds24_refresh_token=os.getenv("BEDS24_REFRESH_TOKEN") or None,
        pricelabs_base_url=os.getenv("PRICELABS_BASE_URL", "https://api.pricelabs.co/v1"),
        pricelabs_api_key=os.getenv("PRICELABS_API_KEY") or None,
    )
