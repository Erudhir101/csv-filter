import { NextRequest, NextResponse } from 'next/server';
import { queryFiltered } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const result = queryFiltered(
      body.selectedColumns || [],
      body.conditions || [],
      body.page || 1,
      body.pageSize || 50,
      body.sortColumn,
      body.sortDir || 'asc'
    );
    return NextResponse.json(result);
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
