"""DENON AVR HTTP API client."""

from __future__ import annotations

import xml.etree.ElementTree as ET

import requests

from avcon._xml import build_param_cmd, build_simple_cmd, parse_params
from avcon.models import (
    AllZoneStereo,
    AudioInfo,
    AudysseySettings,
    AutoStandby,
    ChannelLevel,
    DeviceInfo,
    EcoSettings,
    NetworkInfo,
    QuickSelect,
    SignalChannel,
    SoundMode,
    SoundModeEntry,
    SourceEntry,
    SpeakerChannel,
    Status,
    SubwooferLevel,
    SurroundParameter,
    ToneControl,
    VideoInfo,
    ZoneMute,
    ZonePower,
    ZoneSource,
    ZoneVolume,
    ZoneVolumeInfo,
)


class DenonAPIError(Exception):
    """DENON AVR API error."""


class DenonAVR:
    """DENON AVR HTTP API client for AVC-A110 (CommApiVers 0301)."""

    _ZONE_STATUS_PATHS = {
        1: "/goform/formMainZone_MainZoneXmlStatusLite.xml",
        2: "/goform/formZone2_Zone2XmlStatusLite.xml",
        3: "/goform/formZone3_Zone3XmlStatusLite.xml",
    }

    def __init__(self, host: str, port: int = 8080, timeout: int = 5) -> None:
        self._host = host
        self._port = port
        self._timeout = timeout
        self._base = f"http://{host}:{port}"

    # --- 内部メソッド ---

    def _get(self, path: str) -> ET.Element:
        """Send GET request and return parsed XML root."""
        resp = requests.get(f"{self._base}{path}", timeout=self._timeout)
        resp.raise_for_status()
        return ET.fromstring(resp.text)

    def _post_simple(self, *commands: str) -> ET.Element:
        """Send AppCommand.xml POST and return parsed XML root."""
        body = build_simple_cmd(*commands)
        resp = requests.post(
            f"{self._base}/goform/AppCommand.xml",
            data=body.encode("utf-8"),
            headers={"Content-Type": "text/xml; charset=utf-8"},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        return ET.fromstring(resp.text)

    def _post_param(self, name: str, params: list[str]) -> ET.Element:
        """Send AppCommand0300.xml POST and return parsed XML root."""
        body = build_param_cmd(name, params)
        resp = requests.post(
            f"{self._base}/goform/AppCommand0300.xml",
            data=body.encode("utf-8"),
            headers={"Content-Type": "text/xml; charset=utf-8"},
            timeout=self._timeout,
        )
        resp.raise_for_status()
        root = ET.fromstring(resp.text)
        error = root.findtext(".//error")
        if error is not None:
            raise DenonAPIError(f"APIエラー (code={error})")
        return root

    # --- GET エンドポイント ---

    def get_device_info(self) -> DeviceInfo:
        """Fetch device information from Deviceinfo.xml."""
        root = self._get("/goform/Deviceinfo.xml")
        return DeviceInfo(
            model=root.findtext("ModelName", "").strip(),
            mac_address=root.findtext("MacAddress", "").strip(),
            api_version=root.findtext("CommApiVers", "").strip(),
        )

    def get_status(self, zone: int = 1) -> Status:
        """Fetch zone status (power, volume, mute, source)."""
        root = self._get(self._ZONE_STATUS_PATHS[zone])
        power_raw = root.findtext(".//Power/value", "").strip()
        # API の "OFF" = デバイス上の STANDBY 状態
        power = "STANDBY" if power_raw == "OFF" else power_raw
        volume_str = root.findtext(".//MasterVolume/value", "0").strip()
        return Status(
            power=power,
            source=root.findtext(".//InputFuncSelect/value", "").strip(),
            volume=float(volume_str) if volume_str else 0.0,
            mute=root.findtext(".//Mute/value", "").strip(),
            volume_display=root.findtext(".//VolumeDisplay/value", "").strip(),
        )

    # --- AppCommand.xml 読み取り ---

    def get_all_zone_power(self) -> ZonePower:
        """Fetch power status for all zones."""
        root = self._post_simple("GetAllZonePowerStatus")
        cmd = root.find("cmd")
        return ZonePower(
            zone1=(cmd.findtext("zone1", "") or "").strip(),
            zone2=(cmd.findtext("zone2", "") or "").strip(),
            zone3=(cmd.findtext("zone3", "") or "").strip(),
        )

    def get_all_zone_source(self) -> ZoneSource:
        """Fetch input source for all zones."""
        root = self._post_simple("GetAllZoneSource")
        cmd = root.find("cmd")
        return ZoneSource(
            zone1=(cmd.findtext("zone1/source", "") or "").strip(),
            zone2=(cmd.findtext("zone2/source", "") or "").strip(),
            zone3=(cmd.findtext("zone3/source", "") or "").strip(),
        )

    def get_all_zone_volume(self) -> ZoneVolume:
        """Fetch volume info for all zones."""
        root = self._post_simple("GetAllZoneVolume")
        cmd = root.find("cmd")

        def _parse_zone(tag: str) -> ZoneVolumeInfo:
            z = cmd.find(tag)
            vol = (z.findtext("volume", "0") or "").strip()
            lim = (z.findtext("limit", "0") or "").strip()
            return ZoneVolumeInfo(
                volume=float(vol) if vol else 0.0,
                limit=float(lim) if lim else 0.0,
                display_type=(z.findtext("disptype", "") or "").strip(),
                display_value=(z.findtext("dispvalue", "") or "").strip(),
            )

        return ZoneVolume(
            zone1=_parse_zone("zone1"),
            zone2=_parse_zone("zone2"),
            zone3=_parse_zone("zone3"),
        )

    def get_all_zone_mute(self) -> ZoneMute:
        """Fetch mute status for all zones."""
        root = self._post_simple("GetAllZoneMuteStatus")
        cmd = root.find("cmd")
        return ZoneMute(
            zone1=(cmd.findtext("zone1", "") or "").strip().lower() == "on",
            zone2=(cmd.findtext("zone2", "") or "").strip().lower() == "on",
            zone3=(cmd.findtext("zone3", "") or "").strip().lower() == "on",
        )

    def get_all_zone_stereo(self) -> AllZoneStereo:
        """Fetch All Zone Stereo status."""
        root = self._post_simple("GetAllZoneStereo")
        cmd = root.find("cmd")
        return AllZoneStereo(
            available=(cmd.findtext("status", "") or "").strip() == "1",
            enabled=(cmd.findtext("value", "") or "").strip() == "1",
            zones=(cmd.findtext("zones", "") or "").strip(),
            selections=(cmd.findtext("selections", "") or "").strip(),
        )

    def get_zone_name(self) -> dict[str, str]:
        """Fetch custom zone names. Returns {zone1: name, ...}."""
        root = self._post_simple("GetZoneName")
        cmd = root.find("cmd")
        return {
            "zone1": (cmd.findtext("zone1", "") or "").strip(),
            "zone2": (cmd.findtext("zone2", "") or "").strip(),
            "zone3": (cmd.findtext("zone3", "") or "").strip(),
        }

    def get_surround_mode(self) -> str:
        """Fetch current surround mode name."""
        root = self._post_simple("GetSurroundModeStatus")
        cmd = root.find("cmd")
        return (cmd.findtext("surround", "") or "").strip()

    def get_tone_control(self) -> ToneControl:
        """Fetch tone control (bass/treble) settings."""
        root = self._post_simple("GetToneControl")
        cmd = root.find("cmd")
        return ToneControl(
            available=(cmd.findtext("status", "") or "").strip() == "1",
            adjust=(cmd.findtext("adjust", "") or "").strip() == "1",
            bass_level=(cmd.findtext("basslevel", "") or "").strip(),
            treble_level=(cmd.findtext("treblelevel", "") or "").strip(),
            bass_value=int((cmd.findtext("bassvalue", "0") or "0").strip()),
            treble_value=int((cmd.findtext("treblevalue", "0") or "0").strip()),
        )

    def get_subwoofer_level(self) -> SubwooferLevel:
        """Fetch subwoofer level settings."""
        root = self._post_simple("GetSubwooferLevel")
        cmd = root.find("cmd")
        return SubwooferLevel(
            sw1_name=(cmd.findtext("sw1dispname", "") or "").strip(),
            sw1_active=(cmd.findtext("sw1status", "") or "").strip() == "1",
            sw1_level=(cmd.findtext("sw1level", "") or "").strip(),
            sw1_value=int((cmd.findtext("sw1value", "0") or "0").strip()),
            sw2_name=(cmd.findtext("sw2dispname", "") or "").strip(),
            sw2_active=(cmd.findtext("sw2status", "") or "").strip() == "1",
            sw2_level=(cmd.findtext("sw2level", "") or "").strip(),
            sw2_value=int((cmd.findtext("sw2value", "0") or "0").strip()),
        )

    def get_channel_levels(self) -> list[ChannelLevel]:
        """Fetch all channel level settings (up to 32 channels)."""
        root = self._post_simple("GetChLevel")
        cmd = root.find("cmd")
        channels: list[ChannelLevel] = []
        for ch in cmd.findall("chlists/ch"):
            channels.append(ChannelLevel(
                name=(ch.findtext("name", "") or "").strip(),
                active=(ch.findtext("status", "") or "").strip() == "1",
                speaker_type=int((ch.findtext("sptype", "0") or "0").strip()),
                level=(ch.findtext("level", "") or "").strip(),
                value=int((ch.findtext("value", "0") or "0").strip()),
            ))
        return channels

    def get_channel_indicators(self) -> bool:
        """Fetch channel indicator display state. Returns True if visible."""
        root = self._post_simple("GetChannelIndicators")
        cmd = root.find("cmd")
        return (cmd.findtext("value", "") or "").strip() == "1"

    def get_rename_source(self) -> dict[str, str]:
        """Fetch source rename map. Returns {original_name: custom_name}."""
        root = self._post_simple("GetRenameSource")
        cmd = root.find("cmd")
        result: dict[str, str] = {}
        for item in cmd.findall("functionrename/list"):
            name = (item.findtext("name", "") or "").strip()
            rename = (item.findtext("rename", "") or "").strip()
            if name:
                result[name] = rename
        return result

    def get_deleted_sources(self) -> list[SourceEntry]:
        """Fetch source enabled/disabled status."""
        root = self._post_simple("GetDeletedSource")
        cmd = root.find("cmd")
        sources: list[SourceEntry] = []
        for item in cmd.findall("functiondelete/list"):
            sources.append(SourceEntry(
                name=(item.findtext("name", "") or "").strip(),
                func_name=(item.findtext("FuncName", "") or "").strip(),
                enabled=(item.findtext("use", "") or "").strip() == "1",
            ))
        return sources

    def get_friendly_name(self) -> str:
        """Fetch device friendly name."""
        root = self._post_simple("GetFriendlyName")
        cmd = root.find("cmd")
        return (cmd.findtext("friendlyname", "") or "").strip()

    def get_quick_select(self) -> list[QuickSelect]:
        """Fetch quick select presets (name and source)."""
        root = self._post_simple("GetQuickSelectName")
        cmd = root.find("cmd")
        presets: list[QuickSelect] = []
        for i in range(1, 5):
            name = (cmd.findtext(f"Name{i}", "") or "").strip()
            source = (cmd.findtext(f"Source{i}", "") or "").strip()
            if name:
                presets.append(QuickSelect(name=name, source=source))
        return presets

    def get_auto_standby(self) -> list[AutoStandby]:
        """Fetch auto standby settings for all zones."""
        root = self._post_simple("GetAutoStandby")
        cmd = root.find("cmd")
        entries: list[AutoStandby] = []
        for item in cmd.findall("list/listvalue"):
            entries.append(AutoStandby(
                zone=(item.findtext("zone", "") or "").strip(),
                value=int((item.findtext("value", "0") or "0").strip()),
            ))
        return entries

    def get_dimmer(self) -> int:
        """Fetch display brightness. 0=OFF, 1=Dark, 2=Dim, 3=Bright."""
        root = self._post_simple("GetDimmer")
        cmd = root.find("cmd")
        return int((cmd.findtext("value", "0") or "0").strip())

    def get_eco(self) -> EcoSettings:
        """Fetch ECO mode settings."""
        root = self._post_simple("GetECO")
        cmd = root.find("cmd")
        return EcoSettings(
            available=(cmd.findtext("status", "") or "").strip() == "1",
            mode=int((cmd.findtext("mode", "0") or "0").strip()),
            power_on_default=int((cmd.findtext("pwondefault", "0") or "0").strip()),
            display=int((cmd.findtext("display", "0") or "0").strip()),
        )

    def get_eco_meter(self) -> int:
        """Fetch ECO meter value."""
        root = self._post_simple("GetECOMeter")
        cmd = root.find("cmd")
        return int((cmd.findtext("value", "0") or "0").strip())

    def get_picture_mode(self) -> tuple[bool, int]:
        """Fetch picture mode. Returns (available, value)."""
        root = self._post_simple("GetPictureMode")
        cmd = root.find("cmd")
        available = (cmd.findtext("status", "") or "").strip() == "1"
        value = int((cmd.findtext("value", "0") or "0").strip())
        return (available, value)

    def get_video_select(self) -> bool:
        """Fetch video select availability."""
        root = self._post_simple("GetVideoSelect")
        cmd = root.find("cmd")
        return (cmd.findtext("status", "") or "").strip() == "1"

    # --- AppCommand0300.xml 読み取り ---

    def get_audio_info(self) -> AudioInfo:
        """Fetch audio signal information."""
        root = self._post_param(
            "GetAudioInfo", ["inputmode", "output", "signal", "sound", "fs"],
        )
        params = parse_params(root)
        return AudioInfo(
            input_mode=params.get("inputmode", ("", 0))[0],
            output=params.get("output", ("", 0))[0],
            signal=params.get("signal", ("", 0))[0],
            sound=params.get("sound", ("", 0))[0],
            sample_rate=params.get("fs", ("", 0))[0],
        )

    def get_video_info(self) -> VideoInfo:
        """Fetch HDMI video signal information."""
        root = self._post_param(
            "GetVideoInfo", ["videooutput", "hdmisigin", "hdmisigout"],
        )
        params = parse_params(root)
        return VideoInfo(
            output=params.get("videooutput", ("", 0))[0],
            hdmi_in=params.get("hdmisigin", ("", 0))[0],
            hdmi_out=params.get("hdmisigout", ("", 0))[0],
        )

    def get_input_signal(self) -> list[SignalChannel]:
        """Fetch input signal channel map (5x4 grid)."""
        root = self._post_param("GetInputSignal", ["inputsigall"])
        channels: list[SignalChannel] = []
        for param in root.findall(".//list/param"):
            name = (param.text or "").strip()
            control = int(param.get("control", "0"))
            if name:
                channels.append(SignalChannel(name=name, control=control))
        return channels

    def get_active_speaker(self) -> list[SpeakerChannel]:
        """Fetch active speaker configuration (5x4 grid)."""
        root = self._post_param("GetActiveSpeaker", ["activespall"])
        channels: list[SpeakerChannel] = []
        for param in root.findall(".//list/param"):
            name = (param.text or "").strip()
            control = int(param.get("control", "0"))
            if name:
                channels.append(SpeakerChannel(name=name, control=control))
        return channels

    def get_sound_mode(self) -> SoundMode:
        """Fetch current sound mode category."""
        root = self._post_param(
            "GetSoundMode", ["movie", "music", "game", "pure"],
        )
        params = parse_params(root)
        return SoundMode(
            movie=params.get("movie", ("0", 0))[0] == "1",
            music=params.get("music", ("0", 0))[0] == "1",
            game=params.get("game", ("0", 0))[0] == "1",
            pure=params.get("pure", ("0", 0))[0] == "1",
        )

    def get_sound_mode_list(self) -> tuple[int, list[SoundModeEntry]]:
        """Fetch available sound modes for current signal.

        Returns (genre, modes).
        """
        root = self._post_param("GetSoundModeList", ["genrelist"])
        # genrelist パラメータ値
        genre_param = root.find(".//list/param[@name='genrelist']")
        genre = int((genre_param.text or "0").strip()) if genre_param is not None else 0
        # モードリスト
        modes: list[SoundModeEntry] = []
        for value in root.findall(".//list/list/value"):
            modes.append(SoundModeEntry(
                number=int((value.findtext("listno", "0") or "0").strip()),
                name=(value.findtext("dispname", "") or "").strip(),
                selected=(value.findtext("selected", "0") or "0").strip() == "1",
            ))
        return (genre, modes)

    def get_surround_parameter(self) -> SurroundParameter:
        """Fetch surround DSP parameters."""
        root = self._post_param(
            "GetSurroundParameter",
            ["centerimage", "dimension", "centerwidth", "panorama"],
        )
        params = parse_params(root)
        return SurroundParameter(
            center_image=params.get("centerimage", ("", 0))[0],
            dimension=params.get("dimension", ("", 0))[0],
            center_width=params.get("centerwidth", ("", 0))[0],
            panorama=params.get("panorama", ("", 0))[0],
        )

    def get_audyssey(self) -> AudysseySettings:
        """Fetch Audyssey settings."""
        root = self._post_param(
            "GetAudyssey",
            ["dynamiceq", "reflevoffset", "dynamicvol", "multeq"],
        )
        params = parse_params(root)

        def _int(key: str) -> int:
            val = params.get(key, ("0", 0))[0]
            return int(val) if val else 0

        return AudysseySettings(
            dynamic_eq=_int("dynamiceq"),
            ref_level_offset=_int("reflevoffset"),
            dynamic_vol=_int("dynamicvol"),
            multeq=_int("multeq"),
        )

    def get_audyssey_info(self) -> dict[str, str]:
        """Fetch Audyssey info in human-readable form."""
        root = self._post_param(
            "GetAudyssyInfo", ["dynamiceq", "dynamicvol"],
        )
        params = parse_params(root)
        return {k: v[0] for k, v in params.items()}

    def get_restorer_mode(self) -> int:
        """Fetch Compressed Audio Restorer mode. 0=OFF, 1=Low, 2=Med, 3=High."""
        root = self._post_param("GetRestorerMode", ["mode"])
        params = parse_params(root)
        val = params.get("mode", ("0", 0))[0]
        return int(val) if val else 0

    def get_audio_delay(self) -> int:
        """Fetch audio delay in ms."""
        root = self._post_param("GetAudioDelay", ["audiodelay"])
        params = parse_params(root)
        val = params.get("audiodelay", ("0", 0))[0]
        return int(val) if val else 0

    def get_bass_sync(self) -> int | None:
        """Fetch bass sync value. Returns None if disabled (control=0)."""
        root = self._post_param("GetBassSync", ["basssync"])
        params = parse_params(root)
        entry = params.get("basssync")
        if entry is None or entry[1] == 0:
            return None
        return int(entry[0]) if entry[0] else 0

    def get_bass_treble(self) -> dict[str, str]:
        """Fetch bass/treble settings (0300 format)."""
        root = self._post_param("GetBassTreble", ["bass", "treble"])
        params = parse_params(root)
        return {k: v[0] for k, v in params.items()}

    def get_output_settings(self) -> int:
        """Fetch video output mode setting."""
        root = self._post_param("GetOutputSettings", ["videomode"])
        params = parse_params(root)
        val = params.get("videomode", ("0", 0))[0]
        return int(val) if val else 0

    def get_lr_channel_level(self) -> str | None:
        """Fetch L/R channel level. Returns None if disabled."""
        root = self._post_param("GetLRchLevel", ["lrchlevel"])
        params = parse_params(root)
        entry = params.get("lrchlevel")
        if entry is None or entry[1] == 0:
            return None
        return entry[0] if entry[0] else None

    def get_hide_sources(self) -> dict[str, bool]:
        """Fetch source visibility. Returns {source: visible}."""
        root = self._post_param("GetHideSources", [])
        result: dict[str, bool] = {}
        for param in root.findall(".//list/param"):
            name = param.get("name", "")
            value = (param.text or "").strip()
            if name:
                # 1 = 表示, 2 = 非表示
                result[name] = value == "1"
        return result

    def get_source_rename_0300(self) -> dict[str, str]:
        """Fetch source rename map (0300 format)."""
        root = self._post_param("GetSourceRename", [])
        result: dict[str, str] = {}
        for param in root.findall(".//list/param"):
            name = param.get("name", "")
            value = (param.text or "").strip()
            control = int(param.get("control", "0"))
            if name and control > 0:
                result[name] = value
        return result

    def get_network_info(self) -> NetworkInfo:
        """Fetch network connection information."""
        root = self._post_param(
            "GetNetworkInfo", ["dhcp", "ssid", "connection"],
        )
        params = parse_params(root)
        return NetworkInfo(
            dhcp=params.get("dhcp", ("", 0))[0],
            ssid=params.get("ssid", ("", 0))[0],
            connection=params.get("connection", ("", 0))[0],
        )

    def get_hdmi_setup(self) -> dict[str, str]:
        """Fetch HDMI setup information."""
        root = self._post_param("GetHdmiSetup", ["audioout"])
        params = parse_params(root)
        return {k: v[0] for k, v in params.items()}

    def get_update_info(self) -> dict[str, str]:
        """Fetch firmware update information."""
        root = self._post_param("GetUpdateInfo", ["status"])
        params = parse_params(root)
        return {k: v[0] for k, v in params.items()}

    # --- 制御コマンド (formiPhoneAppDirect.xml) ---

    def _command(self, cmd: str) -> None:
        """Send control command via formiPhoneAppDirect.xml."""
        resp = requests.get(
            f"{self._base}/goform/formiPhoneAppDirect.xml?{cmd}",
            timeout=self._timeout,
        )
        resp.raise_for_status()

    def power_on(self, zone: int = 1) -> None:
        """Power on the specified zone."""
        cmd = {1: "PWON", 2: "Z2ON", 3: "Z3ON"}[zone]
        self._command(cmd)

    def power_standby(self, zone: int = 1) -> None:
        """Set the specified zone to standby."""
        cmd = {1: "PWSTANDBY", 2: "Z2OFF", 3: "Z3OFF"}[zone]
        self._command(cmd)

    def volume_up(self, zone: int = 1) -> None:
        """Increase volume by one step."""
        cmd = {1: "MVUP", 2: "Z2UP", 3: "Z3UP"}[zone]
        self._command(cmd)

    def volume_down(self, zone: int = 1) -> None:
        """Decrease volume by one step."""
        cmd = {1: "MVDOWN", 2: "Z2DOWN", 3: "Z3DOWN"}[zone]
        self._command(cmd)

    def volume_set(self, level: int, zone: int = 1) -> None:
        """Set absolute volume level (0-98, half-step with 5 suffix e.g. 335=-46.5dB)."""
        if zone == 1:
            self._command(f"MV{level:02d}")
        elif zone == 2:
            self._command(f"Z2{level:02d}")
        else:
            self._command(f"Z3{level:02d}")

    def mute_on(self, zone: int = 1) -> None:
        """Enable mute."""
        cmd = {1: "MUON", 2: "Z2MUON", 3: "Z3MUON"}[zone]
        self._command(cmd)

    def mute_off(self, zone: int = 1) -> None:
        """Disable mute."""
        cmd = {1: "MUOFF", 2: "Z2MUOFF", 3: "Z3MUOFF"}[zone]
        self._command(cmd)

    def select_source(self, source: str, zone: int = 1) -> None:
        """Select input source (e.g. 'BD', 'SAT/CBL', 'MPLAY')."""
        if zone == 1:
            self._command(f"SI{source}")
        elif zone == 2:
            self._command(f"Z2{source}")
        else:
            self._command(f"Z3{source}")

    def select_surround_mode(self, mode: str) -> None:
        """Select surround mode (e.g. 'DOLBY ATMOS', 'STEREO', 'AUTO')."""
        self._command(f"MS{mode}")
