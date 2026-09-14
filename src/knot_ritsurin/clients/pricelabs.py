"""PriceLabs Customer API クライアント(接続確認レベルの最小実装)。

認証: PriceLabs管理画面(Account Settings > API Details > Get PriceLabs API Key)
で発行したAPIキーを `X-API-Key` ヘッダー(大文字小文字を区別)に付与する。

正式なエンドポイント一覧は同設定画面からリンクされているSwaggerドキュメントを
参照すること。プランや契約内容により利用可能なエンドポイントが変わる。
"""
from __future__ import annotations

import requests


class PriceLabsClient:
    def __init__(self, base_url: str, api_key: str) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key

    def _headers(self) -> dict[str, str]:
        return {"X-API-Key": self.api_key}

    def get_listings(self) -> list[dict]:
        """接続確認・リスティング一覧取得用。

        NOTE: 正確なパスはSwagger定義で確認の上、必要に応じて修正すること。
        """
        resp = requests.get(f"{self.base_url}/listings", headers=self._headers(), timeout=10)
        resp.raise_for_status()
        return resp.json()
