// المسار: src/frontend/src/components/StepItem.tsx

type StepItemProps = {
  title: string;
  description: string;
  resourceUrl: string;
};

export default function StepItem({ title, description, resourceUrl }: StepItemProps) {
  return (
    <div className="bg-white p-5 rounded-lg shadow border transition-transform hover:scale-[1.02]">
      <div className="flex justify-between items-start">
        <div>
          <h4 className="text-lg font-semibold text-gray-800">{title}</h4>
          <p className="text-gray-600 mt-1">{description}</p>
          <a
            href={resourceUrl}
            target="_blank"
            rel="noopener noreferrer"
            className="text-blue-600 hover:underline mt-3 inline-block font-medium"
          >
            اذهب إلى المورد &larr;
          </a>
        </div>
        <button className="bg-gray-200 text-gray-800 font-semibold py-1 px-3 rounded-full hover:bg-green-200 hover:text-green-800 transition-colors">
          تم
        </button>
      </div>
    </div>
  );
}