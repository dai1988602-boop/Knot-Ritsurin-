"""Beds24 invite code -> refreshToken 交換用の初回セットアップスクリプト。

Beds24管理画面のAPI設定画面で発行した invite code(有効期限が短いので発行後すぐに
使うこと)を使い、`GET /authentication/setup` を1回だけ呼び出して長期利用可能な
refreshToken を取得する。

このスクリプトは `.env` を書き換えない。取得した refreshToken を画面に表示するので、
`.env` の `BEDS24_REFRESH_TOKEN` に手動で貼り付けること。

NOTE: beds24.com への外向き通信を許可していないネットワーク(このリポジトリの
クラウド実行環境など)では実行できない。beds24.com に到達できる環境
(手元のPC等)で実行すること。

Usage:
    python scripts/beds24_setup.py
"""
from __future__ import annotations

import getpass
import sys

import requests

from knot_ritsurin.config import load_settings


def main() -> int:
    settings = load_settings()
    invite_code = getpass.getpass("Beds24 invite code: ").strip()
    if not invite_code:
        print("invite codeが入力されていません", file=sys.stderr)
        return 1

    resp = requests.get(
        f"{settings.beds24_base_url}/authentication/setup",
        headers={"accept": "application/json", "code": invite_code},
        timeout=10,
    )
    resp.raise_for_status()
    data = resp.json()

    print("\n取得成功。以下を .env の BEDS24_REFRESH_TOKEN に設定してください:\n")
    print(f"BEDS24_REFRESH_TOKEN={data['refreshToken']}")
    print(
        f"\n(この場で発行された access token は {data.get('expiresIn')} 秒で失効するが、"
        "refreshTokenは長期間有効。以降はrefreshTokenからaccess tokenを自動取得する)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
