# DENON AVC-A110 HTTP API ドキュメント

> 対象機種: AVC-A110 (CommApiVers 0301)
> テスト日: 2026-02-14

## 機器接続構成

```
4K UHD Blu-ray Player ──HDMI──→ AVR (BD入力)
Apple TV 4K ─────────HDMI──→ AVR (MPLAY入力)
AVR ──────────HDMI──→ BRAVIA (Google TV)
BRAVIA ───────eARC──→ AVR (TV Audio入力) ※TV内蔵アプリのみ
```

### テスト済みサンプル

| # | コンテンツ | ソース機器 | 入力 | 信号フォーマット |
|---|-----------|-----------|------|----------------|
| 1 | WARFARE (4K UHD BD) | 4K UHD Blu-ray Player | BD (HDMI直結) | Dolby Atmos - TrueHD (ロスレス) |
| 2 | Bladerunner 2049 (Sony Pictures Core) | BRAVIA / Sony Pictures Core | TV Audio (eARC) | IMAX DTS (DTS:X IMAX Enhanced) |
| 3 | F1 ザ・ムービー (Apple TV購入) | Apple TV 4K / TVアプリ | MPLAY (HDMI直結) | Dolby Atmos (Dolby Digital+ ロッシー) |
| 4 | Apple Music ロスレス (ステレオ) | Apple TV 4K / Apple Music | MPLAY (HDMI直結) | PCM Stereo (ALAC/ロスレス) |
| 5 | (電源オフ / STANDBY) | — | MPLAY (最終選択) | Unknown / Multi Ch In |

## ドキュメント構成

| ファイル | 内容 |
|----------|------|
| [API 呼び出しガイド](docs/api-notes.md) | 接続情報、リクエスト形式、エラーコード、注意事項、403 エンドポイント一覧 |
| [コマンドリファレンス](docs/api-reference.md) | 全コマンドのレスポンス例、パラメータ一覧、コマンドサマリー表 |

## 概要

- **AppCommand.xml**: 21 コマンド動作確認済み（ゾーン制御、オーディオ、ソース管理、システム設定）
- **AppCommand0300.xml**: 19 コマンドがデータ返却確認済み（信号情報、Audyssey、EQ、サラウンド等）
- **未解決**: 11 コマンドのパラメータ名が不明、3 コマンドが CMD ERR を返す
