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

### 通知先(Discord)

- 承認依頼・実行結果・エラー等の通知先は Discord とする。Webhook URL は `.env` の
  `DISCORD_WEBHOOK_URL` に設定し、コードに直書きしない。
- Discordに通知するタイミング:
  1. 料金・在庫等を変更する前の承認依頼(対象物件・対象期間・変更前後の値を含める)
  2. 承認を得て実行した後の結果報告(成功/失敗)
  3. API呼び出し失敗時のエラーアラート
- 実装は `src/knot_ritsurin/notifications/discord.py` に `DiscordNotifier` を追加する想定
  (`clients/` と同様、Webhook呼び出しのみを担当する薄いラッパーとする)。**現時点では未実装**。

### 監査ログ

- 特に書き込み系操作(料金・在庫・予約の変更)は、実行の都度以下を記録する:
  - 実行日時(ISO8601)
  - 操作内容(どのAPI・どのメソッド・対象物件/期間)
  - 変更前後の値
  - 承認情報(Discordでの承認者・承認日時・該当メッセージへの参照)
  - 実行結果(成功/失敗、エラー内容があればその内容)
- 記録先は `logs/audit.jsonl`(1操作1行のJSON Lines形式)を想定。個人情報や運用の詳細を含み得るため
  Gitにはコミットしない(`logs/` は `.gitignore` 対象)。
- 上記のDiscord通知とローカルの監査ログを二重に残すことで、後からの追跡・説明責任を担保する。
- 読み取り専用(`GET`)の操作は監査ログの必須対象ではないが、デバッグ目的で記録してもよい。
- **現時点では未実装**。書き込み系のクライアントメソッドを追加する際に、この記録処理も併せて実装すること。

## セットアップ・コマンド

```bash
# 仮想環境の作成と依存関係のインストール
python -m venv .venv && source .venv/bin/activate
pip install -e ".[dev]"

# 認証情報の設定(.env.example を元に .env を作成し、値を埋める)
cp .env.example .env
```

- 接続確認(Beds24 / PriceLabs 両方に到達できるかを確認): `python scripts/check_connection.py`
- Beds24初回セットアップ(invite code → refreshToken取得。**beds24.comに到達できる環境で実行**、
  クラウド実行環境では動かない): `python scripts/beds24_setup.py`
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
- `src/knot_ritsurin/notifications/` — Discordなど通知先ごとの薄いクライアントを置く場所
  (`clients/` と同じ設計方針)。承認依頼・実行結果・エラー通知に使う。**現時点では未実装**
  (詳細は下記「運用ポリシー > 通知先(Discord)」を参照)。

## 外部API連携メモ

両サービスとも、Claude Codeからの連携方法には「公式MCPコネクタ経由」と「このリポジトリの
自作クライアント(`src/knot_ritsurin/clients/`)経由」の2通りがありうる。現状は下記の通り
非対称なので、新しくコードを書く前にどちらの経路を使うべきか確認すること。

### Beds24 (API v2)

- **公式MCPコネクタは存在しない**(claude.aiのコネクタディレクトリを確認済み)。非公式の
  `beds24-mcp-server`(個人開発者によるnpmパッケージ)は存在するが、ソース未監査の第三者に
  Beds24の認証情報(料金・在庫・予約を変更できる強い権限)を渡すことになるため、採用する場合は
  事前にソースコードを確認し、ユーザーの承認を得ること。**現時点では未採用**、このリポジトリの
  自作 `Beds24Client` を使う方針。
- ベースURL: `https://beds24.com/api/v2`(`.env` の `BEDS24_BASE_URL`)
- 認証は2段階:
  1. Beds24管理画面で発行した invite code を `GET /authentication/setup` に `code` ヘッダーで
     渡すと長期利用可能な `refreshToken` が発行される(`scripts/beds24_setup.py` で実行できる。
     取得した `refreshToken` は `.env` の `BEDS24_REFRESH_TOKEN` に手動で保存する)。
  2. 保存済みの `refreshToken` を `refreshToken` ヘッダーに載せて `GET /authentication/token`
     を呼ぶと短命の access token が得られる。以降の各APIリクエストには
     `token: <access token>` ヘッダーを付与する。
- `Beds24Client` は現状 `GET /properties` のみを実装。新しいエンドポイントはこのクラスに
  メソッドとして追加する。
- **注意**: このリポジトリのクラウド実行環境(Claude Code on the web等)はネットワークポリシーで
  `beds24.com` への外向き通信をブロックしている(検証済み: `CONNECT tunnel failed, response 403`)。
  `beds24_setup.py` や `Beds24Client` を使った疎通確認は、beds24.comに到達できる環境
  (利用者のローカル環境等)で実行すること。

### PriceLabs (Customer API)

- **公式MCPコネクタが利用可能**(claude.aiのコネクタディレクトリに登録済みで、このアカウントでは
  既に接続・有効化されている: `mcp__PriceLabs__*` ツール群)。listing一覧・料金・稼働率などの
  読み取りや、日別オーバーライドの更新等はまずこのMCPツールを使うこと(クラウド実行環境からでも
  `api.pricelabs.co` への直接HTTP通信はブロックされるため、自作 `PriceLabsClient` は
  MCPが使えない場合のフォールバック、または将来的な非対話処理向けの実装として位置づける)。
- ベースURL: `https://api.pricelabs.co/v1`(`.env` の `PRICELABS_BASE_URL`)
- 認証は静的なAPIキー1本で、`X-API-Key` ヘッダー(大文字小文字を区別)に付与する。
  APIキーは PriceLabs管理画面の Account Settings → API Details から発行する。
- `PriceLabsClient` の `get_listings()` はプレースホルダーであり、正確なエンドポイントパスは
  同設定画面からリンクされているSwaggerドキュメント(契約プランにより内容が変わる)で
  確認・修正すること。
