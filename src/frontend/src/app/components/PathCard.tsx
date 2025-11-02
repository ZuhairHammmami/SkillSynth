// app/components/PathCard.tsx
type PathCardProps = {
  title: string;
  totalHours: number;
};

export default function PathCard({ title, totalHours }: PathCardProps) {
  return (
    <div className="bg-white p-6 rounded-lg shadow-md border flex justify-between items-center">
      <div>
        <h3 className="text-xl font-bold">{title}</h3>
        <p className="text-gray-500">{totalHours} ساعة لإكماله</p>
      </div>
      <button className="bg-green-500 text-white font-semibold py-2 px-4 rounded-lg hover:bg-green-600">
        حفظ
      </button>
    </div>
  );
}