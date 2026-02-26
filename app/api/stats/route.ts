import { NextResponse } from 'next/server';
import { getTableStats, COLUMNS } from '@/lib/db';

export async function GET() {
  try {
    const stats = getTableStats();
    return NextResponse.json({ ...stats, columns: COLUMNS });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
