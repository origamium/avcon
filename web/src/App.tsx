import { useCallback, useEffect, useState } from 'react'
import type { SourceEntry } from './types/avr'
import { getSources } from './api/client'
import { useStatus } from './hooks/useStatus'
import { useControl } from './hooks/useControl'
import { Layout } from './components/Layout'
import { PowerControl } from './components/PowerControl'
import { VolumeControl } from './components/VolumeControl'
import { SourceSelector } from './components/SourceSelector'
import { SurroundModeSelector } from './components/SurroundModeSelector'
import { AudioInfoPanel } from './components/AudioInfoPanel'
import { VideoInfoPanel } from './components/VideoInfoPanel'
import { SpeakerGrid } from './components/SpeakerGrid'
import { SignalGrid } from './components/SignalGrid'

function ZoneCard({
  label,
  zone,
  power,
  volume,
  muted,
  source,
  sources,
  send,
}: {
  label: string
  zone: number
  power: string
  volume: { volume: number; limit: number; display_type: string; display_value: string }
  muted: boolean
  source: string
  sources: SourceEntry[]
  send: (fn: () => Promise<unknown>) => Promise<void>
}) {
  const isOn = power === 'ON'

  return (
    <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-4 space-y-4">
      <div className="flex items-center justify-between">
        <h2 className="font-semibold">{label}</h2>
        <PowerControl zone={zone} power={power} send={send} />
      </div>
      {isOn && (
        <>
          <VolumeControl zone={zone} volume={volume} muted={muted} send={send} />
          <SourceSelector zone={zone} current={source} sources={sources} send={send} />
        </>
      )}
    </section>
  )
}

export default function App() {
  const { status, error, refresh } = useStatus()
  const { send } = useControl(refresh)
  const [sources, setSources] = useState<SourceEntry[]>([])

  const fetchSources = useCallback(async () => {
    try {
      const { sources } = await getSources()
      setSources(sources)
    } catch {
      // ポーリングに影響させない
    }
  }, [])

  useEffect(() => {
    fetchSources()
  }, [fetchSources])

  if (error && !status) {
    return (
      <Layout name="avcon" connected={false}>
        <div className="rounded-xl border border-red-900 bg-red-950/50 p-6 text-center">
          <p className="text-red-400">AVRに接続できません</p>
          <p className="mt-1 text-xs text-red-500">{error}</p>
        </div>
      </Layout>
    )
  }

  if (!status) {
    return (
      <Layout name="avcon" connected={false}>
        <div className="flex justify-center py-12">
          <div className="h-8 w-8 animate-spin rounded-full border-2 border-zinc-700 border-t-blue-500" />
        </div>
      </Layout>
    )
  }

  const zones = [
    { key: 'zone1' as const, label: 'メインゾーン', zone: 1 },
    { key: 'zone2' as const, label: 'Zone 2', zone: 2 },
    { key: 'zone3' as const, label: 'Zone 3', zone: 3 },
  ]

  return (
    <Layout name={status.friendly_name} connected={!error}>
      {/* ゾーンカード */}
      {zones.map((z) => (
        <ZoneCard
          key={z.key}
          label={z.label}
          zone={z.zone}
          power={status.power[z.key]}
          volume={status.volume[z.key]}
          muted={status.mute[z.key]}
          source={status.source[z.key]}
          sources={sources}
          send={send}
        />
      ))}

      {/* オーディオ / ビデオ情報 */}
      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <AudioInfoPanel audio={status.audio} />
        </section>
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <VideoInfoPanel video={status.video} />
        </section>
      </div>

      {/* サラウンドモード */}
      <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
        <SurroundModeSelector currentMode={status.surround_mode} send={send} />
      </section>

      {/* スピーカー / シグナル グリッド */}
      <div className="grid gap-6 md:grid-cols-2">
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <SpeakerGrid speakers={status.active_speaker} />
        </section>
        <section className="rounded-xl border border-zinc-800 bg-zinc-900 p-4">
          <SignalGrid signals={status.input_signal} />
        </section>
      </div>
    </Layout>
  )
}
