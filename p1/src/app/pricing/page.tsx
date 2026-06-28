'use client'

import { useState } from 'react'
import { useSession } from 'next-auth/react'
import Link from 'next/link'
import { Check, Crown, TrendingUp, BookOpen, DollarSign, BarChart3, Users, Zap, Shield, ArrowRight, Star } from 'lucide-react'

const plans = [
  {
    name: 'Free',
    price: '$0',
    description: 'Get started with basic market insights',
    features: [
      { included: true, text: 'Basic market overview dashboard' },
      { included: true, text: '3 free educational lessons/month' },
      { included: true, text: 'Community forum access' },
      { included: true, text: 'Daily market summary' },
      { included: false, text: 'Real-time stock signals' },
      { included: false, text: 'Simulated trading platform' },
      { included: false, text: 'Advanced analytics' },
      { included: false, text: 'Priority support' },
      { included: false, text: 'Weekly webinars' },
      { included: false, text: 'API access' },
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
      { included: true, text: 'Everything in Free, plus:' },
      { included: true, text: 'Real-time stock signals' },
      { included: true, text: 'Unlimited educational content' },
      { included: true, text: 'Simulated trading ($100K virtual)' },
      { included: true, text: 'Advanced portfolio analytics' },
      { included: true, text: 'Risk management tools' },
      { included: true, text: 'Priority email support' },
      { included: true, text: 'Weekly trading webinars' },
      { included: true, text: 'Custom alerts & watchlists' },
      { included: false, text: 'API access' },
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
    description: 'Best value — save 32% compared to monthly',
    features: [
      { included: true, text: 'Everything in Pro Monthly' },
      { included: true, text: '2 months free ($98 savings)' },
      { included: true, text: 'Exclusive strategy calls' },
      { included: true, text: 'Early access to new features' },
      { included: true, text: 'Custom alerts & watchlists' },
      { included: true, text: 'API access for automated trading' },
      { included: true, text: 'Personal trading mentor' },
      { included: true, text: 'Advanced risk analytics' },
      { included: true, text: 'Portfolio rebalancing' },
      { included: true, text: 'Tax optimization reports' },
    ],
    cta: 'Get Yearly Plan',
    href: '/auth/register',
    highlighted: false,
  },
]

const comparisonFeatures = [
  { name: 'Market Dashboard', free: true, pro: true },
  { name: 'Educational Content', free: '3/mo', pro: 'Unlimited' },
  { name: 'Real-time Signals', free: false, pro: true },
  { name: 'Simulated Trading', free: false, pro: '$100K' },
  { name: 'Advanced Analytics', free: false, pro: true },
  { name: 'Risk Management', free: false, pro: true },
  { name: 'Weekly Webinars', free: false, pro: true },
  { name: 'Community Access', free: true, pro: true },
  { name: 'Priority Support', free: false, pro: true },
  { name: 'API Access', free: false, pro: 'Yearly only' },
]

export default function PricingPage() {
  const { data: session } = useSession()

  return (
    <div className="min-h-[calc(100vh-4rem)]">
      {/* Header */}
      <section className="relative py-20">
        <div className="absolute inset-0 bg-[radial-gradient(ellipse_80%_50%_at_50%_-20%,rgba(99,102,241,0.15),transparent)]" />
        <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-primary-500/10 border border-primary-500/30 text-sm text-primary-400 mb-6">
            <Crown className="w-4 h-4" />
            Choose Your Plan
          </div>
          <h1 className="text-4xl sm:text-5xl font-bold mb-4">
            Invest in Your Trading Future
          </h1>
          <p className="text-lg text-gray-400 max-w-2xl mx-auto">
            Start free and upgrade when you&apos;re ready. All plans include a 14-day money-back guarantee.
          </p>
        </div>
      </section>

      {/* Pricing Cards */}
      <section className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 max-w-5xl mx-auto">
          {plans.map((plan) => (
            <div
              key={plan.name}
              className={`relative p-8 rounded-2xl border transition-all duration-300 ${
                plan.highlighted
                  ? 'bg-gradient-to-b from-primary-600/10 to-accent-600/5 border-primary-500/50 scale-105 shadow-2xl shadow-primary-500/10'
                  : 'bg-white/[0.02] border-gray-800/50 hover:border-gray-700/50'
              }`}
            >
              {plan.popular && (
                <div className="absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full gradient-primary text-xs font-semibold text-white shadow-lg flex items-center gap-1">
                  <Star className="w-3 h-3" />
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
                {plan.features.map((feature, i) => (
                  <li key={i} className={`flex items-start gap-3 text-sm ${feature.included ? 'text-gray-400' : (i === 0 ? 'text-gray-400 font-semibold' : 'text-gray-600 line-through')}`}>
                    <Check className={`w-4 h-4 mt-0.5 shrink-0 ${feature.included ? 'text-primary-500' : 'text-gray-700'}`} />
                    {feature.text}
                  </li>
                ))}
              </ul>

              <Link
                href={session ? '/dashboard' : plan.href}
                className={`block text-center py-3 px-6 rounded-xl font-semibold text-sm transition-all duration-200 ${
                  plan.highlighted
                    ? 'gradient-primary text-white hover:scale-105 shadow-lg shadow-primary-500/25'
                    : 'text-gray-300 border border-gray-700 hover:bg-gray-800 hover:text-white'
                }`}
              >
                {session ? 'Go to Dashboard' : plan.cta}
              </Link>
            </div>
          ))}
        </div>
      </section>

      {/* Feature Comparison Table */}
      <section className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <h2 className="text-2xl font-bold text-center mb-8">Feature Comparison</h2>
        <div className="rounded-xl border border-gray-800/50 overflow-hidden">
          <table className="w-full">
            <thead>
              <tr className="border-b border-gray-800/50">
                <th className="text-left p-4 text-sm font-semibold text-gray-400">Feature</th>
                <th className="text-center p-4 text-sm font-semibold text-gray-400">Free</th>
                <th className="text-center p-4 text-sm font-semibold text-primary-400">Pro</th>
              </tr>
            </thead>
            <tbody>
              {comparisonFeatures.map((feat, i) => (
                <tr key={feat.name} className={`border-b border-gray-800/30 ${i % 2 === 0 ? 'bg-white/[0.01]' : ''}`}>
                  <td className="p-4 text-sm text-gray-300">{feat.name}</td>
                  <td className="p-4 text-center">
                    {feat.free === true ? (
                      <Check className="w-4 h-4 text-green-400 mx-auto" />
                    ) : feat.free === false ? (
                      <span className="text-gray-600">—</span>
                    ) : (
                      <span className="text-sm text-gray-500">{feat.free}</span>
                    )}
                  </td>
                  <td className="p-4 text-center">
                    {feat.pro === true ? (
                      <Check className="w-4 h-4 text-primary-400 mx-auto" />
                    ) : (
                      <span className="text-sm text-primary-400">{feat.pro}</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>

      {/* FAQ */}
      <section className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8 pb-20">
        <h2 className="text-2xl font-bold text-center mb-8">Frequently Asked Questions</h2>
        <div className="space-y-4">
          {[
            {
              q: 'Can I switch plans at any time?',
              a: 'Yes, you can upgrade or downgrade your plan at any time. Upgrades take effect immediately, while downgrades apply at the start of the next billing cycle.',
            },
            {
              q: 'Is there a money-back guarantee?',
              a: 'Absolutely! We offer a 14-day money-back guarantee on all Pro plans. If you\'re not satisfied, we\'ll refund your payment — no questions asked.',
            },
            {
              q: 'What payment methods do you accept?',
              a: 'We accept all major credit cards (Visa, Mastercard, American Express) and PayPal. Enterprise customers can also pay via invoice.',
            },
            {
              q: 'Can I use the simulated trading with the free plan?',
              a: 'The simulated trading platform is a Pro feature. However, you can access our educational content and basic market overview on the free plan to get started.',
            },
            {
              q: 'How accurate are the trading signals?',
              a: 'Our signals have historically achieved an 87.3% accuracy rate. However, past performance does not guarantee future results, and all trading involves risk.',
            },
          ].map((faq) => (
            <details key={faq.q} className="group p-4 rounded-xl bg-white/[0.02] border border-gray-800/50 [&_summary::-webkit-details-marker]:hidden">
              <summary className="flex items-center justify-between cursor-pointer">
                <span className="text-sm font-medium text-gray-300 group-hover:text-white transition-colors">{faq.q}</span>
                <ChevronRightIcon className="w-4 h-4 text-gray-500 group-open:rotate-90 transition-transform" />
              </summary>
              <p className="mt-3 text-sm text-gray-500 leading-relaxed">{faq.a}</p>
            </details>
          ))}
        </div>
      </section>

      {/* CTA */}
      <section className="text-center pb-20 px-4">
        <div className="max-w-xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Still Have Questions?</h2>
          <p className="text-gray-500 mb-6">
            Our team is here to help you choose the right plan for your trading journey.
          </p>
          <Link
            href={session ? '/dashboard' : '/auth/register'}
            className="inline-flex items-center gap-2 px-6 py-3 gradient-primary text-white rounded-xl font-semibold hover:scale-105 transition-all shadow-lg shadow-primary-500/25"
          >
            Get Started Free
            <ArrowRight className="w-4 h-4" />
          </Link>
        </div>
      </section>
    </div>
  )
}

function ChevronRightIcon({ className }: { className?: string }) {
  return (
    <svg className={className} fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={2}>
      <path strokeLinecap="round" strokeLinejoin="round" d="M9 5l7 7-7 7" />
    </svg>
  )
}
