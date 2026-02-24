"""FastAPI server for DENON AVR web control."""

from __future__ import annotations

import dataclasses
import os
import threading
from pathlib import Path
from typing import Any

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel

from avcon.client import DenonAPIError, DenonAVR

load_dotenv()

_HOST = os.getenv("D_AVAMP_IP", "192.168.1.23")
_avr = DenonAVR(_HOST)
_lock = threading.Lock()

app = FastAPI(title="avcon", version="0.1.0")

# 開発時 CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_methods=["*"],
    allow_headers=["*"],
)


# --- ヘルパー ---


def _dc_to_dict(obj: Any) -> Any:
    """Convert dataclass (or list of dataclasses) to dict."""
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        return dataclasses.asdict(obj)
    if isinstance(obj, list):
        return [_dc_to_dict(item) for item in obj]
    return obj


def _call(fn: Any, *args: Any, **kwargs: Any) -> Any:
    """Execute AVR function with lock, convert DenonAPIError to 502."""
    with _lock:
        try:
            return fn(*args, **kwargs)
        except DenonAPIError as e:
            raise HTTPException(status_code=502, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=502, detail=f"AVR通信エラー: {e}")


# --- 読み取り API ---


@app.get("/api/status")
def get_status() -> dict:
    """全ゾーンステータス集約（メインポーリング用）。"""
    power = _call(_avr.get_all_zone_power)
    volume = _call(_avr.get_all_zone_volume)
    mute = _call(_avr.get_all_zone_mute)
    source = _call(_avr.get_all_zone_source)
    surround = _call(_avr.get_surround_mode)
    audio = _call(_avr.get_audio_info)
    video = _call(_avr.get_video_info)
    input_signal = _call(_avr.get_input_signal)
    active_speaker = _call(_avr.get_active_speaker)
    friendly_name = _call(_avr.get_friendly_name)

    return {
        "friendly_name": friendly_name,
        "power": _dc_to_dict(power),
        "volume": _dc_to_dict(volume),
        "mute": _dc_to_dict(mute),
        "source": _dc_to_dict(source),
        "surround_mode": surround,
        "audio": _dc_to_dict(audio),
        "video": _dc_to_dict(video),
        "input_signal": _dc_to_dict(input_signal),
        "active_speaker": _dc_to_dict(active_speaker),
    }


@app.get("/api/sound-modes")
def get_sound_modes() -> dict:
    """利用可能サラウンドモード一覧。"""
    genre, modes = _call(_avr.get_sound_mode_list)
    return {"genre": genre, "modes": _dc_to_dict(modes)}


@app.get("/api/sources")
def get_sources() -> dict:
    """ソース一覧（カスタム名付き）。"""
    deleted = _call(_avr.get_deleted_sources)
    rename = _call(_avr.get_rename_source)
    sources = []
    for entry in deleted:
        if entry.enabled:
            sources.append({
                "name": entry.name,
                "func_name": entry.func_name,
                "display_name": rename.get(entry.name, entry.name),
            })
    return {"sources": sources}


# --- 制御 API ---


class PowerRequest(BaseModel):
    zone: int = 1
    state: str  # "on" | "standby"


class VolumeSetRequest(BaseModel):
    zone: int = 1
    level: int


class ZoneRequest(BaseModel):
    zone: int = 1


class MuteRequest(BaseModel):
    zone: int = 1
    state: str  # "on" | "off" | "toggle"


class SourceRequest(BaseModel):
    zone: int = 1
    source: str


class SurroundRequest(BaseModel):
    mode: str


@app.post("/api/power")
def set_power(req: PowerRequest) -> dict:
    """電源制御。"""
    if req.state == "on":
        _call(_avr.power_on, req.zone)
    else:
        _call(_avr.power_standby, req.zone)
    return {"ok": True}


@app.post("/api/volume")
def set_volume(req: VolumeSetRequest) -> dict:
    """絶対音量設定。"""
    _call(_avr.volume_set, req.level, req.zone)
    return {"ok": True}


@app.post("/api/volume/up")
def volume_up(req: ZoneRequest) -> dict:
    """音量+。"""
    _call(_avr.volume_up, req.zone)
    return {"ok": True}


@app.post("/api/volume/down")
def volume_down(req: ZoneRequest) -> dict:
    """音量-。"""
    _call(_avr.volume_down, req.zone)
    return {"ok": True}


@app.post("/api/mute")
def set_mute(req: MuteRequest) -> dict:
    """ミュート制御。"""
    if req.state == "on":
        _call(_avr.mute_on, req.zone)
    elif req.state == "off":
        _call(_avr.mute_off, req.zone)
    else:
        # トグル: 現在の状態を確認して反転
        mute = _call(_avr.get_all_zone_mute)
        zone_key = f"zone{req.zone}"
        current = getattr(mute, zone_key, False)
        if current:
            _call(_avr.mute_off, req.zone)
        else:
            _call(_avr.mute_on, req.zone)
    return {"ok": True}


@app.post("/api/source")
def set_source(req: SourceRequest) -> dict:
    """ソース切替。"""
    _call(_avr.select_source, req.source, req.zone)
    return {"ok": True}


@app.post("/api/surround")
def set_surround(req: SurroundRequest) -> dict:
    """サラウンドモード切替。"""
    _call(_avr.select_surround_mode, req.mode)
    return {"ok": True}


# --- 静的ファイル配信 (本番用) ---

_DIST = Path(__file__).resolve().parent.parent / "web" / "dist"

if _DIST.is_dir():
    app.mount("/assets", StaticFiles(directory=_DIST / "assets"), name="assets")

    @app.get("/{full_path:path}")
    def spa_fallback(full_path: str) -> FileResponse:
        """SPA fallback: 未マッチパスは index.html を返す。"""
        file_path = _DIST / full_path
        if file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(_DIST / "index.html")
