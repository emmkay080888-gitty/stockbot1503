'use client'

import { useState, useEffect, useCallback } from 'react'

interface TickerData {
  symbol: string
  name: string
  value: number
  change: number
  changePercent: number
  up: boolean
}

export function MarketTicker() {
  const [tickers, setTickers] = useState<TickerData[]>([])
  const [error, setError] = useState(false)

  const fetchTickers = useCallback(async () => {
    try {
      const res = await fetch('/api/market/ticker')
      if (!res.ok) throw new Error('Failed to fetch')
      const data = await res.json()
      setTickers(data)
      setError(false)
    } catch {
      setError(true)
    }
  }, [])

  useEffect(() => {
    fetchTickers()
    const interval = setInterval(fetchTickers, 30_000) // Poll every 30s
    return () => clearInterval(interval)
  }, [fetchTickers])

  // Use fallback static data if we haven't loaded yet
  const displayData = tickers.length > 0 ? tickers : [
    { symbol: '^FTSE', name: 'FTSE 100', value: 8123.45, change: 23.33, changePercent: 0.29, up: true },
    { symbol: '^FTMC', name: 'FTSE 250', value: 19567.80, change: -45.20, changePercent: -0.23, up: false },
    { symbol: '^FTAS', name: 'FTSE All-Share', value: 4456.12, change: 12.45, changePercent: 0.28, up: true },
    { symbol: 'GBPUSD=X', name: 'GBP/USD', value: 1.2845, change: 0.0032, changePercent: 0.25, up: true },
  ]

  return (
    <div className="w-full mb-4 overflow-hidden">
      <div className="relative bg-gray-950/80 border border-gray-800/50 rounded-xl p-3 sm:p-4 backdrop-blur-sm">
        <div className="flex items-center gap-4 sm:gap-6 animate-scroll">
          {[...displayData, ...displayData, ...displayData].map((ticker, i) => (
            <div key={i} className="flex items-center gap-3 sm:gap-4 whitespace-nowrap shrink-0">
              <span className="text-gray-300 font-semibold text-sm sm:text-base">{ticker.name}</span>
              <span className="text-white font-bold tabular-nums text-sm sm:text-base">
                {ticker.symbol === 'GBPUSD=X' ? ticker.value.toFixed(4) : ticker.value.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
              </span>
              <span className={`font-semibold text-sm sm:text-base ${ticker.up ? 'text-green-400' : 'text-red-400'}`}>
                <span className="inline-block w-3 sm:w-4">{ticker.up ? '▲' : '▼'}</span>
                {ticker.up ? '+' : ''}{ticker.changePercent.toFixed(2)}%
              </span>
              {/* Separator */}
              <span className="text-gray-700 text-lg sm:text-xl font-light mx-1 sm:mx-2">|</span>
            </div>
          ))}
        </div>
        {error && (
          <span className="absolute top-1 right-2 text-xs text-yellow-500" title="Using cached data">●</span>
        )}
      </div>
    </div>
  )
}
