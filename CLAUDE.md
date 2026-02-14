# CLAUDE.md — avcon プロジェクト指示書

## Serena MCP 活用指針

このプロジェクトでは **Serena MCP のシンボリックツールを最優先** で使用すること。

- コード探索には `find_symbol`, `get_symbols_overview`, `find_referencing_symbols` を使う
- ファイル全体の `cat` / `read_file` より、シンボル単位の取得（`include_body=True`）を優先
- 編集は `replace_symbol_body`, `insert_after_symbol`, `insert_before_symbol` を第一候補とし、行単位の微修正のみ `replace_content` を使う
- リファクタリング時は `find_referencing_symbols` で影響範囲を必ず確認してから変更する
- Serena のメモリ（`project_overview`, `denon_api_reference`, `style_and_conventions` 等）を活用し、重複した調査を避ける

## プロジェクト概要

DENON AVC-A110 AVアンプを HTTP API（XML）経由でネットワーク制御する Python ツール。

## 技術スタック

- **言語**: Python 3.9+（`from __future__ import annotations` で新構文を有効化）
- **パッケージ管理**: uv（`uv.lock` で依存固定）
- **依存ライブラリ**: `requests`, `python-dotenv`, `xml.etree.ElementTree`（標準）
- **仮想環境**: `.venv/`

## 開発規約

- コメント・ユーザー向け出力は **日本語**、docstring は **英語**
- 関数: `snake_case` / 定数: `UPPER_SNAKE_CASE` / プライベート: `_` プレフィックス
- 型ヒントを関数の引数・戻り値に付与する
- 出力メッセージには `[OK]`, `[FAIL]`, `[WARN]`, `[ERROR]` プレフィックスを付ける
- 既存のコードパターンを踏襲し、不要な抽象化やリファクタを行わない

## DENON API ノート

- **制御ポート**: 8080（HTTP）
- ステータス取得は **Lite 版** XML を使う: `/goform/formMainZone_MainZoneXmlStatusLite.xml`
  - 通常版 `MainZoneXmlStatus.xml` は **403 Forbidden** になる（AVC-A110 固有）
- Power 値 `"OFF"` = デバイス上の STANDBY 状態
- 設定値（IP / MAC）は `.env` ファイルで管理（`D_AVAMP_IP`, `D_AVAMP_MAC`）
