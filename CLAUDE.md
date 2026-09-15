# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## プロジェクト概要

Knot Ritsurin は民泊(1棟貸し等)物件の運営者が、Beds24(PMS/チャネルマネージャー)と
PriceLabs(動的価格設定)を使って運営を自動化することを目指すリポジトリです。
最終目標は、Claude Code からこれらのツールの状態を確認したり操作を指示したりできるように
することであり、このリポジトリにはそのための Python 連携スクリプト群を実装していきます。

## 運用ポリシー(必読・最優先)

### セキュリティ

- 認証情報(`BEDS24_REFRESH_TOKEN`, `PRICELABS_API_KEY` 等)は `.env` にのみ保持する。コード・
  テスト・ログ出力・コミット・チャットへの返答など、いかなる形でも平文の値を露出させない。
- 新しいクライアントメソッドやスクリプトは、そのタスクに必要な最小限のエンドポイント・権限のみを
  呼び出す設計にする。
- ゲストの個人情報(氏名・連絡先・決済情報・予約内容等)を扱うコードを追加する場合、ログや外部
  送信先(通知先チャット等)にそれらを含めない。

### 料金・在庫等を変更する操作は必ず承認を得ること

- Beds24 の料金・在庫・予約状態を変更する操作(レート更新、部屋止め/解除、予約の作成・変更・
  キャンセル等)や、PriceLabs の価格・最低宿泊日数などの設定を変更する操作は、**実行前に必ず
  ユーザーへ変更内容(対象物件・対象期間・変更前後の値)を提示し、明示的な承認を得てから実行する**。
  承認なしに自動実行してはならない。
- 現状の `Beds24Client` / `PriceLabsClient` は読み取り専用(`GET`)のみを実装している。書き込み系
  (`POST`/`PUT`/`PATCH`等)のメソッドを追加する場合も、呼び出し元(スクリプト)側で上記の承認フロー
  を経由しない限り実行できないようにすること。

## セットアップ・コマンド

```bash
# 仮想環境の作成と依存関係のインストール
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 認証情報の設定(.env.example を元に .env を作成し、値を埋める)
cp .env.example .env
```

- 接続確認(Beds24 / PriceLabs 両方に到達できるかを確認): `python scripts/check_connection.py`
- テスト全体の実行: `pytest`
- 単一テストの実行: `pytest tests/test_config.py::test_load_settings_defaults`

## アーキテクチャ

- `src/knot_ritsurin/config.py` — 設定値の唯一の入口。`.env` を読み込み `load_settings()` が
  `Settings` を返す。以降の全コード(クライアント・スクリプト)はここ経由でのみ認証情報を参照し、
  `os.environ` を直接読まない。
- `src/knot_ritsurin/clients/` — 外部サービスごとに薄いクライアントクラスを1つずつ置く
  (`Beds24Client`, `PriceLabsClient`)。各クライアントは認証処理とHTTP呼び出しのみを担当する。
  新しいAPI呼び出しを追加する際は、スクリプト側で直接 `requests` を呼ぶのではなく、対応する
  クライアントにメソッドを追加すること。
- `scripts/` — クライアントを組み合わせて1つのタスクを実行するエントリーポイント。現時点では
  接続確認 (`check_connection.py`) のみ。今後、料金同期・予約状況の取得・ゲスト対応の自動化などの
  スクリプトを追加していく想定。

## 外部API連携メモ

### Beds24 (API v2)

- ベースURL: `https://beds24.com/api/v2`(`.env` の `BEDS24_BASE_URL`)
- 認証は2段階:
  1. Beds24管理画面で発行した invite code を `GET /authentication/setup` に渡すと
     長期利用可能な `refreshToken` が発行される(この交換作業は初回セットアップ時に手動で行い、
     得られた `refreshToken` を `.env` の `BEDS24_REFRESH_TOKEN` に保存する。この処理自体は
     `Beds24Client` には未実装)。
  2. 保存済みの `refreshToken` を `refreshToken` ヘッダーに載せて `GET /authentication/token`
     を呼ぶと短命の access token が得られる。以降の各APIリクエストには
     `token: <access token>` ヘッダーを付与する。
- `Beds24Client` は現状 `GET /properties` のみを実装。新しいエンドポイントはこのクラスに
  メソッドとして追加する。

### PriceLabs (Customer API)

- ベースURL: `https://api.pricelabs.co/v1`(`.env` の `PRICELABS_BASE_URL`)
- 認証は静的なAPIキー1本で、`X-API-Key` ヘッダー(大文字小文字を区別)に付与する。
  APIキーは PriceLabs管理画面の Account Settings → API Details から発行する。
- `PriceLabsClient` の `get_listings()` はプレースホルダーであり、正確なエンドポイントパスは
  同設定画面からリンクされているSwaggerドキュメント(契約プランにより内容が変わる)で
  確認・修正すること。
