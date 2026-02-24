import type { ReactNode } from 'react'

export function Layout({
  name,
  connected,
  children,
}: {
  name: string
  connected: boolean
  children: ReactNode
}) {
  return (
    <div className="mx-auto max-w-5xl px-4 py-6">
      <header className="mb-6 flex items-center justify-between border-b border-zinc-800 pb-4">
        <h1 className="text-xl font-bold tracking-tight">{name || 'avcon'}</h1>
        <span
          className={`inline-flex items-center gap-1.5 text-xs ${connected ? 'text-emerald-400' : 'text-red-400'}`}
        >
          <span
            className={`h-2 w-2 rounded-full ${connected ? 'bg-emerald-400' : 'bg-red-400'}`}
          />
          {connected ? '接続中' : '切断'}
        </span>
      </header>
      <main className="space-y-6">{children}</main>
    </div>
  )
}
