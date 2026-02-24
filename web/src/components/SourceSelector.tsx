import type { SourceEntry } from '../types/avr'
import { setSource } from '../api/client'

export function SourceSelector({
  zone,
  current,
  sources,
  send,
}: {
  zone: number
  current: string
  sources: SourceEntry[]
  send: (fn: () => Promise<unknown>) => Promise<void>
}) {
  return (
    <div className="flex flex-wrap gap-2">
      {sources.map((s) => (
        <button
          key={s.name}
          onClick={() => send(() => setSource(zone, s.name))}
          className={`rounded-md px-3 py-1.5 text-xs font-medium transition ${
            current === s.name
              ? 'bg-blue-600 text-white'
              : 'bg-zinc-800 text-zinc-300 hover:bg-zinc-700'
          }`}
        >
          {s.display_name}
        </button>
      ))}
    </div>
  )
}
