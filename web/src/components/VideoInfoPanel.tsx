import type { VideoInfo } from '../types/avr'

export function VideoInfoPanel({ video }: { video: VideoInfo }) {
  const rows = [
    ['HDMI入力', video.hdmi_in],
    ['HDMI出力', video.hdmi_out],
    ['出力モード', video.output],
  ]

  return (
    <div className="space-y-2">
      <h3 className="text-sm font-semibold text-zinc-400">ビデオ情報</h3>
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
