# DENON AVC-A110 HTTP API 呼び出しガイド

> 対象機種: AVC-A110 (CommApiVers 0301)
> テスト日: 2026-02-14

---

## 接続情報

| 項目 | 値 |
|------|-----|
| API ポート | **8080** (HTTP) |
| Web コントロール UI | 10443 (HTTPS, 自己署名証明書) |
| HEOS TCP | 1255 |
| HEOS HTTP | 60006 |
| CommApiVers | **0301** |

> **注意**: ポート 80 は HTTPS へリダイレクトされるため HTTP では使用不可。

---

## POST エンドポイントの使い分け

AVC-A110 では **2 種類の POST エンドポイント** があり、コマンドの種類によって使い分ける。

### `POST /goform/AppCommand.xml` — 基本コマンド

パラメータ不要の単純なコマンドに使用する。

```
POST /goform/AppCommand.xml HTTP/1.1
Content-Type: text/xml; charset=utf-8
```

```xml
<?xml version="1.0" encoding="utf-8" ?>
<tx>
<cmd id="1">コマンド名</cmd>
</tx>
```

### `POST /goform/AppCommand0300.xml` — 拡張コマンド

パラメータ付きの詳細情報取得コマンドに使用する（CommApiVers 0300 以降）。

```
POST /goform/AppCommand0300.xml HTTP/1.1
Content-Type: text/xml; charset=utf-8
```

```xml
<?xml version="1.0" encoding="utf-8" ?>
<tx>
<cmd id="3">
<name>コマンド名</name>
<list>
<param name="パラメータ名" />
</list>
</cmd>
</tx>
```

---

## 重要な制約・注意事項

### 1. 改行付き XML が必須

リクエスト XML は**改行付き**で送信すること。1 行にまとめると空の `<rx/>` が返る。

```bash
# NG — 空応答になる
curl -s -X POST "http://<IP>:8080/goform/AppCommand.xml" \
  -d '<?xml version="1.0" encoding="utf-8" ?><tx><cmd id="1">GetAllZonePowerStatus</cmd></tx>'

# OK — 改行付き
curl -s -X POST "http://<IP>:8080/goform/AppCommand.xml" \
  -H "Content-Type: text/xml; charset=utf-8" \
  -d '<?xml version="1.0" encoding="utf-8" ?>
<tx>
<cmd id="1">GetAllZonePowerStatus</cmd>
</tx>'
```

### 2. エンドポイントとリクエスト形式の一致

- `AppCommand.xml` にパラメータ形式（`<name>` + `<list>`）を送ると `<error>3</error>` が返る
- `AppCommand0300.xml` にテキスト直接形式（`<cmd id="1">Name</cmd>`）を送ると `<error>2</error>` が返る

### 3. Content-Type

`text/xml; charset=utf-8` を指定する。

### 4. 1 リクエスト最大 5 cmd

`AppCommand.xml` は 1 リクエストに 5 個以上の `<cmd>` を含むとエラーになる。

### 5. タイムアウト

5 秒程度が適切。

### 6. 固定長パディング

多くの文字列値は末尾にスペースが付加される。`strip()` で除去すること。

```xml
<!-- surround 値は 64 文字にパディングされている -->
<surround>Dolby Atmos                                                    </surround>
```

### 7. 0300 の空リスト

一部コマンド（`GetHideSources`, `GetSourceRename`）は空 `<list />` でもデータを返す。

### 8. コマンド重複

いくつかのコマンドは両エンドポイントで利用可能だが、返却形式が異なる:

| AppCommand.xml | AppCommand0300.xml | 備考 |
|---------------|-------------------|------|
| `GetRenameSource` | `GetSourceRename` | 同等情報、異なる XML 構造 |
| `GetDeletedSource` | `GetDeleteSource` | 0300 版は CMD ERR を返す |

---

## レスポンスの `control` 属性 (0300 形式)

AppCommand0300.xml のレスポンスに含まれる `control` 属性の意味:

| 値 | 意味 |
|----|------|
| `0` | 読み取り不可 / 現在のモードでは無効 |
| `1` | 読み取り可能 / ユーザー変更可能 |
| `2` | 読み取り可能 / システム管理 |

---

## エラーレスポンス

### AppCommand.xml / AppCommand0300.xml 共通

```xml
<rx><error>N</error></rx>
```

| コード | 意味 |
|--------|------|
| `2` | コマンドにはパラメータが必要（`AppCommand0300.xml` を使用すべき） |
| `3` | 無効なコマンド形式（エンドポイントとリクエスト形式の不一致） |

### 0300 コマンド内エラー

```xml
<list>
<CMD ERR>
</list>
```

コマンド自体は認識されるが、指定されたパラメータが無効。

---

## 使用不可エンドポイント (403 Forbidden)

AVC-A110 (CommApiVers 0301) で 403 を返すエンドポイント:

- `GET /goform/formMainZone_MainZoneXmlStatus.xml`（Lite 版を使用すること）
- `GET /goform/formMainZone_MainZoneXml.xml`
- `GET /goform/formNetAudio_StatusXml.xml`
- `GET /goform/formTuner_TunerXml.xml`
- `GET /goform/formBluetooth_BluetoothXml.xml`
- `GET /goform/formDSP_DSPInfoXml.xml`
- `GET /goform/formNetAudio_StatusXmlInfo.xml`
- `GET /goform/formMoviePlayer_MoviePlayerXml.xml`
- `POST /goform/AppCommand0301.xml`
