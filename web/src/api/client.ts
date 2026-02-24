import type { AVRStatus, SoundModeEntry, SourceEntry } from '../types/avr'

const BASE = '/api'

async function fetchJSON<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE}${path}`, init)
  if (!res.ok) {
    const text = await res.text().catch(() => res.statusText)
    throw new Error(`API error ${res.status}: ${text}`)
  }
  return res.json()
}

function postJSON<T>(path: string, body: Record<string, unknown>): Promise<T> {
  return fetchJSON<T>(path, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body),
  })
}

// 読み取り
export const getStatus = () => fetchJSON<AVRStatus>('/status')
export const getSoundModes = () =>
  fetchJSON<{ genre: number; modes: SoundModeEntry[] }>('/sound-modes')
export const getSources = () =>
  fetchJSON<{ sources: SourceEntry[] }>('/sources')

// 制御
export const setPower = (zone: number, state: 'on' | 'standby') =>
  postJSON('/power', { zone, state })
export const setVolume = (zone: number, level: number) =>
  postJSON('/volume', { zone, level })
export const volumeUp = (zone: number) =>
  postJSON('/volume/up', { zone })
export const volumeDown = (zone: number) =>
  postJSON('/volume/down', { zone })
export const setMute = (zone: number, state: 'on' | 'off' | 'toggle') =>
  postJSON('/mute', { zone, state })
export const setSource = (zone: number, source: string) =>
  postJSON('/source', { zone, source })
export const setSurround = (mode: string) =>
  postJSON('/surround', { mode })
