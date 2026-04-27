type StatusCardProps = {
  title: string;
  value: string;
  description?: string;
};

export default function StatusCard({ title, value, description }: StatusCardProps) {
  return (
    <div className="rounded-xl border border-gray-200 bg-white p-4 shadow-sm">
      <p className="text-sm text-gray-500">{title}</p>
      <p className="mt-2 text-2xl font-bold text-gray-900">{value}</p>
      {description ? <p className="mt-2 text-sm text-gray-600">{description}</p> : null}
    </div>
  );
}