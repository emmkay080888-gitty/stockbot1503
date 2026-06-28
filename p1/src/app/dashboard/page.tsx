'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { TrendingUp, BookOpen, DollarSign, Crown, ArrowRight, BarChart3, Activity, Clock, AlertTriangle } from 'lucide-react'
import { formatCurrency, formatPercent, timeAgo, getSignalColor, formatDate } from '@/lib/utils'

interface DashboardData {
  user: any
  signals: any[]
  lessons: any[]
}

export default function DashboardPage() {
  const { data: session, status } = useSession()
  const [data, setData] = useState<DashboardData | null>(null)
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    if (status === 'unauthenticated') redirect('/auth/login')
    if (status !== 'authenticated') return

    async function fetchData() {
      try {
        const [userRes, signalsRes, lessonsRes] = await Promise.all([
          fetch('/api/users'),
          fetch('/api/signals?limit=5'),
          fetch('/api/lessons?limit=3'),
        ])

        const user = await userRes.json()
        const signals = await signalsRes.json()
        const lessons = await lessonsRes.json()

        setData({ user, signals, lessons })
      } catch (err) {
        console.error('Failed to load dashboard data:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchData()
  }, [status])

  if (loading) {
    return (
      <div className="min-h-[calc(100vh-4rem)] flex items-center justify-center">
        <div className="animate-spin rounded-full h-12 w-12 border-2 border-primary-500 border-t-transparent" />
      </div>
    )
  }

  const tier = session?.user ? (session.user as any).tier || 'free' : 'free'
  const isPro = tier === 'pro'

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4 mb-8">
          <div>
            <h1 className="text-2xl sm:text-3xl font-bold">Welcome back{data?.user?.name ? `, ${data.user.name}` : ''}</h1>
            <p className="text-gray-500 mt-1">
              {isPro ? 'Here\'s your trading overview for today.' : 'Upgrade to Pro to unlock all features.'}
            </p>
          </div>
          {!isPro && (
            <Link
              href="/pricing"
              className="inline-flex items-center gap-2 px-4 py-2 gradient-primary text-white rounded-lg text-sm font-semibold hover:scale-105 transition-all shadow-lg shadow-primary-500/25"
            >
              <Crown className="w-4 h-4" />
              Upgrade to Pro
            </Link>
          )}
        </div>

        {/* Stats Grid */}
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4 mb-8">
          <div className="p-4 rounded-xl bg-gradient-to-br from-primary-500/10 to-primary-600/5 border border-primary-500/20">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-primary-500/20">
                <Activity className="w-5 h-5 text-primary-400" />
              </div>
              <span className="text-sm text-gray-500">Active Signals</span>
            </div>
            <div className="text-2xl font-bold">{data?.signals?.length || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/10 to-emerald-600/5 border border-emerald-500/20">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-emerald-500/20">
                <BookOpen className="w-5 h-5 text-emerald-400" />
              </div>
              <span className="text-sm text-gray-500">Lessons</span>
            </div>
            <div className="text-2xl font-bold">{data?.lessons?.length || 0}</div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/10 to-purple-600/5 border border-purple-500/20">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-purple-500/20">
                <DollarSign className="w-5 h-5 text-purple-400" />
              </div>
              <span className="text-sm text-gray-500">Portfolio Value</span>
            </div>
            <div className="text-2xl font-bold">
              {data?.user?.tradingAccount ? formatCurrency(data.user.tradingAccount.balance) : '$100,000'}
            </div>
          </div>
          <div className="p-4 rounded-xl bg-gradient-to-br from-amber-500/10 to-amber-600/5 border border-amber-500/20">
            <div className="flex items-center gap-3 mb-3">
              <div className="p-2 rounded-lg bg-amber-500/20">
                <Crown className="w-5 h-5 text-amber-400" />
              </div>
              <span className="text-sm text-gray-500">Membership</span>
            </div>
            <div className="text-2xl font-bold capitalize">{tier}</div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Latest Signals */}
          <div className="lg:col-span-2">
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Latest Signals</h2>
              <Link href="/signals" className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1">
                View All <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="space-y-3">
              {isPro ? (
                data?.signals?.map((signal: any) => (
                  <Link
                    key={signal.id}
                    href="/signals"
                    className="block p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all"
                  >
                    <div className="flex items-center justify-between mb-2">
                      <div className="flex items-center gap-3">
                        <span className="text-lg font-bold">{signal.symbol}</span>
                        <span className="text-sm text-gray-500">{signal.name}</span>
                      </div>
                      <span className={`text-sm font-semibold ${getSignalColor(signal.action)}`}>
                        {signal.action.replace('_', ' ').toUpperCase()}
                      </span>
                    </div>
                    <div className="flex items-center gap-6 text-sm text-gray-500">
                      <span>Entry: {formatCurrency(signal.entryPrice)}</span>
                      <span>Target: {formatCurrency(signal.targetPrice)}</span>
                      {signal.stopLoss && <span>Stop: {formatCurrency(signal.stopLoss)}</span>}
                      <span className="flex items-center gap-1"><Clock className="w-3 h-3" />{timeAgo(signal.createdAt)}</span>
                    </div>
                  </Link>
                ))
              ) : (
                <div className="p-8 rounded-xl bg-white/[0.02] border border-gray-800/50 text-center">
                  <Crown className="w-12 h-12 text-yellow-400 mx-auto mb-4" />
                  <h3 className="text-lg font-semibold mb-2">Pro Feature</h3>
                  <p className="text-gray-500 text-sm mb-4">Upgrade to Pro to access real-time stock signals</p>
                  <Link
                    href="/pricing"
                    className="inline-flex items-center gap-2 px-4 py-2 gradient-primary text-white rounded-lg text-sm font-semibold"
                  >
                    Upgrade Now <ArrowRight className="w-4 h-4" />
                  </Link>
                </div>
              )}
            </div>
          </div>

          {/* Learning Progress */}
          <div>
            <div className="flex items-center justify-between mb-4">
              <h2 className="text-lg font-semibold">Continue Learning</h2>
              <Link href="/learn" className="text-sm text-primary-400 hover:text-primary-300 flex items-center gap-1">
                View All <ArrowRight className="w-3 h-3" />
              </Link>
            </div>
            <div className="space-y-3">
              {data?.lessons?.map((lesson: any) => (
                <Link
                  key={lesson.id}
                  href="/learn"
                  className="block p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all"
                >
                  <h3 className="text-sm font-semibold mb-1">{lesson.title}</h3>
                  <p className="text-xs text-gray-500 mb-2">{lesson.description}</p>
                  <div className="flex items-center gap-2">
                    <span className="text-xs px-2 py-0.5 rounded-full bg-primary-500/10 text-primary-400 border border-primary-500/30 capitalize">
                      {lesson.category}
                    </span>
                    <span className="text-xs text-gray-600">{lesson.duration || 'Self-paced'}</span>
                  </div>
                </Link>
              ))}
              {(!data?.lessons || data.lessons.length === 0) && (
                <div className="p-6 rounded-xl bg-white/[0.02] border border-gray-800/50 text-center">
                  <BookOpen className="w-8 h-8 text-primary-500 mx-auto mb-2" />
                  <p className="text-sm text-gray-500">No lessons yet</p>
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Quick Actions */}
        <div className="mt-8">
          <h2 className="text-lg font-semibold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <Link
              href="/signals"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all group"
            >
              <TrendingUp className="w-5 h-5 text-primary-400 group-hover:scale-110 transition-transform" />
              <div>
                <div className="text-sm font-semibold">View Signals</div>
                <div className="text-xs text-gray-500">See latest market opportunities</div>
              </div>
            </Link>
            <Link
              href="/trading"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all group"
            >
              <BarChart3 className="w-5 h-5 text-emerald-400 group-hover:scale-110 transition-transform" />
              <div>
                <div className="text-sm font-semibold">Paper Trade</div>
                <div className="text-xs text-gray-500">Practice with $100K virtual capital</div>
              </div>
            </Link>
            <Link
              href="/learn"
              className="flex items-center gap-4 p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all group"
            >
              <BookOpen className="w-5 h-5 text-amber-400 group-hover:scale-110 transition-transform" />
              <div>
                <div className="text-sm font-semibold">Learn</div>
                <div className="text-xs text-gray-500">Explore educational content</div>
              </div>
            </Link>
          </div>
        </div>

        {/* Risk Disclaimer */}
        <div className="mt-8 p-4 rounded-xl bg-yellow-500/5 border border-yellow-500/20">
          <div className="flex items-start gap-3">
            <AlertTriangle className="w-5 h-5 text-yellow-400 shrink-0 mt-0.5" />
            <div className="text-sm text-yellow-300/70">
              <strong>Risk Disclaimer:</strong> Trading involves substantial risk of loss. The signals and analysis 
              provided are for educational purposes only and should not be considered financial advice. 
              Past performance does not guarantee future results.
            </div>
          </div>
        </div>
      </div>
    </div>
  )
}
