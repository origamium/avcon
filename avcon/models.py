"""Response dataclasses for DENON AVR API."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass
class DeviceInfo:
    """GET Deviceinfo.xml response."""

    model: str
    mac_address: str
    api_version: str


@dataclass
class Status:
    """GET MainZoneXmlStatusLite.xml response."""

    power: str
    source: str
    volume: float
    mute: str
    volume_display: str


@dataclass
class ZonePower:
    """GetAllZonePowerStatus response."""

    zone1: str
    zone2: str
    zone3: str


@dataclass
class ZoneSource:
    """GetAllZoneSource response."""

    zone1: str
    zone2: str
    zone3: str


@dataclass
class ZoneVolumeInfo:
    """Single zone volume info (part of ZoneVolume)."""

    volume: float
    limit: float
    display_type: str
    display_value: str


@dataclass
class ZoneVolume:
    """GetAllZoneVolume response."""

    zone1: ZoneVolumeInfo
    zone2: ZoneVolumeInfo
    zone3: ZoneVolumeInfo


@dataclass
class ZoneMute:
    """GetAllZoneMuteStatus response."""

    zone1: bool
    zone2: bool
    zone3: bool


@dataclass
class AllZoneStereo:
    """GetAllZoneStereo response."""

    available: bool
    enabled: bool
    zones: str
    selections: str


@dataclass
class ToneControl:
    """GetToneControl response."""

    available: bool
    adjust: bool
    bass_level: str
    treble_level: str
    bass_value: int
    treble_value: int


@dataclass
class SubwooferLevel:
    """GetSubwooferLevel response."""

    sw1_name: str
    sw1_active: bool
    sw1_level: str
    sw1_value: int
    sw2_name: str
    sw2_active: bool
    sw2_level: str
    sw2_value: int


@dataclass
class ChannelLevel:
    """Single channel level (part of GetChLevel response)."""

    name: str
    active: bool
    speaker_type: int
    level: str
    value: int


@dataclass
class SourceEntry:
    """Single source entry (part of GetDeletedSource response)."""

    name: str
    func_name: str
    enabled: bool


@dataclass
class QuickSelect:
    """Single quick select preset (part of GetQuickSelectName response)."""

    name: str
    source: str


@dataclass
class AutoStandby:
    """Single zone auto standby (part of GetAutoStandby response)."""

    zone: str
    value: int


@dataclass
class EcoSettings:
    """GetECO response."""

    available: bool
    mode: int
    power_on_default: int
    display: int


@dataclass
class AudioInfo:
    """GetAudioInfo response."""

    input_mode: str
    output: str
    signal: str
    sound: str
    sample_rate: str


@dataclass
class VideoInfo:
    """GetVideoInfo response."""

    output: str
    hdmi_in: str
    hdmi_out: str


@dataclass
class SignalChannel:
    """Single input signal channel (part of GetInputSignal response)."""

    name: str
    control: int


@dataclass
class SpeakerChannel:
    """Single active speaker (part of GetActiveSpeaker response)."""

    name: str
    control: int


@dataclass
class SoundMode:
    """GetSoundMode response."""

    movie: bool
    music: bool
    game: bool
    pure: bool


@dataclass
class SoundModeEntry:
    """Single sound mode entry (part of GetSoundModeList response)."""

    number: int
    name: str
    selected: bool


@dataclass
class SurroundParameter:
    """GetSurroundParameter response."""

    center_image: str
    dimension: str
    center_width: str
    panorama: str


@dataclass
class AudysseySettings:
    """GetAudyssey response."""

    dynamic_eq: int
    ref_level_offset: int
    dynamic_vol: int
    multeq: int


@dataclass
class NetworkInfo:
    """GetNetworkInfo response."""

    dhcp: str
    ssid: str
    connection: str
