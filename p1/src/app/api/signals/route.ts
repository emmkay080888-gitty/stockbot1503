import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function GET(request: Request) {
  const session = await getServerSession(authOptions)
  if (!session?.user) {
    return NextResponse.json(
      { error: 'Authentication required' },
      { status: 401 }
    )
  }

  // Free tier users get limited signals data
  const tier = (session.user as any).tier || 'free'
  const isPro = tier === 'pro'
  const { searchParams } = new URL(request.url)
  const action = searchParams.get('action')
  const sector = searchParams.get('sector')
  const active = searchParams.get('active') !== 'false'

  try {
    const where: any = { isActive: active }

    if (action) where.action = action
    if (sector) where.sector = sector

    const signals = await prisma.stockSignal.findMany({
      where,
      orderBy: { createdAt: 'desc' },
      take: isPro ? 50 : 3,
      select: isPro ? undefined : {
        id: true,
        symbol: true,
        name: true,
        action: true,
        createdAt: true,
        sector: true,
        timeframe: true,
      },
    })

    return NextResponse.json(signals)
  } catch (error) {
    console.error('Signals fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch signals' },
      { status: 500 }
    )
  }
}
