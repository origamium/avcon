import type { AudioInfo } from '../types/avr'

export function AudioInfoPanel({ audio }: { audio: AudioInfo }) {
  const rows = [
    ['入力', audio.input_mode],
    ['信号', audio.signal],
    ['出力', audio.output],
    ['サウンド', audio.sound],
    ['サンプルレート', audio.sample_rate],
  ]

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-zinc-400">オーディオ情報</h3>
      <div className="grid grid-cols-[auto_1fr] gap-x-4 gap-y-1 text-sm">
        {rows.map(([label, value]) => (
          <div key={label} className="contents">
            <span className="text-zinc-500">{label}</span>
            <span className="font-mono text-zinc-200">{value || '---'}</span>
          </div>
        ))}
      </div>
    </div>
  )
}
