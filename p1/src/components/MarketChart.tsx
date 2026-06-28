'use client'

import { useState, useEffect } from 'react'
import { MarketTicker } from './MarketTicker'

interface Candle {
  time: number
  open: number
  high: number
  low: number
  close: number
  volume: number
}

function generateCandle(prevClose: number, trend: 'up' | 'down' | 'sideways'): Candle {
  const volatility = prevClose * 0.008
  const trendBias = trend === 'up' ? 0.004 : trend === 'down' ? -0.004 : 0
  const open = prevClose + (Math.random() - 0.5) * volatility * 0.5
  const close = open + (Math.random() - 0.5 + trendBias * 100) * volatility * 0.6
  const high = Math.max(open, close) + Math.random() * volatility * 0.4
  const low = Math.min(open, close) - Math.random() * volatility * 0.4
  const volume = Math.floor(500000 + Math.random() * 2000000)
  return { time: Date.now(), open, high, low, close, volume }
}

export function MarketChart() {
  const [candles, setCandles] = useState<Candle[]>([])
  const [visibleCount, setVisibleCount] = useState(0)
  const [isForming, setIsForming] = useState(false)
  const [currentCandle, setCurrentCandle] = useState<Candle | null>(null)
  const [currentPrice, setCurrentPrice] = useState<number>(4200)
  // Initialize candles
  useEffect(() => {
    const initialCandles: Candle[] = []
    let price = 4200
    for (let i = 0; i < 50; i++) {
      const t = i < 20 ? 'up' : i < 35 ? 'sideways' : 'down'
      const candle = generateCandle(price, t as any)
      initialCandles.push(candle)
      price = candle.close
    }
    setCandles(initialCandles)
    setCurrentPrice(price)
    setVisibleCount(30)
  }, [])

  // Animate candles forming
  useEffect(() => {
    if (candles.length === 0) return

    const animate = () => {
      // Every few seconds add a new candle with animation
      if (!isForming) {
        setIsForming(true)
        setCurrentCandle(null)

        // Create the new candle
        const nextTrend = Math.random() < 0.4 ? 'up' : Math.random() < 0.7 ? 'down' : 'sideways'
        
        const newCandle = generateCandle(currentPrice, nextTrend)
        
        // Animate the candle forming (wick then body)
        let progress = 0
        const formInterval = setInterval(() => {
          progress += 0.04
          if (progress >= 1) {
            clearInterval(formInterval)
            setCandles(prev => [...prev, newCandle])
            setCurrentPrice(newCandle.close)
            setCurrentCandle(null)
            setVisibleCount(prev => prev + 1)
            setIsForming(false)
            

          } else {
            setCurrentCandle({
              ...newCandle,
              high: newCandle.open + (newCandle.high - newCandle.open) * Math.min(progress * 2, 1),
              low: newCandle.open - (newCandle.open - newCandle.low) * Math.min(progress * 2, 1),
              close: newCandle.open + (newCandle.close - newCandle.open) * Math.min(progress * 1.5, 1),
            })
          }
        }, 50) // Fast animation speed
      }
    }

    const timer = setInterval(animate, 2200)
    return () => clearInterval(timer)
  }, [candles.length, isForming, currentPrice])

  // Get visible candles
  const startIdx = Math.max(0, visibleCount - 35)
  const visibleCandles = candles.slice(startIdx, visibleCount)
  const allVisible = currentCandle ? [...visibleCandles, currentCandle] : visibleCandles

  // Chart dimensions
  const width = 500
  const height = 360
  const padding = { top: 20, right: 50, bottom: 40, left: 10 }
  const chartW = width - padding.left - padding.right
  const chartH = height - padding.top - padding.bottom

  // Calculate scales
  const prices = allVisible.flatMap(c => [c.high, c.low])
  const minPrice = Math.min(...prices) * 0.998
  const maxPrice = Math.max(...prices) * 1.002
  const priceRange = maxPrice - minPrice

  const volumes = allVisible.map(c => c.volume)
  const maxVolume = Math.max(...volumes)

  const candleW = Math.min(chartW / allVisible.length * 0.7, 8)
  const gap = chartW / allVisible.length

  const getY = (price: number) => padding.top + chartH - ((price - minPrice) / priceRange) * chartH
  const getVolumeH = (vol: number) => (vol / maxVolume) * chartH * 0.25

  return (
    <div className="w-full mx-auto h-full flex flex-col">
      {/* Real UK Market Ticker Tape */}
      <MarketTicker />

      {/* Chart */}
      <div className="relative flex-1 bg-gray-950/60 border border-gray-800/50 rounded-xl p-2 backdrop-blur-sm flex items-center">
        <svg viewBox={`0 0 ${width} ${height}`} className="w-full h-auto">
          {/* Grid lines */}
          {Array.from({ length: 6 }).map((_, i) => {
            const y = padding.top + (chartH / 5) * i
            const price = maxPrice - (priceRange / 5) * i
            return (
              <g key={i}>
                <line x1={padding.left} y1={y} x2={width - padding.right} y2={y} stroke="#1f2937" strokeWidth="0.5" />
                <text x={width - padding.right + 4} y={y + 3} fill="#6b7280" fontSize="9" textAnchor="start">
                  {price.toFixed(1)}
                </text>
              </g>
            )
          })}

          {/* Candles */}
          {allVisible.map((candle, i) => {
            const x = padding.left + i * gap + gap / 2
            const isUp = candle.close >= candle.open
            const color = isUp ? '#22c55e' : '#ef4444'
            const opacity = i === allVisible.length - 1 && !currentCandle ? 0.6 : 1

            return (
              <g key={i} opacity={opacity}>
                {/* Wick */}
                <line
                  x1={x}
                  y1={getY(candle.high)}
                  x2={x}
                  y2={getY(candle.low)}
                  stroke={color}
                  strokeWidth="1"
                  strokeLinecap="round"
                />
                {/* Body */}
                <rect
                  x={x - candleW / 2}
                  y={getY(Math.max(candle.open, candle.close))}
                  width={candleW}
                  height={Math.max(1, Math.abs(getY(candle.open) - getY(candle.close)))}
                  fill={color}
                  rx="0.5"
                  className="transition-all duration-75"
                />
                {/* Volume bar */}
                <rect
                  x={x - candleW / 2}
                  y={height - padding.bottom + 2}
                  width={candleW}
                  height={getVolumeH(candle.volume)}
                  fill={color}
                  opacity="0.15"
                  rx="0.5"
                />
              </g>
            )
          })}

          {/* Latest price label */}
          {allVisible.length > 0 && (
            <g>
              <rect
                x={width - 65}
                y={padding.top - 2}
                width="60"
                height="16"
                rx="3"
                fill={currentPrice >= (allVisible[allVisible.length - 1]?.open || currentPrice) ? '#22c55e' : '#ef4444'}
                opacity="0.15"
              />
              <text
                x={width - 35}
                y={padding.top + 10}
                fill={currentPrice >= (allVisible[allVisible.length - 1]?.open || currentPrice) ? '#22c55e' : '#ef4444'}
                fontSize="10"
                fontWeight="bold"
                textAnchor="middle"
              >
                ${currentPrice.toFixed(2)}
              </text>
            </g>
          )}
        </svg>
      </div>
    </div>
  )
}
