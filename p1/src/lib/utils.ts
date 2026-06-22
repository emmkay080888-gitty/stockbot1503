import { type ClassValue, clsx } from 'clsx'
import { twMerge } from 'tailwind-merge'

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function formatCurrency(amount: number): string {
  return new Intl.NumberFormat('en-US', {
    style: 'currency',
    currency: 'USD',
    minimumFractionDigits: 2,
    maximumFractionDigits: 2,
  }).format(amount)
}

export function formatPercent(value: number): string {
  return `${value >= 0 ? '+' : ''}${value.toFixed(2)}%`
}

export function formatDate(date: Date | string): string {
  return new Date(date).toLocaleDateString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  })
}

export function timeAgo(date: Date | string): string {
  const now = new Date()
  const past = new Date(date)
  const diffMs = now.getTime() - past.getTime()
  const diffSecs = Math.floor(diffMs / 1000)
  const diffMins = Math.floor(diffSecs / 60)
  const diffHours = Math.floor(diffMins / 60)
  const diffDays = Math.floor(diffHours / 24)

  if (diffDays > 0) return `${diffDays}d ago`
  if (diffHours > 0) return `${diffHours}h ago`
  if (diffMins > 0) return `${diffMins}m ago`
  return 'just now'
}

export function getSignalColor(action: string): string {
  switch (action.toLowerCase()) {
    case 'strong_buy': return 'text-green-400'
    case 'buy': return 'text-emerald-400'
    case 'hold': return 'text-yellow-400'
    case 'sell': return 'text-orange-400'
    case 'strong_sell': return 'text-red-400'
    default: return 'text-gray-400'
  }
}

export function getSignalBgColor(action: string): string {
  switch (action.toLowerCase()) {
    case 'strong_buy': return 'bg-green-500/10 border-green-500/30'
    case 'buy': return 'bg-emerald-500/10 border-emerald-500/30'
    case 'hold': return 'bg-yellow-500/10 border-yellow-500/30'
    case 'sell': return 'bg-orange-500/10 border-orange-500/30'
    case 'strong_sell': return 'bg-red-500/10 border-red-500/30'
    default: return 'bg-gray-500/10 border-gray-500/30'
  }
}

export function getDifficultyColor(difficulty: string): string {
  switch (difficulty.toLowerCase()) {
    case 'beginner': return 'bg-green-500/10 text-green-400 border-green-500/30'
    case 'intermediate': return 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30'
    case 'advanced': return 'bg-red-500/10 text-red-400 border-red-500/30'
    default: return 'bg-gray-500/10 text-gray-400 border-gray-500/30'
  }
}
