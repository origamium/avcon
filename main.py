"""DENON AVC-A110 導通チェック (Power Status Check)"""

from __future__ import annotations

import sys
import xml.etree.ElementTree as ET

import requests
from dotenv import dotenv_values


PORT = 8080
TIMEOUT = 5


def load_config() -> dict:
    """Load IP and MAC address from .env file."""
    config = dotenv_values(".env")
    ip = config.get("D_AVAMP_IP")
    mac = config.get("D_AVAMP_MAC")
    if not ip:
        print("[ERROR] D_AVAMP_IP が .env に設定されていません")
        sys.exit(1)
    return {"ip": ip, "mac": mac}


def _get_xml(ip: str, path: str) -> ET.Element | None:
    """GET request to port 8080, return parsed XML root or None."""
    url = f"http://{ip}:{PORT}{path}"
    try:
        resp = requests.get(url, timeout=TIMEOUT)
        resp.raise_for_status()
        return ET.fromstring(resp.text)
    except requests.ConnectionError:
        print(f"  [WARN] {url} に接続できません")
    except requests.Timeout:
        print(f"  [WARN] {url} タイムアウト")
    except requests.HTTPError as e:
        print(f"  [WARN] HTTPエラー: {e}")
    except ET.ParseError as e:
        print(f"  [WARN] XMLパースエラー: {e}")
    return None


def _post_xml(ip: str, path: str, body: str) -> ET.Element | None:
    """POST XML body to port 8080, return parsed XML root or None."""
    url = f"http://{ip}:{PORT}{path}"
    headers = {"Content-Type": "text/xml; charset=utf-8"}
    try:
        resp = requests.post(
            url, data=body.encode("utf-8"), headers=headers, timeout=TIMEOUT,
        )
        resp.raise_for_status()
        return ET.fromstring(resp.text)
    except requests.ConnectionError:
        print(f"  [WARN] {url} に接続できません")
    except requests.Timeout:
        print(f"  [WARN] {url} タイムアウト")
    except requests.HTTPError as e:
        print(f"  [WARN] HTTPエラー: {e}")
    except ET.ParseError as e:
        print(f"  [WARN] XMLパースエラー: {e}")
    return None


def check_device_info(ip: str) -> bool:
    """Fetch Deviceinfo.xml and display model info. Return True on success."""
    print("[Step 1] デバイス情報取得 ...")
    root = _get_xml(ip, "/goform/Deviceinfo.xml")
    if root is None:
        print("  [FAIL] デバイス情報を取得できませんでした")
        return False

    model = root.findtext("ModelName", default="不明")
    mac = root.findtext("MacAddress", default="不明")
    api_ver = root.findtext("CommApiVers", default="不明")
    print(f"  モデル名: {model}")
    print(f"  MACアドレス: {mac}")
    print(f"  API バージョン: {api_ver}")
    print("  [OK] ネットワーク接続確認")
    return True


def check_power_status(ip: str) -> str | None:
    """Fetch MainZoneXmlStatusLite and return power state, or None on failure."""
    print("[Step 2] 電源状態取得 ...")

    # AVC-A110 (CommApiVers 0301) では通常の MainZoneXmlStatus.xml は 403 を返す。
    # Lite版を使用する。
    root = _get_xml(ip, "/goform/formMainZone_MainZoneXmlStatusLite.xml")
    if root is None:
        print("  [FAIL] 電源状態を取得できませんでした")
        return None

    power = root.findtext(".//Power/value")
    volume = root.findtext(".//MasterVolume/value")
    mute = root.findtext(".//Mute/value")
    source = root.findtext(".//InputFuncSelect/value")

    if power is None:
        print("  [FAIL] 電源状態の解析に失敗しました")
        return None

    # Denon API は電源OFFを "OFF" ではなく "STANDBY" と返すこともある
    display_power = "STANDBY" if power == "OFF" else power
    print(f"  電源: {display_power}")
    if volume is not None:
        print(f"  音量: {volume} dB")
    if mute is not None:
        print(f"  ミュート: {mute}")
    if source is not None:
        print(f"  入力ソース: {source}")
    return display_power


def check_audio_signal(ip: str) -> dict | None:
    """Fetch audio signal info via AppCommand0300. Return parsed dict or None."""
    print("[Step 3] オーディオ信号情報取得 ...")

    # AVC-A110 (CommApiVers 0301) では AppCommand0300.xml を使用する。
    # 重要: リクエストXMLは改行付き + <param /> 自己閉じタグでないと空応答になる。
    body = """\
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
</tx>"""
    root = _post_xml(ip, "/goform/AppCommand0300.xml", body)
    if root is None:
        print("  [FAIL] オーディオ信号情報を取得できませんでした")
        return None

    # エラーチェック
    error = root.findtext(".//error")
    if error is not None:
        print(f"  [FAIL] APIエラー (code={error})")
        return None

    # レスポンス構造: <rx><cmd><name>GetAudioInfo</name><list>
    #   <param name="signal" control="1">PCM</param> ... </list></cmd></rx>
    result: dict = {}
    for param in root.findall(".//list/param"):
        name = param.get("name")
        value = (param.text or "").strip()
        if name and value:
            result[name] = value

    if not result:
        print("  [WARN] オーディオ信号情報が空です")
        return None

    if "signal" in result:
        print(f"  信号フォーマット: {result['signal']}")
    if "sound" in result:
        print(f"  サラウンドモード: {result['sound']}")
    if "inputmode" in result:
        print(f"  入力モード: {result['inputmode']}")
    if "fs" in result:
        print(f"  サンプリング周波数: {result['fs']}")
    if "output" in result:
        print(f"  出力: {result['output']}")
    print("  [OK] オーディオ信号情報取得完了")
    return result


def main():
    print("=" * 50)
    print("DENON AVC-A110 導通チェック")
    print("=" * 50)

    config = load_config()
    ip = config["ip"]
    mac = config["mac"]
    print(f"対象IP: {ip}")
    if mac:
        print(f"MACアドレス: {mac}")
    print()

    device_ok = check_device_info(ip)
    print()

    if not device_ok:
        print("[結果] 接続失敗 — デバイスに到達できません")
        print("  - IPアドレスを確認してください")
        print("  - アンプがネットワークに接続されているか確認してください")
        sys.exit(1)

    power = check_power_status(ip)
    print()

    if power is None:
        print("[結果] 接続成功（デバイス情報取得済み）だが電源状態の取得に失敗")
        sys.exit(1)

    # 電源 ON 時のみオーディオ信号情報を取得
    audio = None
    if power == "ON":
        audio = check_audio_signal(ip)
        print()

    print("=" * 50)
    summary = f"[結果] 接続成功 — 電源: {power}"
    if audio and "signal" in audio:
        summary += f" / 信号: {audio['signal']}"
    print(summary)
    print("=" * 50)


if __name__ == "__main__":
    main()
