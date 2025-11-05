// المسار: src/frontend/src/app/components/PathCard.tsx
import Link from 'next/link';

type PathCardProps = {
  id: number;
  title: string;
  totalHours: number;
};

export default function PathCard({ id, title, totalHours }: PathCardProps) {
  return (
    <Link href={`/paths/${id}`} className="block">
        <div className="bg-card p-6 rounded-lg border shadow hover:shadow-lg transition-shadow h-full">
            <h3 className="text-xl font-bold text-primary">{title}</h3>
            <p className="text-muted-foreground mt-2">{totalHours} ساعة لإكماله</p>
        </div>
    </Link>
  );
}