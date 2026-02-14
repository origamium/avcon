# DENON AVC-A110 HTTP API リファレンス

## 接続情報
- **APIポート**: 8080（HTTPのみ）
- **WebコントロールUI**: 10443（HTTPS）
- **HEOS**: TCP 1255, HTTP 60006
- **ポート80**: HTTPSへリダイレクト（自己署名証明書）— 使用不可
- **CommApiVers**: 0301（新世代API）

## 動作確認済みエンドポイント（ポート8080）

### デバイス情報
- `GET /goform/Deviceinfo.xml` → 200 OK（約68KB）
  - `<Device_Info>` ルート要素
  - 主要フィールド: `ModelName`, `MacAddress`, `CommApiVers`, `DeviceZones`, `DeviceCapabilities`

### メインゾーンステータス（Lite版）
- `GET /goform/formMainZone_MainZoneXmlStatusLite.xml` → 200 OK
  - `<item>` ルート要素
  - フィールド:
    - `Power/value` — "ON" または "OFF"（"OFF" = STANDBY状態）
    - `InputFuncSelect/value` — 入力ソース（例: "MPLAY"）
    - `VolumeDisplay/value` — 音量表示形式（例: "Absolute"）
    - `MasterVolume/value` — 音量（例: "-50.0"）
    - `Mute/value` — ミュート状態（例: "off"）

### Zone 2/3 ステータス
- `GET /goform/formZone2_Zone2XmlStatusLite.xml` → 200 OK
- `GET /goform/formZone3_Zone3XmlStatusLite.xml` → 200 OK

### AppCommand（POST） — 基本コマンド
- `POST /goform/AppCommand.xml` → 200 OK
  - Content-Type: `text/xml; charset=utf-8`
  - **重要**: リクエストXMLは改行付きで送信すること（1行だと空応答になる）
  - ボディ形式（テキスト直接指定、改行付き）:
    ```
    <?xml version="1.0" encoding="utf-8" ?>
    <tx>
    <cmd id="1">コマンド名</cmd>
    </tx>
    ```
  - 動作確認済みコマンド: `GetAllZonePowerStatus`, `GetAllZoneSource`, `GetAllZoneVolume`, `GetSurroundModeStatus`, `GetRenameSource`, `GetAllZoneStereo`

### AppCommand0300（POST） — 拡張コマンド (CommApiVers 0300+)
- `POST /goform/AppCommand0300.xml` → 200 OK
  - パラメータ付きコマンド用: `<name>` + `<list>` + `<param />` 自己閉じタグ形式
  - **重要**: `AppCommand.xml` にこの形式で送ると `<error>3</error>` になる
  - ボディ形式（改行付き必須）:
    ```
    <?xml version="1.0" encoding="utf-8" ?>
    <tx>
    <cmd id="3">
    <name>GetAudioInfo</name>
    <list>
    <param name="signal" />
    <param name="sound" />
    <param name="fs" />
    <param name="inputmode" />
    <param name="output" />
    </list>
    </cmd>
    </tx>
    ```
  - レスポンス: `<param name="signal" control="1">PCM</param>` 形式で値が返る
  - エラーコード: 2=パラメータ必要, 3=無効な形式

## 403 Forbidden になるエンドポイント
- `GET /goform/formMainZone_MainZoneXmlStatus.xml` — 使用不可（Lite版を使用）
- `GET /goform/formMainZone_MainZoneXml.xml`
- `GET /goform/formNetAudio_StatusXml.xml`
- `GET /goform/formTuner_TunerXml.xml`
- `GET /goform/formBluetooth_BluetoothXml.xml`
- `GET /goform/formDSP_DSPInfoXml.xml`
- `GET /goform/formNetAudio_StatusXmlInfo.xml`
- `POST /goform/AppCommand0301.xml`

## テレネットスタイルコマンド（HTTP経由）
- `GET /goform/formiPhoneAppDirect.xml?PW?` → 200 OK（空レスポンス — 応答が返らない）

## 注意事項
- Lite版XMLを使うこと（通常版は403）
- Power値 "OFF" はデバイス上では "STANDBY" に対応
- ポート80はHTTPSリダイレクトのため使用不可
- POST XMLは必ず改行付きで送信（1行だと空応答）
- エンドポイント使い分け: 単純コマンド→AppCommand.xml, パラメータ付き→AppCommand0300.xml
