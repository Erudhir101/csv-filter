import { NextRequest, NextResponse } from 'next/server';
import { parse } from 'csv-parse/sync';
import { importCSV } from '@/lib/db';

export async function POST(request: NextRequest) {
  try {
    const formData = await request.formData();
    const file = formData.get('file') as File;
    if (!file) return NextResponse.json({ error: 'Nenhum arquivo' }, { status: 400 });

    const text = await file.text();
    const firstLine = text.split('\n')[0];
    const delimiter = firstLine.split('\t').length > 3 ? '\t'
      : firstLine.split(';').length > 3 ? ';' : ',';

    const records = parse(text, {
      delimiter,
      skip_empty_lines: true,
      relax_column_count: true,
      trim: true,
    });

    if (records.length < 2) {
      return NextResponse.json({ error: 'CSV precisa ter cabeçalho + dados' }, { status: 400 });
    }

    const result = importCSV(records[0], records.slice(1));
    return NextResponse.json({ success: true, ...result });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
