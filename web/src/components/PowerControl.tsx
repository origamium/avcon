import { setPower } from '../api/client'

export function PowerControl({
  zone,
  power,
  send,
}: {
  zone: number
  power: string
  send: (fn: () => Promise<unknown>) => Promise<void>
}) {
  const isOn = power === 'ON'

  return (
    <button
      onClick={() => send(() => setPower(zone, isOn ? 'standby' : 'on'))}
      className={`rounded-lg px-4 py-2 text-sm font-medium transition ${
        isOn
          ? 'bg-emerald-600 text-white hover:bg-emerald-700'
          : 'bg-zinc-800 text-zinc-400 hover:bg-zinc-700'
      }`}
    >
      {isOn ? 'ON' : 'STANDBY'}
    </button>
  )
}
