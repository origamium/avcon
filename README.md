# avcon

DENON AVC-A110 AVアンプ ネットワーク制御ツール。

## セットアップ

```bash
uv sync
cp .env.example .env  # D_AVAMP_IP を設定
```

## 使い方

```bash
uv run python main.py
```

## curl で導通チェック

シェルだけで電源状態を確認できます。`192.168.1.23` は実際のアンプの IP に置き換えてください。

```bash
curl -s http://192.168.1.23:8080/goform/formMainZone_MainZoneXmlStatusLite.xml \
  | grep -oP '<Power><value>\K[^<]+'
```

> **注意**: 通常版 `MainZoneXmlStatus.xml` は AVC-A110 では 403 になります。必ず **Lite** 版を使ってください。

レスポンス例:

| 出力 | 意味 |
|------|------|
| `ON` | 電源オン |
| `OFF` | スタンバイ状態 |
