"""DENON AVC-A110 導通チェック"""

from __future__ import annotations

import sys

from dotenv import dotenv_values

from avcon import DenonAVR


def main() -> None:
    config = dotenv_values(".env")
    ip = config.get("D_AVAMP_IP")
    if not ip:
        print("[ERROR] D_AVAMP_IP が .env に設定されていません")
        sys.exit(1)

    avr = DenonAVR(ip)

    # Step 1: デバイス情報
    try:
        info = avr.get_device_info()
        print(f"[OK] {info.model} (MAC: {info.mac_address}, API: {info.api_version})")
    except Exception as e:
        print(f"[FAIL] デバイス情報を取得できません: {e}")
        sys.exit(1)

    # Step 2: 電源状態
    status = avr.get_status()
    print(f"[OK] 電源: {status.power} / 入力: {status.source} / 音量: {status.volume}dB / ミュート: {status.mute}")

    # Step 3: オーディオ信号 (電源ON時)
    if status.power == "ON":
        audio = avr.get_audio_info()
        print(f"[OK] 信号: {audio.signal} / モード: {audio.sound} / fs: {audio.sample_rate}")


if __name__ == "__main__":
    main()
