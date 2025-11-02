// File: src/frontend/app/paths/[id]/page.tsx
export default function PathDetailsPage({ params }: { params: { id: string } }) {
  return <h1>تفاصيل المسار رقم: {params.id}</h1>;
}