import { useCallback, useEffect, useRef, useState } from 'react'
import type { AVRStatus } from '../types/avr'
import { getStatus } from '../api/client'

const POLL_INTERVAL = 3000

export function useStatus() {
  const [status, setStatus] = useState<AVRStatus | null>(null)
  const [error, setError] = useState<string | null>(null)
  const timerRef = useRef<ReturnType<typeof setTimeout>>(undefined)

  const refresh = useCallback(async () => {
    try {
      const data = await getStatus()
      setStatus(data)
      setError(null)
    } catch (e) {
      setError(e instanceof Error ? e.message : String(e))
    }
  }, [])

  useEffect(() => {
    let active = true

    const poll = async () => {
      if (!active) return
      await refresh()
      if (active) {
        timerRef.current = setTimeout(poll, POLL_INTERVAL)
      }
    }

    poll()
    return () => {
      active = false
      clearTimeout(timerRef.current)
    }
  }, [refresh])

  return { status, error, refresh }
}
