import { useCallback, useEffect, useState } from 'react'
import type { SoundModeEntry } from '../types/avr'
import { getSoundModes, setSurround } from '../api/client'

export function SurroundModeSelector({
  currentMode,
  send,
}: {
  currentMode: string
  send: (fn: () => Promise<unknown>) => Promise<void>
}) {
  const [modes, setModes] = useState<SoundModeEntry[]>([])

  const fetchModes = useCallback(async () => {
    try {
      const { modes } = await getSoundModes()
      setModes(modes)
    } catch {
      // ステータスポーリングに影響させない
    }
  }, [])

  useEffect(() => {
    fetchModes()
  }, [fetchModes])

  if (modes.length === 0) return null

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-zinc-400">サラウンドモード</h3>
      <div className="flex flex-wrap gap-2">
        {modes.map((m) => (
          <button
            key={m.number}
            onClick={() => send(() => setSurround(m.name))}
            className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
              m.selected
                ? 'bg-purple-600 text-white'
                : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
            }`}
          >
            {m.name}
          </button>
        ))}
      </div>
      <p className="text-xs text-zinc-500">現在: {currentMode}</p>
    </div>
  )
}
