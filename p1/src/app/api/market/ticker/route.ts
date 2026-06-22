import { NextResponse } from 'next/server'

const UK_TICKERS = [
  { symbol: '^FTSE', name: 'FTSE 100' },
  { symbol: '^FTMC', name: 'FTSE 250' },
  { symbol: '^FTAS', name: 'FTSE All-Share' },
  { symbol: 'GBPUSD=X', name: 'GBP/USD' },
]

// Cache to avoid hammering Yahoo Finance on every request
let cachedData: TickerData[] | null = null
let lastFetch = 0
const CACHE_TTL = 30_000 // 30 seconds

export interface TickerData {
  symbol: string
  name: string
  value: number
  change: number
  changePercent: number
  up: boolean
}

export async function GET() {
  const now = Date.now()

  // Return cached data if fresh enough
  if (cachedData && now - lastFetch < CACHE_TTL) {
    return NextResponse.json(cachedData)
  }

  try {
    const results = await Promise.allSettled(
      UK_TICKERS.map(async (ticker) => {
        const encodedSymbol = encodeURIComponent(ticker.symbol)
        const url = `https://query1.finance.yahoo.com/v8/finance/chart/${encodedSymbol}?interval=1d&range=1d`

        const res = await fetch(url, {
          headers: {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
          },
        })

        if (!res.ok) throw new Error(`Yahoo Finance returned ${res.status}`)

        const json = await res.json()
        const meta = json?.chart?.result?.[0]?.meta

        if (!meta) throw new Error(`No meta data for ${ticker.symbol}`)

        const price = meta.regularMarketPrice
        const prevClose = meta.previousClose ?? meta.chartPreviousClose ?? price
        const change = price - prevClose
        const changePercent = prevClose > 0 ? (change / prevClose) * 100 : 0

        return {
          symbol: ticker.symbol,
          name: ticker.name,
          value: price,
          change,
          changePercent,
          up: change >= 0,
        }
      })
    )

    const data: TickerData[] = []
    let hasRealData = false

    for (const result of results) {
      if (result.status === 'fulfilled') {
        data.push(result.value)
        hasRealData = true
      } else {
        console.error('Ticker fetch error:', result.reason)
      }
    }

    // If we got at least some real data, cache and return it
    if (hasRealData) {
      cachedData = data
      lastFetch = now
      return NextResponse.json(data)
    }

    // If we have stale cache, return it as fallback
    if (cachedData) {
      return NextResponse.json(cachedData)
    }

    // Last resort: return fallback static data
    return NextResponse.json(getFallbackData())
  } catch (error) {
    console.error('Market ticker error:', error)

    // Return stale cache or fallback
    if (cachedData) {
      return NextResponse.json(cachedData)
    }
    return NextResponse.json(getFallbackData())
  }
}

function getFallbackData(): TickerData[] {
  return [
    { symbol: '^FTSE', name: 'FTSE 100', value: 8123.45, change: 23.33, changePercent: 0.29, up: true },
    { symbol: '^FTMC', name: 'FTSE 250', value: 19567.80, change: -45.20, changePercent: -0.23, up: false },
    { symbol: '^FTAS', name: 'FTSE All-Share', value: 4456.12, change: 12.45, changePercent: 0.28, up: true },
    { symbol: 'GBPUSD=X', name: 'GBP/USD', value: 1.2845, change: 0.0032, changePercent: 0.25, up: true },
  ]
}
