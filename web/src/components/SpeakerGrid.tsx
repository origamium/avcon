import type { SpeakerChannel } from '../types/avr'

export function SpeakerGrid({ speakers }: { speakers: SpeakerChannel[] }) {
  if (speakers.length === 0) return null

  // 5列グリッド
  const cols = 5

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-zinc-400">
        アクティブスピーカー
      </h3>
      <div
        className="grid gap-1"
        style={{ gridTemplateColumns: `repeat(${cols}, 1fr)` }}
      >
        {speakers.map((sp, i) => (
          <div
            key={i}
            className={`rounded px-2 py-1.5 text-center text-xs ${
              sp.control > 0
                ? 'bg-emerald-900/50 text-emerald-300'
                : 'bg-zinc-800/50 text-zinc-600'
            }`}
          >
            {sp.name}
          </div>
        ))}
      </div>
    </div>
  )
}
