interface DashboardHeaderProps {
  title: string;
  description?: string;
}

export default function DashboardHeader({ title, description }: DashboardHeaderProps) {

  return (
    <div className="mb-6">
      <nav className="text-sm mb-2">
      </nav>
      <h1 className="text-2xl font-bold text-[#333333] mb-2">{title}</h1>
      {description && (
        <p className="text-[#888888]">{description}</p>
      )}
    </div>
  );
}
