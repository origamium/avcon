# 開発コマンド一覧

## 環境セットアップ
```bash
# 仮想環境の有効化
source .venv/bin/activate

# 依存関係インストール
pip install -r requirements.txt
```

## 実行
```bash
# 導通チェック（電源状態確認）
source .venv/bin/activate && python main.py
```

## Git
```bash
git status
git add <file>
git commit -m "message"
```

## システムユーティリティ（macOS / Darwin）
```bash
ls          # ファイル一覧
find . -name "*.py"  # ファイル検索
grep -r "pattern" .  # パターン検索
```

## 注意
- `.env` ファイルは `.gitignore` に含まれるため、手動で作成が必要
- `.env` に `D_AVAMP_IP` と `D_AVAMP_MAC` を設定すること
- venvはシステムPython 3.9で作成済み
- テストフレームワーク・リンター・フォーマッターは未設定
