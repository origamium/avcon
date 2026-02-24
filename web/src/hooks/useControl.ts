import { useCallback, useState } from 'react'

const REFRESH_DELAY = 300

export function useControl(refresh: () => Promise<void>) {
  const [busy, setBusy] = useState(false)

  const send = useCallback(
    async (fn: () => Promise<unknown>) => {
      setBusy(true)
      try {
        await fn()
        // コマンド反映待ち後にステータス再取得
        await new Promise((r) => setTimeout(r, REFRESH_DELAY))
        await refresh()
      } finally {
        setBusy(false)
      }
    },
    [refresh],
  )

  return { send, busy }
}
