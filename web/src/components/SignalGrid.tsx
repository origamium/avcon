import type { SignalChannel } from '../types/avr'

export function SignalGrid({ signals }: { signals: SignalChannel[] }) {
  if (signals.length === 0) return null

  // 5列グリッド
  const cols = 5

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-zinc-400">入力信号</h3>
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
      >
        {signals.map((ch, i) => (
          <div
            key={i}
            className={`rounded px-2 py-1.5 text-center text-xs ${
              ch.control > 0
                ? 'bg-blue-900/50 text-blue-300'
                : 'bg-zinc-800/50 text-zinc-600'
            }`}
          >
            {ch.name}
          </div>
        ))}
      </div>
    </div>
  )
}
