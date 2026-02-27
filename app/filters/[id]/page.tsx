import { getFilterById } from '@/lib/db';
import { notFound } from 'next/navigation';
import FilterPageClient from './FilterPageClient';
import type { SavedFilter } from '@/lib/types';

interface Props {
  params: { id: string };
}

export default function FilterPage({ params }: Props) {
  const filter = getFilterById(params.id);
  if (!filter) notFound();
  return <FilterPageClient initialFilter={filter as unknown as SavedFilter} />;
}
