# avcon - DENON AVC-A110 ネットワーク制御プロジェクト

## 概要
DENON AVC-A110 AVアンプをネットワーク経由で制御するPythonプロジェクト。
HTTP API（XMLベース）を使い、電源状態の確認・音量操作・入力切替などを行う。

## 対象デバイス
- **機種**: DENON AVC-A110
- **IP**: `.env` の `D_AVAMP_IP` で指定（デフォルト: 192.168.1.23）
- **MAC**: `.env` の `D_AVAMP_MAC` で指定

## Tech Stack
- **言語**: Python 3.9+（`.python-version` = 3.9）
- **パッケージ管理**: pip + requirements.txt（pyproject.toml も存在するがdependenciesは空）
- **仮想環境**: `.venv/`（system Python 3.9 で作成）
- **ビルドツール**: uv（uv.lock が存在）
- **IDE**: PyCharm（.idea/ ディレクトリ存在）

## 依存ライブラリ
- `requests` — HTTP通信
- `python-dotenv` — .env ファイル読み込み
- `xml.etree.ElementTree` — XMLパース（標準ライブラリ）

## プロジェクト構成
```
avcon/
├── main.py              # メインスクリプト（導通チェック）
├── .env                 # デバイスIP/MAC設定（git管理外）
├── requirements.txt     # pip依存関係
├── pyproject.toml       # プロジェクトメタデータ
├── .python-version      # Python 3.9
├── uv.lock              # uvロックファイル
├── .venv/               # 仮想環境
├── .gitignore           # 標準的なPython/Node/JetBrains用
└── README.md            # （空）
```
