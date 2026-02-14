# DENON AVC-A110 HTTP API リファレンス

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

## GET エンドポイント

### `GET /goform/Deviceinfo.xml` — デバイス情報

デバイスの基本情報と対応コマンド一覧を返す（約 68KB）。

**レスポンス例（抜粋）**:
```xml
<Device_Info>
  <ModelName>AVC-A110</ModelName>
  <MacAddress>000678850F90</MacAddress>
  <CommApiVers>0301</CommApiVers>
  <!-- DeviceCapabilities, DeviceZones, Commands 等 -->
</Device_Info>
```

### `GET /goform/formMainZone_MainZoneXmlStatusLite.xml` — メインゾーン状態

電源・音量・ミュート・入力ソースを返す。

**レスポンス例**:
```xml
<item>
  <Power><value>ON</value></Power>
  <InputFuncSelect><value>MPLAY</value></InputFuncSelect>
  <VolumeDisplay><value>Absolute</value></VolumeDisplay>
  <MasterVolume><value>-43.5</value></MasterVolume>
  <Mute><value>off</value></Mute>
</item>
```

- `Power/value`: `"ON"` または `"OFF"`（`"OFF"` = デバイス上の STANDBY 状態）
- `MasterVolume/value`: dB 値（例: `"-43.5"`）

### `GET /goform/formZone2_Zone2XmlStatusLite.xml` — Zone 2 状態

### `GET /goform/formZone3_Zone3XmlStatusLite.xml` — Zone 3 状態

Zone 2/3 もメインゾーンと同じ XML 構造で応答する。

---

## POST エンドポイント

AVC-A110 では **2 種類の POST エンドポイント** があり、**コマンドの種類によって使い分ける**。

### `POST /goform/AppCommand.xml` — 基本コマンド

**パラメータ不要の単純なコマンド**に使用する。

#### リクエスト形式

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

> **重要**: リクエスト XML は**改行付き**で送信すること。1 行に連結すると空の `<rx/>` が返る。

#### 動作確認済みコマンド

**`GetAllZonePowerStatus`**
```xml
<rx>
<cmd>
<zone1>ON</zone1>
<zone2>OFF</zone2>
<zone3>OFF</zone3>
</cmd>
</rx>
```

**`GetAllZoneSource`**
```xml
<rx>
<cmd>
<zone1><source>MPLAY</source></zone1>
<zone2><source>SOURCE</source></zone2>
<zone3><source>NET</source></zone3>
</cmd>
</rx>
```

**`GetAllZoneVolume`**
```xml
<rx>
<cmd>
<zone1>
<volume>-43.5</volume>
<state>variable</state>
<limit>-10.0</limit>
<disptype>ABSOLUTE</disptype>
<dispvalue>36.5</dispvalue>
</zone1>
<!-- zone2, zone3 も同様 -->
</cmd>
</rx>
```

**`GetSurroundModeStatus`**
```xml
<rx>
<cmd>
<surround>Stereo</surround>
</cmd>
</rx>
```

**`GetRenameSource`** — 入力ソースのリネーム情報
```xml
<rx>
<cmd>
<functionrename>
<list><name>CBL/SAT</name><rename>CBL/SAT</rename></list>
<list><name>Media Player</name><rename>Apple TV</rename></list>
<!-- 全ソース分 -->
</functionrename>
</cmd>
</rx>
```

**`GetAllZoneStereo`**
```xml
<rx>
<cmd>
<status>1</status>
<value>0</value>
<zones>000</zones>
<selections>000</selections>
</cmd>
</rx>
```

### `POST /goform/AppCommand0300.xml` — 拡張コマンド (CommApiVers 0300+)

**パラメータ付きの詳細情報取得コマンド**に使用する。

#### リクエスト形式

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

> **重要**: 改行付き + `<param />` 自己閉じタグを使用すること。
> `AppCommand.xml` にこの形式で送ると `<error>3</error>` が返る。

#### `GetAudioInfo` — オーディオ信号情報

```xml
<!-- リクエスト -->
<?xml version="1.0" encoding="utf-8" ?>
<tx>
<cmd id="3">
<name>GetAudioInfo</name>
<list>
<param name="inputmode" />
<param name="output" />
<param name="signal" />
<param name="sound" />
<param name="fs" />
</list>
</cmd>
</tx>
```

```xml
<!-- レスポンス -->
<rx>
<cmd>
<name>GetAudioInfo</name>
<list>
<param name="inputmode" control="1">Auto</param>
<param name="output" control="1">Speaker</param>
<param name="signal" control="1">PCM</param>
<param name="sound" control="1">Stereo</param>
<param name="fs" control="1">48 kHz</param>
</list>
</cmd>
</rx>
```

- `signal`: 受信信号フォーマット（PCM, Dolby Digital, DTS, Dolby Atmos 等）
- `sound`: 現在のサラウンドモード（Stereo, Dolby Surround, Neural:X 等）
- `fs`: サンプリング周波数（48 kHz, 96 kHz 等）
- `inputmode`: 入力モード（Auto, HDMI, Digital 等）
- `output`: 出力先（Speaker 等）
- `control` 属性: `"1"` = ユーザー変更可能

---

## エラーレスポンス

```xml
<rx><error>N</error></rx>
```

| コード | 意味 |
|--------|------|
| `2` | コマンドにはパラメータが必要（`AppCommand0300.xml` を使用すべき） |
| `3` | 無効なコマンド形式 |

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

---

## API 呼び出し時の注意

1. **改行付き XML が必須**: 1 行にまとめると空応答または解析エラーになる
2. **エンドポイントの使い分け**: 単純コマンドは `AppCommand.xml`、パラメータ付きは `AppCommand0300.xml`
3. **Content-Type**: `text/xml; charset=utf-8` を指定
4. **タイムアウト**: 5 秒程度が適切
5. **1リクエスト最大 5 cmd**: AppCommand.xml は 5 個以上の cmd を含むとエラーになる
