'use client'

import Link from 'next/link'
import Image from 'next/image'
import { ArrowRight, TrendingUp, BookOpen, DollarSign, Shield, BarChart3, Users, Zap, Crown, Check, Star } from 'lucide-react'
import { MarketChart } from '@/components/MarketChart'

const stats = [
  { label: 'Active Members', value: '12,400+' },
  { label: 'Signals Accuracy', value: '87.3%' },
  { label: 'Avg. Monthly Return', value: '+14.2%' },
  { label: 'Educational Hours', value: '500+' },
]

const features = [
  {
    icon: TrendingUp,
    title: 'Pro Stock Signals',
    description: 'Real-time buy/sell signals with detailed analysis, entry prices, stop-losses, and target prices.',
    gradient: 'from-emerald-500 to-teal-500',
  },
  {
    icon: BookOpen,
    title: 'Structured Learning',
    description: 'From beginner to advanced — our curriculum covers technical analysis, fundamental analysis, and trading psychology.',
    gradient: 'from-blue-500 to-indigo-500',
  },
  {
    icon: DollarSign,
    title: 'Simulated Trading',
    description: 'Practice with $100,000 virtual capital. Test strategies risk-free before trading real money.',
    gradient: 'from-purple-500 to-pink-500',
  },
  {
    icon: BarChart3,
    title: 'Advanced Analytics',
    description: 'Track your portfolio performance with detailed metrics, risk analysis, and historical returns.',
    gradient: 'from-orange-500 to-red-500',
  },
  {
    icon: Shield,
    title: 'Risk Management',
    description: 'Learn proper position sizing, portfolio diversification, and risk-reward ratio optimization.',
    gradient: 'from-cyan-500 to-blue-500',
  },
  {
    icon: Users,
    title: 'Community & Support',
    description: 'Join a community of like-minded traders. Get mentorship from experienced professionals.',
    gradient: 'from-rose-500 to-purple-500',
  },
]

const plans = [
  {
    name: 'Free',
    price: '$0',
    description: 'Get started with basic market insights',
    features: [
      'Basic market overview',
      '3 free lessons/month',
      'Community access',
      'Limited signals (daily)',
      'Email support',
    ],
    cta: 'Get Started Free',
    href: '/auth/register',
    highlighted: false,
  },
  {
    name: 'Pro Monthly',
    price: '$49',
    period: '/month',
    description: 'Everything you need to trade confidently',
    features: [
      'All stock signals (real-time)',
      'Unlimited educational content',
      'Simulated trading ($100K)',
      'Advanced analytics dashboard',
      'Priority support',
      'Weekly webinars',
      'Risk management tools',
    ],
    cta: 'Start Pro Trial',
    href: '/auth/register',
    highlighted: true,
    popular: true,
  },
  {
    name: 'Pro Yearly',
    price: '$399',
    period: '/year',
    description: 'Best value — save 32% annually',
    features: [
      'Everything in Pro Monthly',
      '2 months free',
      'Exclusive strategy calls',
      'Early access to new features',
      'Custom alerts & watchlists',
      'API access',
    ],
    cta: 'Get Yearly Plan',
    href: '/auth/register',
    highlighted: false,
  },
]

const testimonials = [
  {
    name: 'Sarah K.',
    role: 'Day Trader',
    content: 'plentyofmoney.online completely transformed my trading. The signals are incredibly accurate and the educational content helped me understand the "why" behind each trade.',
    rating: 5,
  },
  {
    name: 'Marcus J.',
    role: 'Long-term Investor',
    content: 'I was a complete beginner. The structured learning path took me from knowing nothing to confidently managing my own portfolio in 3 months.',
    rating: 5,
  },
  {
    name: 'Elena R.',
    role: 'Swing Trader',
    content: 'The simulated trading feature is a game-changer. I tested dozens of strategies before going live and saved thousands in potential losses.',
    rating: 5,
  },
]

