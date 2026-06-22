'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { DollarSign, TrendingUp, TrendingDown, Plus, Minus, Crown, BarChart3, PieChart, ArrowRight, AlertTriangle, RefreshCw } from 'lucide-react'
import { formatCurrency, formatPercent } from '@/lib/utils'

const popularStocks = [
  { symbol: 'AAPL', name: 'Apple Inc.', price: 178.50, change: 1.2 },
  { symbol: 'GOOGL', name: 'Alphabet Inc.', price: 141.80, change: -0.5 },
  { symbol: 'MSFT', name: 'Microsoft Corp.', price: 378.90, change: 2.1 },
  { symbol: 'AMZN', name: 'Amazon.com Inc.', price: 178.25, change: 0.8 },
  { symbol: 'NVDA', name: 'NVIDIA Corp.', price: 875.30, change: 3.4 },
  { symbol: 'TSLA', name: 'Tesla Inc.', price: 248.60, change: -1.8 },
  { symbol: 'META', name: 'Meta Platforms', price: 505.70, change: 1.5 },
  { symbol: 'JPM', name: 'JPMorgan Chase', price: 198.40, change: -0.3 },
]

export default function TradingPage() {
  const { data: session, status } = useSession()
  const [account, setAccount] = useState<any>(null)
  const [positions, setPositions] = useState<any[]>([])
  const [totalValue, setTotalValue] = useState(100000)
  const [totalReturn, setTotalReturn] = useState(0)
  const [loading, setLoading] = useState(true)
  const [tradeSymbol, setTradeSymbol] = useState('')
  const [tradeShares, setTradeShares] = useState('')
  const [tradeType, setTradeType] = useState<'buy' | 'sell'>('buy')
  const [tradeResult, setTradeResult] = useState<{ success: boolean; message: string } | null>(null)
  const [tradeLoading, setTradeLoading] = useState(false)
  const [selectedStock, setSelectedStock] = useState(popularStocks[0])

  useEffect(() => {
    if (status === 'unauthenticated') redirect('/auth/login')
    if (status !== 'authenticated') return

    fetchAccount()
  }, [status])

  async function fetchAccount() {
    try {
      const res = await fetch('/api/trading')
      if (res.ok) {
        const data = await res.json()
        setAccount(data.account)
        setPositions(data.positions)
        setTotalValue(data.totalValue)
        setTotalReturn(data.totalReturn)
      }
    } catch (err) {
      console.error('Failed to fetch account:', err)
    } finally {
      setLoading(false)
    }
  }

  const tier = session?.user ? (session.user as any).tier || 'free' : 'free'
  const isPro = tier === 'pro'

  if (!isPro) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4">
        <div className="max-w-md text-center">
          <Crown className="w-16 h-16 text-yellow-400 mx-auto mb-6" />
          <h1 className="text-2xl font-bold mb-2">Pro Feature</h1>
          <p className="text-gray-500 mb-6">
            Upgrade to Pro to access the simulated trading platform with $100,000 virtual capital 
            to practice your strategies risk-free.
          </p>
          <Link
            href="/pricing"
            className="inline-flex items-center gap-2 px-6 py-3 gradient-primary text-white rounded-xl font-semibold hover:scale-105 transition-all shadow-lg shadow-primary-500/25"
          >
            <Crown className="w-4 h-4" />
            Upgrade to Pro
          </Link>
        </div>
      </div>
    )
  }

  async function executeTrade() {
    if (!tradeSymbol || !tradeShares) return

    const shares = parseFloat(tradeShares)
    if (isNaN(shares) || shares <= 0) return

    setTradeLoading(true)
    setTradeResult(null)

    try {
      const res = await fetch('/api/trading', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          symbol: tradeSymbol.toUpperCase(),
          action: tradeType,
          shares,
          price: selectedStock.price,
        }),
      })

      const data = await res.json()

      if (res.ok) {
        setTradeResult({ success: true, message: `Successfully ${tradeType === 'buy' ? 'bought' : 'sold'} ${shares} shares of ${tradeSymbol.toUpperCase()}` })
        setTradeShares('')
        fetchAccount()
      } else {
        setTradeResult({ success: false, message: data.error || 'Trade failed' })
      }
    } catch (err) {
      setTradeResult({ success: false, message: 'Failed to execute trade' })
    } finally {
      setTradeLoading(false)
    }
  }

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Simulated Trading</h1>
            <p className="text-gray-500 mt-1">Practice trading with $100,000 virtual capital</p>
          </div>
          <button
            onClick={fetchAccount}
            className="flex items-center gap-2 px-4 py-2 text-sm text-gray-400 border border-gray-800 rounded-lg hover:bg-gray-800 transition-all"
          >
            <RefreshCw className="w-4 h-4" />
            Refresh
          </button>
        </div>

        {/* Portfolio Overview */}
        <div className="grid grid-cols-1 sm:grid-cols-3 gap-4 mb-8">
          <div className="p-4 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/5 border border-primary-500/20">
            <div className="text-sm text-gray-500 mb-1">Portfolio Value</div>
            <div className="text-2xl font-bold">{formatCurrency(totalValue)}</div>
          </div>
          <div className={`p-4 rounded-xl border ${totalReturn >= 0 ? 'bg-gradient-to-br from-green-500/10 to-green-600/5 border-green-500/20' : 'bg-gradient-to-br from-red-500/10 to-red-600/5 border-red-500/20'}`}>
            <div className="text-sm text-gray-500 mb-1">Total Return</div>
            <div className={`text-2xl font-bold ${totalReturn >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              {formatPercent(totalReturn)}
            </div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20">
            <div className="text-sm text-gray-500 mb-1">Cash Balance</div>
            <div className="text-2xl font-bold">{formatCurrency(account?.balance || 100000)}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Market Watch + Trade */}
          <div className="space-y-6">
            {/* Market Watch */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-gray-800/50">
              <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
                <BarChart3 className="w-4 h-4 text-primary-400" />
                Market Watch
              </h2>
              <div className="space-y-2">
                {popularStocks.map((stock) => (
                  <button
                    key={stock.symbol}
                    onClick={() => { setSelectedStock(stock); setTradeSymbol(stock.symbol) }}
                    className={`w-full flex items-center justify-between p-2 rounded-lg text-sm transition-all ${
                      selectedStock.symbol === stock.symbol
                        ? 'bg-primary-500/10 border border-primary-500/30'
                        : 'hover:bg-gray-800/50'
                    }`}
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-semibold">{stock.symbol}</span>
                      <span className="text-gray-500 text-xs">{stock.name}</span>
                    </div>
                    <div className="text-right">
                      <div className="font-medium">${stock.price.toFixed(2)}</div>
                      <div className={`text-xs flex items-center gap-1 ${stock.change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                        {stock.change >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                        {stock.change >= 0 ? '+' : ''}{stock.change.toFixed(2)}%
                      </div>
                    </div>
                  </button>
                ))}
              </div>
            </div>

            {/* Trade Form */}
            <div className="p-4 rounded-xl bg-white/[0.02] border border-gray-800/50">
              <h2 className="text-sm font-semibold mb-3">Place Trade</h2>
              <div className="space-y-3">
                <div className="flex gap-2">
                  <button
                    onClick={() => setTradeType('buy')}
                    className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                      tradeType === 'buy'
                        ? 'bg-green-500/20 text-green-400 border border-green-500/30'
                        : 'text-gray-500 border border-gray-800'
                    }`}
                  >
                    <Plus className="w-4 h-4 inline mr-1" />
                    Buy
                  </button>
                  <button
                    onClick={() => setTradeType('sell')}
                    className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${
                      tradeType === 'sell'
                        ? 'bg-red-500/20 text-red-400 border border-red-500/30'
                        : 'text-gray-500 border border-gray-800'
                    }`}
                  >
                    <Minus className="w-4 h-4 inline mr-1" />
                    Sell
                  </button>
                </div>

                <div>
                  <label className="block text-xs text-gray-500 mb-1">Symbol</label>
                  <input
                    type="text"
                    value={tradeSymbol}
                    onChange={(e) => setTradeSymbol(e.target.value.toUpperCase())}
                    placeholder="e.g. AAPL"
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-primary-500"
                  />
                </div>

                <div>
                  <label className="block text-xs text-gray-500 mb-1">Shares</label>
                  <input
                    type="number"
                    value={tradeShares}
                    onChange={(e) => setTradeShares(e.target.value)}
                    placeholder="Number of shares"
                    min={1}
                    className="w-full px-3 py-2 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-primary-500"
                  />
                </div>

                {tradeSymbol && selectedStock && (
                  <div className="text-sm text-gray-500">
                    Est. {tradeType === 'buy' ? 'cost' : 'proceeds'}: <strong className="text-white">
                      {formatCurrency(parseFloat(tradeShares || '0') * selectedStock.price)}
                    </strong>
                  </div>
                )}

                <button
                  onClick={executeTrade}
                  disabled={tradeLoading || !tradeSymbol || !tradeShares}
                  className={`w-full py-2.5 rounded-lg text-sm font-semibold transition-all ${
                    tradeType === 'buy'
                      ? 'bg-green-500/20 text-green-400 border border-green-500/30 hover:bg-green-500/30'
                      : 'bg-red-500/20 text-red-400 border border-red-500/30 hover:bg-red-500/30'
                  } disabled:opacity-50 disabled:cursor-not-allowed`}
                >
                  {tradeLoading ? 'Processing...' : `${tradeType === 'buy' ? 'Buy' : 'Sell'} ${tradeSymbol || 'Stock'}`}
                </button>

                {tradeResult && (
                  <div className={`p-2 rounded-lg text-xs ${
                    tradeResult.success
                      ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                      : 'bg-red-500/10 text-red-400 border border-red-500/30'
                  }`}>
                    {tradeResult.message}
                  </div>
                )}
              </div>
            </div>
          </div>

          {/* Positions */}
          <div className="lg:col-span-2">
            <h2 className="text-sm font-semibold mb-3 flex items-center gap-2">
              <PieChart className="w-4 h-4 text-primary-400" />
              Your Positions
            </h2>
            {positions.length > 0 ? (
              <div className="space-y-3">
                {positions.map((pos: any) => {
                  const pl = (pos.currentPrice - pos.avgPrice) * pos.shares
                  const plPercent = ((pos.currentPrice - pos.avgPrice) / pos.avgPrice) * 100
                  return (
                    <div
                      key={pos.id}
                      className="p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all"
                    >
                      <div className="flex items-center justify-between mb-3">
                        <div className="flex items-center gap-3">
                          <span className="text-lg font-bold">{pos.symbol}</span>
                          <span className="text-sm text-gray-500">{pos.shares} shares</span>
                        </div>
                        <div className="text-right">
                          <div className="font-semibold">{formatCurrency(pos.avgPrice * pos.shares)}</div>
                          <div className={`text-sm flex items-center gap-1 ${pl >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                            {pl >= 0 ? <TrendingUp className="w-3 h-3" /> : <TrendingDown className="w-3 h-3" />}
                            {formatCurrency(pl)} ({formatPercent(plPercent)})
                          </div>
                        </div>
                      </div>
                      <div className="flex items-center justify-between text-sm text-gray-500">
                        <span>Avg Price: {formatCurrency(pos.avgPrice)}</span>
                        <span>Current: {formatCurrency(pos.currentPrice)}</span>
                      </div>
                    </div>
                  )
                })}
              </div>
            ) : (
              <div className="p-12 rounded-xl bg-white/[0.02] border border-gray-800/50 text-center">
                <DollarSign className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">No Positions Yet</h3>
                <p className="text-gray-500 text-sm mb-4">
                  Start trading by selecting a stock from the market watch and placing your first trade.
                </p>
                <p className="text-xs text-gray-600">
                  You have {formatCurrency(account?.balance || 100000)} in buying power
                </p>
              </div>
            )}
          </div>
        </div>

        {/* Risk Disclaimer */}
        <div className="mt-8 p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/20">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-300/70">
              <strong>Important:</strong> This is a simulated trading environment using virtual currency. 
              All prices and market data are for educational purposes. Real trading involves substantial 
              financial risk. Never trade with money you cannot afford to lose.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
