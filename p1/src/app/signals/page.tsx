'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { TrendingUp, Filter, Crown, Search, Clock, ArrowRight, AlertTriangle, BarChart3, Target, Shield, Activity } from 'lucide-react'
import { formatCurrency, formatPercent, timeAgo, getSignalColor, getSignalBgColor } from '@/lib/utils'

const sectors = ['All', 'Technology', 'Finance', 'Healthcare', 'Energy', 'Consumer', 'Industrial']
const actions = ['All', 'Strong Buy', 'Buy', 'Hold', 'Sell', 'Strong Sell']
const timeframes = ['All', 'Short Term', 'Medium Term', 'Long Term']

export default function SignalsPage() {
  const { data: session, status } = useSession()
  const [signals, setSignals] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [filterAction, setFilterAction] = useState('All')
  const [filterSector, setFilterSector] = useState('All')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (status === 'unauthenticated') redirect('/auth/login')
    if (status !== 'authenticated') return

    async function fetchSignals() {
      try {
        const params = new URLSearchParams()
        if (filterAction !== 'All') params.set('action', filterAction.toLowerCase().replace(' ', '_'))
        if (filterSector !== 'All') params.set('sector', filterSector.toLowerCase())
        
        const res = await fetch(`/api/signals?${params}`)
        const data = await res.json()
        setSignals(data)
      } catch (err) {
        console.error('Failed to fetch signals:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchSignals()
  }, [status, filterAction, filterSector])

  const tier = session?.user ? (session.user as any).tier || 'free' : 'free'
  const isPro = tier === 'pro'

  if (!isPro) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center px-4">
        <div className="max-w-md text-center">
          <Crown className="w-16 h-16 text-yellow-400 mx-auto mb-6" />
          <h1 className="text-2xl font-bold mb-2">Pro Feature</h1>
          <p className="text-gray-500 mb-6">
            Upgrade to Pro to access real-time stock signals with detailed analysis, 
            entry/exit prices, and risk management recommendations.
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

  const filteredSignals = signals.filter((s) => {
    const matchesSearch = !searchQuery || 
      s.symbol.toLowerCase().includes(searchQuery.toLowerCase()) ||
      s.name.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold">Stock Signals</h1>
          <p className="text-gray-500 mt-1">Professional-grade trading signals with detailed analysis</p>
        </div>

        {/* Stats Overview */}
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="p-4 rounded-xl bg-gradient-to-br from-green-500/10 to-green-600/5 border border-green-500/20">
            <div className="text-sm text-gray-500 mb-1">Buy Signals</div>
            <div className="text-2xl font-bold text-green-400">{signals.filter(s => s.action === 'buy' || s.action === 'strong_buy').length}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-red-500/10 to-red-600/5 border border-red-500/20">
            <div className="text-sm text-gray-500 mb-1">Sell Signals</div>
            <div className="text-2xl font-bold text-red-400">{signals.filter(s => s.action === 'sell' || s.action === 'strong_sell').length}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-yellow-500/10 to-yellow-600/5 border border-yellow-500/20">
            <div className="text-sm text-gray-500 mb-1">Hold</div>
            <div className="text-2xl font-bold text-yellow-400">{signals.filter(s => s.action === 'hold').length}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-blue-500/10 to-blue-600/5 border border-blue-500/20">
            <div className="text-sm text-gray-500 mb-1">Avg Confidence</div>
            <div className="text-2xl font-bold text-blue-400">
              {signals.length > 0 ? Math.round(signals.reduce((a: number, s: any) => a + s.confidence, 0) / signals.length) : 0}%
            </div>
          </div>
        </div>

        {/* Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-6">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search by symbol or company name..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-primary-500 transition-colors"
            />
          </div>
          <div className="flex gap-2">
            <select
              value={filterAction}
              onChange={(e) => setFilterAction(e.target.value)}
              className="px-3 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-primary-500"
            >
              {actions.map((a) => (
                <option key={a} value={a}>{a}</option>
              ))}
            </select>
            <select
              value={filterSector}
              onChange={(e) => setFilterSector(e.target.value)}
              className="px-3 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-sm text-gray-300 focus:outline-none focus:border-primary-500"
            >
              {sectors.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Signals List */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-500 border-t-transparent" />
          </div>
        ) : (
          <div className="space-y-4">
            {filteredSignals.map((signal: any) => (
              <div
                key={signal.id}
                className={`p-6 rounded-xl border ${getSignalBgColor(signal.action)} transition-all hover:scale-[1.01]`}
              >
                <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
                  <div className="flex items-center gap-4">
                    <div>
                      <div className="flex items-center gap-3">
                        <h3 className="text-xl font-bold">{signal.symbol}</h3>
                        <span className="text-sm text-gray-500">{signal.name}</span>
                        <span className={`px-2 py-0.5 text-xs font-semibold rounded-full ${getSignalColor(signal.action)} bg-current/10`}>
                          {signal.action.replace('_', ' ').toUpperCase()}
                        </span>
                      </div>
                    </div>
                  </div>
                  <div className="flex items-center gap-4 text-sm">
                    <span className="flex items-center gap-1 text-gray-500">
                      <Activity className="w-3 h-3" />
                      Confidence: <strong className="text-white">{signal.confidence}%</strong>
                    </span>
                    <span className="text-gray-500 capitalize">{signal.timeframe.replace('_', ' ')}</span>
                  </div>
                </div>

                <div className="grid grid-cols-2 sm:grid-cols-4 gap-4 mb-4">
                  <div>
                    <div className="text-xs text-gray-500">Entry Price</div>
                    <div className="text-lg font-semibold">{formatCurrency(signal.entryPrice)}</div>
                  </div>
                  <div>
                    <div className="text-xs text-gray-500">Target Price</div>
                    <div className="text-lg font-semibold text-green-400">{formatCurrency(signal.targetPrice)}</div>
                  </div>
                  {signal.stopLoss && (
                    <div>
                      <div className="text-xs text-gray-500">Stop Loss</div>
                      <div className="text-lg font-semibold text-red-400">{formatCurrency(signal.stopLoss)}</div>
                    </div>
                  )}
                  <div>
                    <div className="text-xs text-gray-500">Risk Level</div>
                    <div className="text-lg font-semibold capitalize">{signal.riskLevel}</div>
                  </div>
                </div>

                <p className="text-sm text-gray-400 mb-3">{signal.analysis}</p>

                <div className="flex items-center gap-4 text-xs text-gray-600">
                  <span className="flex items-center gap-1"><Clock className="w-3 h-3" /> {timeAgo(signal.createdAt)}</span>
                  {signal.sector && <span className="capitalize">Sector: {signal.sector}</span>}
                  {signal.timeframe && <span className="capitalize">Timeframe: {signal.timeframe.replace('_', ' ')}</span>}
                </div>
              </div>
            ))}

            {filteredSignals.length === 0 && (
              <div className="text-center py-20">
                <BarChart3 className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-500">No signals found matching your filters</p>
              </div>
            )}
          </div>
        )}

        {/* Risk Disclaimer */}
        <div className="mt-8 p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/20">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-300/70">
              <strong>Risk Disclaimer:</strong> Trading signals are for educational and informational purposes only. 
              They do not constitute financial advice. Always do your own research before making investment decisions.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
