# コードスタイル・規約

## 全般
- Python 3.9+対応（`from __future__ import annotations` を使用してUnion型ヒント `X | Y` を有効化）
- 単一ファイル構成（現時点では `main.py` のみ）
- コメント・出力メッセージは**日本語**
- docstringは**英語**

## 型ヒント
- 関数の引数・戻り値に型ヒントを付与
- `from __future__ import annotations` を使い、Python 3.9でも `X | Y` 構文を使用

## 命名規則
- 関数: snake_case（例: `check_power_status`）
- 定数: UPPER_SNAKE_CASE（例: `PORT`, `TIMEOUT`）
- プライベート関数: `_`プレフィックス（例: `_get_xml`）

## エラーハンドリング
- `try/except` で個別の例外をキャッチ
- ユーザー向けメッセージを `print()` で表示（`[OK]`, `[FAIL]`, `[WARN]` プレフィックス付き）
- 致命的エラーは `sys.exit(1)`

## リンター・フォーマッター
- 未設定（今後追加の可能性あり）
