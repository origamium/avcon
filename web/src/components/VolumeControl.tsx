import type { ZoneVolumeInfo } from '../types/avr'
import { setMute, setVolume, volumeDown, volumeUp } from '../api/client'

export function VolumeControl({
  zone,
  volume,
  muted,
  send,
}: {
  zone: number
  volume: ZoneVolumeInfo
  muted: boolean
  send: (fn: () => Promise<unknown>) => Promise<void>
}) {
  // dB表示: volume - 80 (例: 34.5 → -45.5dB)
  const db = volume.volume - 80
  const dbStr = db <= -80 ? '---' : `${db > 0 ? '+' : ''}${db.toFixed(1)} dB`

  // スライダー: 0〜98 (APIスケール)
  const sliderValue = volume.volume

  return (
    <div className="flex items-center gap-3">
      <button
        onClick={() => send(() => volumeDown(zone))}
        className="rounded bg-zinc-800 px-2 py-1 text-sm hover:bg-zinc-700"
      >
        −
      </button>
      <input
        type="range"
        min={0}
        max={98}
        step={0.5}
        value={sliderValue}
        onChange={(e) =>
          send(() => setVolume(zone, parseFloat(e.target.value)))
        }
        className="h-2 flex-1 cursor-pointer accent-blue-500"
      />
      <button
        onClick={() => send(() => volumeUp(zone))}
        className="rounded bg-zinc-800 px-2 py-1 text-sm hover:bg-zinc-700"
      >
        +
      </button>
      <span className="w-24 text-right font-mono text-sm text-zinc-300">
        {dbStr}
      </span>
      <button
        onClick={() => send(() => setMute(zone, 'toggle'))}
        className={`rounded px-2 py-1 text-xs font-medium ${
          muted
            ? 'bg-red-600 text-white'
            : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
        }`}
      >
        {muted ? 'MUTED' : 'MUTE'}
      </button>
    </div>
  )
}
