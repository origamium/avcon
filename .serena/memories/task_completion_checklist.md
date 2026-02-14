# タスク完了時のチェックリスト

## 必須
1. コードが正常に実行できることを確認（`python main.py`）
2. `.env` の秘密情報がコミットに含まれていないことを確認
3. `from __future__ import annotations` が先頭にあることを確認（Python 3.9互換性）

## 推奨
- 新しい依存関係を追加した場合、`requirements.txt` を更新
- API の新しい知見が得られた場合、`denon_api_reference.md` メモリを更新