export default function HomePage() {
  return (
    <div className="overflow-hidden">
      {/* Hero Section */}
      <section className="relative min-h-[90vh] flex items-center">
        {/* Background effects */}
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.15),transparent)]" />
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_30%_at_80%_80%,rgba(6,182,212,0.1),transparent)]" />
        
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
          <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 lg:gap-8 items-stretch">
            {/* Logo Column */}
            <div className="flex items-center justify-center p-4">
              <Image
                src="/logo.png"
                alt="plentyofmoney.online"
                width={320}
                height={407}
                className="rounded-2xl w-full h-auto max-h-[400px] object-contain"
                priority
              />
            </div>

            {/* Hero Text Column */}
            <div className="flex flex-col justify-center">
              <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/30 text-sm text-primary-400 mb-6 w-fit">
                <Zap className="w-4 h-4" />
                Trusted by 12,400+ traders worldwide
              </div>
              <h1 className="text-2xl sm:text-3xl lg:text-4xl font-bold tracking-tight mb-5">
                Master the Stock Market
                <span className="block mt-2 bg-gradient-to-r from-primary-400 via-accent-500 to-primary-400 bg-clip-text text-transparent whitespace-nowrap">
                  with Proven Strategies, Trading Methods
                </span>
                <span className="block mt-1 bg-gradient-to-r from-primary-400 via-accent-500 to-primary-400 bg-clip-text text-transparent">
                  with well researched AI-Powered Signals
                </span>
              </h1>
              <p className="text-base sm:text-lg text-gray-400 mb-8">
                Get professional-grade stock signals, comprehensive educational content, and a risk-free 
                simulated trading environment — all in one platform.
              </p>
              <div className="flex flex-col sm:flex-row gap-3">
                <Link
                  href="/auth/register"
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold gradient-primary text-white rounded-xl hover:scale-105 transition-all duration-200 shadow-lg shadow-primary-500/25"
                >
                  Start Your Journey
                  <ArrowRight className="w-4 h-4" />
                </Link>
                <Link
                  href="/learn"
                  className="inline-flex items-center justify-center gap-2 px-6 py-3 text-sm font-semibold text-gray-300 border border-gray-700 rounded-xl hover:bg-gray-800 hover:text-white transition-all duration-200"
                >
                  Explore Free Content
                </Link>
              </div>
            </div>

            {/* Market Chart Column */}
            <div className="hidden lg:flex flex-col h-full">
              <MarketChart />
            </div>
          </div>

          {/* Stats */}
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mt-20">
            {stats.map((stat) => (
              <div key={stat.label} className="text-center p-4 rounded-xl bg-white/5 border border-gray-800/50">
                <div className="text-2xl sm:text-3xl font-bold text-white mb-1">{stat.value}</div>
                <div className="text-sm text-gray-500">{stat.label}</div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="relative py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Everything You Need to Succeed
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              A comprehensive platform designed to take you from beginner to confident trader.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {features.map((feature) => {
              const Icon = feature.icon
              return (
                <div
                  key={feature.title}
                  className="group p-6 rounded-xl bg-white/[0.02] border border-gray-800/50 hover:border-gray-700/50 transition-all duration-300 hover:-translate-y-1"
                >
                  <div className={`inline-flex p-3 rounded-lg bg-gradient-to-br ${feature.gradient} mb-4`}>
                    <Icon className="w-6 h-6 text-white" />
                  </div>
                  <h3 className="text-lg font-semibold mb-2">{feature.title}</h3>
                  <p className="text-gray-500 text-sm leading-relaxed">{feature.description}</p>
                </div>
              )
            })}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="relative py-24">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              What Our Members Say
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Join thousands of successful traders who transformed their approach with plentyofmoney.online.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            {testimonials.map((t) => (
              <div
                key={t.name}
                className="p-6 rounded-xl bg-white/[0.02] border border-gray-800/50"
              >
                <div className="flex gap-1 mb-4">
                  {Array.from({ length: t.rating }).map((_, i) => (
                    <Star key={i} className="w-4 h-4 fill-yellow-400 text-yellow-400" />
                  ))}
                </div>
                <p className="text-gray-400 text-sm mb-6 leading-relaxed">&ldquo;{t.content}&rdquo;</p>
                <div className="flex items-center gap-3">
                  <div className="w-10 h-10 rounded-full gradient-primary flex items-center justify-center text-sm font-semibold text-white">
                    {t.name.charAt(0)}
                  </div>
                  <div>
                    <div className="text-sm font-medium text-white">{t.name}</div>
                    <div className="text-xs text-gray-500">{t.role}</div>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing Section */}
      <section id="pricing" className="relative py-24">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_50%_50%_at_50%_50%,rgba(99,102,241,0.05),transparent)]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-16">
            <h2 className="text-3xl sm:text-4xl font-bold mb-4">
              Simple, Transparent Pricing
            </h2>
            <p className="text-lg text-gray-400 max-w-2xl mx-auto">
              Start free, upgrade when you&apos;re ready to take your trading to the next level.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {plans.map((plan) => (
              <div
                key={plan.name}
                className={`relative p-8 rounded-2xl border transition-all duration-300 ${
                  plan.highlighted
                    ? 'bg-gradient-to-b from-primary-600/10 to-accent-600/5 border-primary-500/50 scale-105'
                    : 'bg-white/[0.02] border-gray-800/50 hover:border-gray-700/50'
                }`}
              >
                {plan.popular && (
                  <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full gradient-primary text-xs font-semibold text-white shadow-lg">
                    MOST POPULAR
                  </div>
                )}
                <div className="mb-6">
                  <h3 className="text-lg font-semibold mb-1">{plan.name}</h3>
                  <p className="text-sm text-gray-500 mb-4">{plan.description}</p>
                  <div className="flex items-baseline gap-1">
                    <span className="text-4xl font-bold">{plan.price}</span>
                    {plan.period && <span className="text-gray-500">{plan.period}</span>}
                  </div>
                </div>
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature) => (
                    <li key={feature} className="flex items-start gap-3 text-sm text-gray-400">
                      <Check className="w-4 h-4 text-primary-500 mt-0.5 shrink-0" />
                      {feature}
                    </li>
                  ))}
                </ul>
                <Link
                  href={plan.href}
                  className={`block text-center py-3 px-6 rounded-xl font-semibold text-sm transition-all duration-200 ${
                    plan.highlighted
                      ? 'gradient-primary text-white hover:scale-105 shadow-lg shadow-primary-500/25'
                      : 'text-gray-300 border border-gray-700 hover:bg-gray-800 hover:text-white'
                  }`}
                >
                  {plan.cta}
                </Link>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="relative py-24">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <Crown className="w-12 h-12 text-yellow-400 mx-auto mb-6" />
          <h2 className="text-3xl sm:text-4xl font-bold mb-4">
            Ready to Transform Your Trading?
          </h2>
          <p className="text-lg text-gray-400 mb-8 max-w-2xl mx-auto">
            Join 12,400+ traders who are already using plentyofmoney.online to make smarter, 
            more profitable trading decisions.
          </p>
          <Link
            href="/auth/register"
            className="inline-flex items-center gap-2 px-8 py-4 text-base font-semibold gradient-primary text-white rounded-xl hover:scale-105 transition-all duration-200 shadow-xl shadow-primary-500/25"
          >
            Get Started Free
            <ArrowRight className="w-5 h-5" />
          </Link>
        </div>
      </section>
    </div>
  )
}
