'use client'

import { useState, useEffect } from 'react'
import { useSession } from 'next-auth/react'
import { redirect } from 'next/navigation'
import Link from 'next/link'
import { BookOpen, Clock, Filter, Search, ChevronRight, Play, FileText, GraduationCap, BarChart3, TrendingUp, Shield, Brain, Sparkles } from 'lucide-react'
import { getDifficultyColor } from '@/lib/utils'

const categories = [
  { id: 'all', label: 'All', icon: Sparkles },
  { id: 'beginner', label: 'Beginner', icon: GraduationCap },
  { id: 'intermediate', label: 'Intermediate', icon: TrendingUp },
  { id: 'advanced', label: 'Advanced', icon: BarChart3 },
  { id: 'strategy', label: 'Strategy', icon: Brain },
  { id: 'analysis', label: 'Analysis', icon: Shield },
]

const lessonTypes = [
  { id: 'all', label: 'All Types' },
  { id: 'article', label: 'Articles' },
  { id: 'video', label: 'Videos' },
  { id: 'course', label: 'Courses' },
]

export default function LearnPage() {
  const { data: session, status } = useSession()
  const [lessons, setLessons] = useState<any[]>([])
  const [loading, setLoading] = useState(true)
  const [category, setCategory] = useState('all')
  const [type, setType] = useState('all')
  const [searchQuery, setSearchQuery] = useState('')

  useEffect(() => {
    if (status !== 'authenticated') return

    async function fetchLessons() {
      try {
        const params = new URLSearchParams()
        if (category !== 'all') params.set('category', category)
        if (type !== 'all') params.set('type', type)
        
        const res = await fetch(`/api/lessons?${params}`)
        const data = await res.json()
        setLessons(data)
      } catch (err) {
        console.error('Failed to fetch lessons:', err)
      } finally {
        setLoading(false)
      }
    }

    fetchLessons()
  }, [status, category, type])

  const filteredLessons = lessons.filter((l) => {
    const matchesSearch = !searchQuery || 
      l.title.toLowerCase().includes(searchQuery.toLowerCase()) ||
      l.description.toLowerCase().includes(searchQuery.toLowerCase())
    return matchesSearch
  })

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-2xl sm:text-3xl font-bold">Learning Center</h1>
          <p className="text-gray-500 mt-1">Master the stock market with our comprehensive educational content</p>
        </div>

        {/* Category Tabs */}
        <div className="flex flex-wrap gap-2 mb-6">
          {categories.map((cat) => {
            const Icon = cat.icon
            return (
              <button
                key={cat.id}
                onClick={() => setCategory(cat.id)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all ${
                  category === cat.id
                    ? 'gradient-primary text-white shadow-lg shadow-primary-500/25'
                    : 'text-gray-400 bg-gray-900 border border-gray-800 hover:border-gray-700'
                }`}
              >
                <Icon className="w-4 h-4" />
                {cat.label}
              </button>
            )
          })}
        </div>

        {/* Search and Filters */}
        <div className="flex flex-col sm:flex-row gap-4 mb-8">
          <div className="relative flex-1">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-500" />
            <input
              type="text"
              placeholder="Search lessons..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="w-full pl-10 pr-4 py-2.5 bg-gray-900 border border-gray-800 rounded-lg text-sm text-white placeholder-gray-600 focus:outline-none focus:border-primary-500 transition-colors"
            />
          </div>
          <div className="flex gap-2">
            {lessonTypes.map((t) => (
              <button
                key={t.id}
                onClick={() => setType(t.id)}
                className={`px-3 py-2 rounded-lg text-sm transition-all ${
                  type === t.id
                    ? 'bg-primary-500/10 text-primary-400 border border-primary-500/30'
                    : 'text-gray-500 bg-gray-900 border border-gray-800 hover:border-gray-700'
                }`}
              >
                {t.label}
              </button>
            ))}
          </div>
        </div>

        {/* Lessons Grid */}
        {loading ? (
          <div className="flex items-center justify-center py-20">
            <div className="animate-spin rounded-full h-8 w-8 border-2 border-primary-500 border-t-transparent" />
          </div>
        ) : (
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {filteredLessons.map((lesson: any) => (
              <div
                key={lesson.id}
                className="group p-6 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 hover:-translate-y-1 transition-all duration-300 cursor-pointer"
              >
                <div className="flex items-start justify-between mb-4">
                  <div className="flex items-center gap-2">
                    {lesson.type === 'video' && <Play className="w-4 h-4 text-red-400" />}
                    {lesson.type === 'article' && <FileText className="w-4 h-4 text-blue-400" />}
                    {lesson.type === 'course' && <GraduationCap className="w-4 h-4 text-green-400" />}
                    <span className="text-xs text-gray-500 capitalize">{lesson.type}</span>
                  </div>
                  {lesson.premium && (
                    <span className="text-xs text-yellow-400 bg-yellow-400/10 px-2 py-0.5 rounded-full border border-yellow-400/30">
                      Premium
                    </span>
                  )}
                </div>

                <h3 className="text-base font-semibold mb-2 group-hover:text-primary-400 transition-colors">
                  {lesson.title}
                </h3>
                <p className="text-sm text-gray-500 mb-4 line-clamp-2">{lesson.description}</p>

                <div className="flex items-center gap-2 flex-wrap mb-4">
                  <span className={`text-xs px-2 py-0.5 rounded-full ${getDifficultyColor(lesson.difficulty)}`}>
                    {lesson.difficulty}
                  </span>
                  <span className="text-xs text-gray-600 px-2 py-0.5 rounded-full bg-gray-800/50 border border-gray-700/50 capitalize">
                    {lesson.category}
                  </span>
                  {lesson.duration && (
                    <span className="flex items-center gap-1 text-xs text-gray-600">
                      <Clock className="w-3 h-3" />
                      {lesson.duration}
                    </span>
                  )}
                </div>

                <div className="flex items-center justify-between text-sm">
                  {lesson.author && <span className="text-gray-600">by {lesson.author}</span>}
                  <span className="text-primary-400 group-hover:translate-x-1 transition-transform flex items-center gap-1">
                    {lesson.type === 'video' ? 'Watch' : lesson.type === 'course' ? 'Enroll' : 'Read'}
                    <ChevronRight className="w-3 h-3" />
                  </span>
                </div>
              </div>
            ))}

            {filteredLessons.length === 0 && (
              <div className="col-span-full py-20 text-center">
                <BookOpen className="w-12 h-12 text-gray-600 mx-auto mb-4" />
                <p className="text-gray-500">No lessons found matching your filters</p>
              </div>
            )}
          </div>
        )}

        {/* Learning Paths Section */}
        <div className="mt-16">
          <h2 className="text-xl font-bold mb-6">Learning Paths</h2>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {[
              {
                title: 'Stock Market Fundamentals',
                description: 'Start here if you\'re new to trading. Learn the basics of how the stock market works.',
                lessons: 12,
                duration: '4 hours',
                gradient: 'from-green-500 to-emerald-600',
              },
              {
                title: 'Technical Analysis Mastery',
                description: 'Master chart patterns, indicators, and price action trading strategies.',
                lessons: 18,
                duration: '6 hours',
                gradient: 'from-blue-500 to-indigo-600',
              },
              {
                title: 'Advanced Trading Strategies',
                description: 'Learn professional trading strategies including options, futures, and algorithmic trading.',
                lessons: 15,
                duration: '8 hours',
                gradient: 'from-purple-500 to-pink-600',
              },
            ].map((path) => (
              <div
                key={path.title}
                className="p-6 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all"
              >
                <div className={`w-10 h-10 rounded-lg bg-gradient-to-br ${path.gradient} flex items-center justify-center mb-4`}>
                  <GraduationCap className="w-5 h-5 text-white" />
                </div>
                <h3 className="text-base font-semibold mb-2">{path.title}</h3>
                <p className="text-sm text-gray-500 mb-4">{path.description}</p>
                <div className="flex items-center gap-4 text-sm text-gray-600">
                  <span>{path.lessons} lessons</span>
                  <span>{path.duration}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  )
}
