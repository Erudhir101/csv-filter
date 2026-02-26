import { NextRequest, NextResponse } from 'next/server';
import { getDistinctValues } from '@/lib/db';

export async function GET(request: NextRequest) {
  try {
    const col = new URL(request.url).searchParams.get('column');
    if (!col) return NextResponse.json({ error: 'column required' }, { status: 400 });
    const values = getDistinctValues(col);
    return NextResponse.json({ values });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
