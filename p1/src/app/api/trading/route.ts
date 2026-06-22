import { NextResponse } from 'next/server'
import { getServerSession } from 'next-auth'
import { authOptions } from '@/lib/auth'
import { prisma } from '@/lib/prisma'

export async function GET() {
  const session = await getServerSession(authOptions)
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const userId = (session.user as any).id

  try {
    const account = await prisma.tradingAccount.findUnique({
      where: { userId },
      include: {
        positions: true,
      },
    })

    if (!account) {
      return NextResponse.json({ error: 'Trading account not found' }, { status: 404 })
    }

    // Calculate portfolio value
    let totalValue = account.balance
    const positions = account.positions.map((pos) => ({
      ...pos,
      currentPrice: pos.avgPrice * (1 + (Math.random() - 0.5) * 0.1), // Simulated current price
    }))

    for (const pos of positions) {
      totalValue += pos.shares * pos.currentPrice
    }

    const totalReturn = ((totalValue - 100000) / 100000) * 100

    return NextResponse.json({
      account,
      positions,
      totalValue,
      totalReturn,
    })
  } catch (error) {
    console.error('Trading fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch trading data' },
      { status: 500 }
    )
  }
}

export async function POST(request: Request) {
  const session = await getServerSession(authOptions)
  if (!session?.user) {
    return NextResponse.json({ error: 'Unauthorized' }, { status: 401 })
  }

  const userId = (session.user as any).id
  const { symbol, action, shares, price } = await request.json()

  if (!symbol || !action || !shares || !price) {
    return NextResponse.json(
      { error: 'Missing required fields: symbol, action, shares, price' },
      { status: 400 }
    )
  }

  try {
    const account = await prisma.tradingAccount.findUnique({
      where: { userId },
      include: { positions: true },
    })

    if (!account) {
      return NextResponse.json({ error: 'Trading account not found' }, { status: 404 })
    }

    const total = shares * price

    if (action === 'buy') {
      const cost = total
      if (account.balance < cost) {
        return NextResponse.json(
          { error: 'Insufficient funds' },
          { status: 400 }
        )
      }

      // Update or create position
      const existingPosition = account.positions.find((p) => p.symbol === symbol)
      
      if (existingPosition) {
        const newShares = existingPosition.shares + shares
        const newAvgPrice = ((existingPosition.avgPrice * existingPosition.shares) + total) / newShares
        
        await prisma.portfolioPosition.update({
          where: { id: existingPosition.id },
          data: { shares: newShares, avgPrice: newAvgPrice },
        })
      } else {
        await prisma.portfolioPosition.create({
          data: {
            accountId: account.id,
            symbol,
            shares,
            avgPrice: price,
          },
        })
      }

      await prisma.tradingAccount.update({
        where: { id: account.id },
        data: { balance: account.balance - cost },
      })
    } else if (action === 'sell') {
      const position = account.positions.find((p) => p.symbol === symbol)
      if (!position || position.shares < shares) {
        return NextResponse.json(
          { error: 'Not enough shares to sell' },
          { status: 400 }
        )
      }

      const remaining = position.shares - shares
      if (remaining <= 0) {
        await prisma.portfolioPosition.delete({
          where: { id: position.id },
        })
      } else {
        await prisma.portfolioPosition.update({
          where: { id: position.id },
          data: { shares: remaining },
        })
      }

      const proceeds = total
      await prisma.tradingAccount.update({
        where: { id: account.id },
        data: { balance: account.balance + proceeds },
      })
    }

    // Record transaction
    await prisma.transaction.create({
      data: {
        userId,
        accountId: account.id,
        type: action,
        symbol,
        shares,
        price,
        total,
      },
    })

    return NextResponse.json({ success: true })
  } catch (error) {
    console.error('Trade execution error:', error)
    return NextResponse.json(
      { error: 'Failed to execute trade' },
      { status: 500 }
    )
  }
}
