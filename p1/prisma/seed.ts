import { PrismaClient } from '@prisma/client'
import bcrypt from 'bcryptjs'

const prisma = new PrismaClient()

async function main() {
  console.log('Seeding database...')

  // Create demo user
  const passwordHash = await bcrypt.hash('demo1234', 12)
  const user = await prisma.user.upsert({
    where: { email: 'demo@plentyofmoney.online' },
    update: {},
    create: {
      name: 'Demo User',
      email: 'demo@plentyofmoney.online',
      passwordHash,
      tier: 'pro',
      tradingAccount: {
        create: {
          balance: 100000,
        },
      },
    },
  })
  console.log(`Created demo user: ${user.email} (password: demo1234)`)

  // Create stock signals
  const signals = [
    {
      symbol: 'AAPL',
      name: 'Apple Inc.',
      action: 'buy',
      entryPrice: 178.50,
      targetPrice: 195.00,
      stopLoss: 168.00,
      confidence: 85,
      timeframe: 'medium_term',
      analysis: 'Apple shows strong bullish momentum with upcoming product launches. The services segment continues to grow, providing a stable revenue stream. Technical indicators show a breakout from a consolidation pattern with increasing volume.',
      riskLevel: 'medium',
      sector: 'Technology',
    },
    {
      symbol: 'NVDA',
      name: 'NVIDIA Corp.',
      action: 'strong_buy',
      entryPrice: 875.30,
      targetPrice: 950.00,
      stopLoss: 830.00,
      confidence: 92,
      timeframe: 'short_term',
      analysis: 'NVIDIA continues to dominate the AI chip market. Recent earnings exceeded expectations by 15%. The upcoming Blackwell architecture launch is expected to drive further growth. Strong technical momentum with bullish flag pattern.',
      riskLevel: 'medium',
      sector: 'Technology',
    },
    {
      symbol: 'TSLA',
      name: 'Tesla Inc.',
      action: 'hold',
      entryPrice: 248.60,
      targetPrice: 280.00,
      stopLoss: 235.00,
      confidence: 60,
      timeframe: 'medium_term',
      analysis: 'Tesla is in a consolidation phase. While the long-term EV story remains intact, near-term headwinds from competition and pricing pressures suggest waiting for a better entry point. Support at $240 level is crucial.',
      riskLevel: 'high',
      sector: 'Consumer',
    },
    {
      symbol: 'MSFT',
      name: 'Microsoft Corp.',
      action: 'buy',
      entryPrice: 378.90,
      targetPrice: 420.00,
      stopLoss: 360.00,
      confidence: 88,
      timeframe: 'long_term',
      analysis: 'Microsoft\'s cloud business (Azure) continues to gain market share. AI integration across products (Copilot) opens new revenue streams. Strong balance sheet with consistent dividend growth. Accumulate on dips.',
      riskLevel: 'low',
      sector: 'Technology',
    },
    {
      symbol: 'AMZN',
      name: 'Amazon.com Inc.',
      action: 'buy',
      entryPrice: 178.25,
      targetPrice: 200.00,
      stopLoss: 168.00,
      confidence: 82,
      timeframe: 'medium_term',
      analysis: 'Amazon Web Services (AWS) growth is accelerating. E-commerce margins are improving due to efficiency initiatives. Advertising business is becoming a significant profit center. Technical setup shows a cup-and-handle pattern.',
      riskLevel: 'medium',
      sector: 'Technology',
    },
    {
      symbol: 'GOOGL',
      name: 'Alphabet Inc.',
      action: 'sell',
      entryPrice: 141.80,
      targetPrice: 130.00,
      stopLoss: 148.00,
      confidence: 70,
      timeframe: 'short_term',
      analysis: 'Alphabet faces increasing competition in AI search from various players. Advertising revenue growth is slowing. Regulatory risks in both US and EU are mounting. Technical indicators show a bearish divergence on RSI.',
      riskLevel: 'medium',
      sector: 'Technology',
    },
    {
      symbol: 'JPM',
      name: 'JPMorgan Chase & Co.',
      action: 'buy',
      entryPrice: 198.40,
      targetPrice: 220.00,
      stopLoss: 188.00,
      confidence: 80,
      timeframe: 'long_term',
      analysis: 'JPMorgan benefits from higher interest rate environment. Strong investment banking pipeline. Consistent dividend payer with solid capital ratios. The banking sector overall shows relative strength.',
      riskLevel: 'low',
      sector: 'Finance',
    },
    {
      symbol: 'META',
      name: 'Meta Platforms Inc.',
      action: 'strong_buy',
      entryPrice: 505.70,
      targetPrice: 560.00,
      stopLoss: 480.00,
      confidence: 90,
      timeframe: 'short_term',
      analysis: 'Meta is executing well on AI integration across platforms. Revenue growth is accelerating, driven by Reels monetization and AI-powered advertising tools. Cost discipline has improved margins significantly. Breakout above resistance.',
      riskLevel: 'medium',
      sector: 'Technology',
    },
    {
      symbol: 'XOM',
      name: 'Exxon Mobil Corp.',
      action: 'hold',
      entryPrice: 118.30,
      targetPrice: 130.00,
      stopLoss: 110.00,
      confidence: 65,
      timeframe: 'medium_term',
      analysis: 'Energy sector remains volatile with oil price fluctuations. XOM offers good dividend yield but limited near-term upside. Better opportunities exist in other sectors currently.',
      riskLevel: 'medium',
      sector: 'Energy',
    },
    {
      symbol: 'UNH',
      name: 'UnitedHealth Group Inc.',
      action: 'buy',
      entryPrice: 525.40,
      targetPrice: 570.00,
      stopLoss: 505.00,
      confidence: 78,
      timeframe: 'long_term',
      analysis: 'Healthcare sector provides defensive exposure. UNH has a diverse business model across insurance, pharmacy benefits, and healthcare services. Aging population provides long-term demand tailwinds.',
      riskLevel: 'low',
      sector: 'Healthcare',
    },
  ]

  for (const signal of signals) {
    await prisma.stockSignal.create({ data: signal })
  }
  console.log(`Created ${signals.length} stock signals`)

  // Create educational lessons
  const lessons = [
    {
      title: 'Understanding the Stock Market',
      description: 'A comprehensive introduction to how stock markets work, including exchanges, order types, and market participants.',
      content: 'The stock market is a marketplace where buyers and sellers trade shares of publicly listed companies...',
      category: 'beginner',
      type: 'article',
      difficulty: 'beginner',
      premium: false,
      order: 1,
      duration: '15 min',
      author: 'Sarah Mitchell',
    },
    {
      title: 'Technical Analysis Fundamentals',
      description: 'Learn the basics of technical analysis including support/resistance, trends, and chart patterns.',
      content: 'Technical analysis is the study of market action through the use of charts...',
      category: 'beginner',
      type: 'course',
      difficulty: 'beginner',
      premium: false,
      order: 2,
      duration: '45 min',
      author: 'Marcus Chen',
    },
    {
      title: 'Reading Candlestick Charts',
      description: 'Master the art of reading candlestick patterns to identify market sentiment and potential reversals.',
      content: 'Candlestick charts originated in Japan over 100 years ago...',
      category: 'beginner',
      type: 'video',
      difficulty: 'beginner',
      premium: false,
      order: 3,
      duration: '20 min',
      author: 'Emily Roberts',
    },
    {
      title: 'Introduction to Fundamental Analysis',
      description: 'Understand how to evaluate a company\'s financial health through earnings, revenue, and key ratios.',
      content: 'Fundamental analysis involves evaluating a company\'s financial statements...',
      category: 'beginner',
      type: 'article',
      difficulty: 'beginner',
      premium: false,
      order: 4,
      duration: '25 min',
      author: 'David Park',
    },
    {
      title: 'Building a Diversified Portfolio',
      description: 'Learn the principles of portfolio diversification and asset allocation for long-term success.',
      content: 'Diversification is one of the most important concepts in investing...',
      category: 'intermediate',
      type: 'article',
      difficulty: 'intermediate',
      premium: false,
      order: 5,
      duration: '20 min',
      author: 'Sarah Mitchell',
    },
    {
      title: 'Advanced Candlestick Patterns',
      description: 'Deep dive into complex candlestick patterns including engulfing, doji, harami, and morning/evening stars.',
      content: 'Building on basic candlestick knowledge, advanced patterns provide...',
      category: 'intermediate',
      type: 'video',
      difficulty: 'intermediate',
      premium: true,
      order: 6,
      duration: '35 min',
      author: 'Emily Roberts',
    },
    {
      title: 'Risk Management Strategies',
      description: 'Master position sizing, stop-losses, and risk-reward ratios to protect your capital.',
      content: 'Professional traders know that risk management is more important than...',
      category: 'intermediate',
      type: 'course',
      difficulty: 'intermediate',
      premium: false,
      order: 7,
      duration: '40 min',
      author: 'Marcus Chen',
    },
    {
      title: 'Moving Averages & Trend Indicators',
      description: 'Learn to use moving averages, MACD, and RSI to identify trends and generate trading signals.',
      content: 'Moving averages smooth out price data to help identify trends...',
      category: 'intermediate',
      type: 'article',
      difficulty: 'intermediate',
      premium: true,
      order: 8,
      duration: '30 min',
      author: 'David Park',
    },
    {
      title: 'Options Trading: A Complete Guide',
      description: 'From calls and puts to complex strategies — everything you need to know about options trading.',
      content: 'Options are derivative contracts that give the buyer the right...',
      category: 'advanced',
      type: 'course',
      difficulty: 'advanced',
      premium: true,
      order: 9,
      duration: '60 min',
      author: 'Marcus Chen',
    },
    {
      title: 'Algorithmic Trading with Python',
      description: 'Build your own trading algorithms using Python. Covers backtesting, APIs, and execution.',
      content: 'Algorithmic trading uses computer programs to execute trades...',
      category: 'advanced',
      type: 'course',
      difficulty: 'advanced',
      premium: true,
      order: 10,
      duration: '90 min',
      author: 'Alex Kim',
    },
    {
      title: 'Swing Trading Strategies',
      description: 'Proven swing trading strategies that capture medium-term price movements with defined risk parameters.',
      content: 'Swing trading involves holding positions for several days to weeks...',
      category: 'strategy',
      type: 'article',
      difficulty: 'intermediate',
      premium: true,
      order: 11,
      duration: '25 min',
      author: 'Sarah Mitchell',
    },
    {
      title: 'Earnings Season Playbook',
      description: 'How to trade earnings announcements effectively. Pre-earnings analysis and post-earnings strategies.',
      content: 'Earnings season can be one of the most profitable times...',
      category: 'strategy',
      type: 'video',
      difficulty: 'intermediate',
      premium: true,
      order: 12,
      duration: '30 min',
      author: 'David Park',
    },
    {
      title: 'Market Sentiment Analysis',
      description: 'Learn to gauge market sentiment using put/call ratios, VIX, and other sentiment indicators.',
      content: 'Market sentiment refers to the overall attitude of investors...',
      category: 'analysis',
      type: 'article',
      difficulty: 'advanced',
      premium: true,
      order: 13,
      duration: '20 min',
      author: 'Emily Roberts',
    },
    {
      title: 'Volume Profile & Order Flow',
      description: 'Advanced analysis of volume distribution and order flow to identify smart money positioning.',
      content: 'Volume Profile shows trading activity at specific price levels...',
      category: 'analysis',
      type: 'video',
      difficulty: 'advanced',
      premium: true,
      order: 14,
      duration: '45 min',
      author: 'Alex Kim',
    },
    {
      title: 'Trading Psychology & Discipline',
      description: 'Master the mental aspects of trading including fear, greed, discipline, and emotional control.',
      content: 'Your mindset is your most important trading tool...',
      category: 'beginner',
      type: 'article',
      difficulty: 'beginner',
      premium: false,
      order: 0,
      duration: '15 min',
      author: 'Sarah Mitchell',
    },
  ]

  for (const lesson of lessons) {
    await prisma.lesson.create({ data: lesson })
  }
  console.log(`Created ${lessons.length} lessons`)

  console.log('Database seeded successfully!')
  console.log('\nDemo account:')
  console.log('  Email: demo@plentyofmoney.online')
  console.log('  Password: demo1234')
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
  .finally(async () => {
    await prisma.$disconnect()
  })
