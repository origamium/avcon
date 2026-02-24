export interface ZoneVolumeInfo {
  volume: number
  limit: number
  display_type: string
  display_value: string
}

export interface ZonePower {
  zone1: string
  zone2: string
  zone3: string
}

export interface ZoneSource {
  zone1: string
  zone2: string
  zone3: string
}

export interface ZoneVolume {
  zone1: ZoneVolumeInfo
  zone2: ZoneVolumeInfo
  zone3: ZoneVolumeInfo
}

export interface ZoneMute {
  zone1: boolean
  zone2: boolean
  zone3: boolean
}

export interface AudioInfo {
  input_mode: string
  output: string
  signal: string
  sound: string
  sample_rate: string
}

export interface VideoInfo {
  output: string
  hdmi_in: string
  hdmi_out: string
}

export interface SignalChannel {
  name: string
  control: number
}

export interface SpeakerChannel {
  name: string
  control: number
}

export interface SoundModeEntry {
  number: number
  name: string
  selected: boolean
}

export interface SourceEntry {
  name: string
  func_name: string
  display_name: string
}

export interface AVRStatus {
  friendly_name: string
  power: ZonePower
  volume: ZoneVolume
  mute: ZoneMute
  source: ZoneSource
  surround_mode: string
  audio: AudioInfo
  video: VideoInfo
  input_signal: SignalChannel[]
  active_speaker: SpeakerChannel[]
}
