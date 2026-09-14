# Knot Ritsurin

民泊「Knot Ritsurin」の自動化運営を目的とした連携スクリプト群です。
Beds24(PMS/チャネルマネージャー)と PriceLabs(動的価格設定)の API を Python から呼び出し、
Claude Code から運営タスク(料金確認・予約状況確認など)を指示できるようにすることを目指しています。

## セットアップ

```bash
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"
cp .env.example .env   # BEDS24_REFRESH_TOKEN / PRICELABS_API_KEY を設定する
```

## 接続確認

```bash
python scripts/check_connection.py
```

詳しい構成・開発方針は [CLAUDE.md](./CLAUDE.md) を参照してください。
