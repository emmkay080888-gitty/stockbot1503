import { NextResponse } from 'next/server'
import { prisma } from '@/lib/prisma'

export async function GET(request: Request) {
  const { searchParams } = new URL(request.url)
  const category = searchParams.get('category')
  const difficulty = searchParams.get('difficulty')
  const type = searchParams.get('type')
  const limit = parseInt(searchParams.get('limit') || '50')

  try {
    const where: any = {}

    if (category) where.category = category
    if (difficulty) where.difficulty = difficulty
    if (type) where.type = type

    const lessons = await prisma.lesson.findMany({
      where,
      orderBy: { order: 'asc' },
      take: limit,
    })

    return NextResponse.json(lessons)
  } catch (error) {
    console.error('Lessons fetch error:', error)
    return NextResponse.json(
      { error: 'Failed to fetch lessons' },
      { status: 500 }
    )
  }
}
