"""Beds24 API v2 クライアント(接続確認レベルの最小実装)。

認証フロー:
1. Beds24管理画面でinvite codeを発行する(手動)。
2. `GET /authentication/setup` にinvite codeを渡すとrefreshTokenが発行される
   (これは初回セットアップ時に一度だけ行い、refreshTokenを `.env` に保存する。
   このステップ自体はこのクライアントには実装していない)。
3. 以降は保存済みのrefreshTokenを使い `GET /authentication/token` で短命の
   access tokenを取得する(`refreshToken` ヘッダーで渡す)。
4. 各APIリクエストには `token: <access token>` ヘッダーを付与する。

参考: https://wiki.beds24.com/index.php/Category:API_V2
"""
from __future__ import annotations

import requests


class Beds24Client:
    def __init__(self, base_url: str, refresh_token: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.refresh_token = refresh_token
        self._access_token: str | None = None

    def _refresh_access_token(self) -> str:
        resp = requests.get(
            f"{self.base_url}/authentication/token",
            headers={"refreshToken": self.refresh_token},
            timeout=10,
        )
        resp.raise_for_status()
        self._access_token = resp.json()["token"]
        return self._access_token

    def _headers(self) -> dict[str, str]:
        token = self._access_token or self._refresh_access_token()
        return {"accept": "application/json", "token": token}

    def get_properties(self) -> list[dict]:
        """接続確認・物件一覧取得用。"""
        resp = requests.get(f"{self.base_url}/properties", headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
