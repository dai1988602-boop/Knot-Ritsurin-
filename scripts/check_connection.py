"""Beds24 / PriceLabs への接続確認スクリプト。

Usage:
    python scripts/check_connection.py
"""
from __future__ import annotations

import sys

from knot_ritsurin.clients.beds24 import Beds24Client
from knot_ritsurin.clients.pricelabs import PriceLabsClient
from knot_ritsurin.config import load_settings


def main() -> int:
    settings = load_settings()
    ok = True

    if settings.beds24_refresh_token:
        try:
            client = Beds24Client(settings.beds24_base_url, settings.beds24_refresh_token)
            properties = client.get_properties()
            print(f"[Beds24] OK: {len(properties)} 件の物件を取得")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"[Beds24] NG: {exc}")
    else:
        ok = False
        print("[Beds24] NG: BEDS24_REFRESH_TOKEN が未設定です")

    if settings.pricelabs_api_key:
        try:
            client = PriceLabsClient(settings.pricelabs_base_url, settings.pricelabs_api_key)
            listings = client.get_listings()
            print(f"[PriceLabs] OK: {len(listings)} 件のリスティングを取得")
        except Exception as exc:  # noqa: BLE001
            ok = False
            print(f"[PriceLabs] NG: {exc}")
    else:
        ok = False
        print("[PriceLabs] NG: PRICELABS_API_KEY が未設定です")

    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
