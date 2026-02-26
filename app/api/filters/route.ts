import { NextRequest, NextResponse } from 'next/server';
import { getSavedFilters, saveFilterToFile, deleteFilterFile, getFilterById, SavedFilter } from '@/lib/db';

// GET all filters or single filter by id
export async function GET(request: NextRequest) {
  try {
    const id = new URL(request.url).searchParams.get('id');

    if (id === 'export-all') {
      // Export ALL filters as a single JSON array for download
      const filters = getSavedFilters();
      return new NextResponse(JSON.stringify(filters, null, 2), {
        headers: {
          'Content-Type': 'application/json',
          'Content-Disposition': 'attachment; filename="filtros_exportados.json"',
        },
      });
    }

    if (id) {
      const filter = getFilterById(id);
      if (!filter) return NextResponse.json({ error: 'Filtro não encontrado' }, { status: 404 });
      // Export single filter as JSON download
      return new NextResponse(JSON.stringify(filter, null, 2), {
        headers: {
          'Content-Type': 'application/json',
          'Content-Disposition': `attachment; filename="filtro_${filter.name.replace(/\s+/g, '_')}.json"`,
        },
      });
    }

    const filters = getSavedFilters();
    return NextResponse.json({ filters });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// POST: save a filter OR import filters from JSON
export async function POST(request: NextRequest) {
  try {
    const contentType = request.headers.get('content-type') || '';

    // Handle JSON filter import via multipart
    if (contentType.includes('multipart/form-data')) {
      const formData = await request.formData();
      const file = formData.get('file') as File;
      if (!file) return NextResponse.json({ error: 'Nenhum arquivo' }, { status: 400 });

      const text = await file.text();
      const parsed = JSON.parse(text);

      // Can be array of filters or single filter
      const filtersToImport: SavedFilter[] = Array.isArray(parsed) ? parsed : [parsed];
      let imported = 0;

      for (const f of filtersToImport) {
        if (f.selectedColumns && f.conditions) {
          // Generate new ID to avoid conflicts
          const filter: SavedFilter = {
            id: `imported_${Date.now()}_${imported}`,
            name: f.name || `Filtro importado ${imported + 1}`,
            description: f.description,
            selectedColumns: f.selectedColumns,
            conditions: f.conditions,
            createdAt: f.createdAt || new Date().toISOString(),
          };
          saveFilterToFile(filter);
          imported++;
        }
      }

      return NextResponse.json({ success: true, imported });
    }

    // Regular save
    const filter: SavedFilter = await request.json();
    if (!filter.id) filter.id = Date.now().toString();
    if (!filter.createdAt) filter.createdAt = new Date().toISOString();
    saveFilterToFile(filter);
    return NextResponse.json({ success: true, filter });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}

// DELETE a filter
export async function DELETE(request: NextRequest) {
  try {
    const { id } = await request.json();
    deleteFilterFile(id);
    return NextResponse.json({ success: true });
  } catch (error: any) {
    return NextResponse.json({ error: error.message }, { status: 500 });
  }
}
