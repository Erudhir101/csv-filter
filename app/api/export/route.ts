import { NextRequest, NextResponse } from 'next/server';
import { exportFilteredCSV } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const { selectedColumns = [], conditions = [] } = await request.json();
    const csv = exportFilteredCSV(selectedColumns, conditions);
    return new NextResponse(csv, {
      headers: {
        'Content-Type': 'text/csv; charset=utf-8',
        'Content-Disposition': 'attachment; filename="dados_filtrados.csv"',
      },
    });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
