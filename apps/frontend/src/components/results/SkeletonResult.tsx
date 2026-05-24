export function SkeletonResult() {
  return (
    <div className="card space-y-4 animate-in">
      <div className="skeleton h-4 w-24 rounded" />
      <div className="skeleton h-6 w-48 rounded" />
      <div className="divider" />
      <div className="flex items-center gap-4">
        <div className="skeleton h-8 w-36 rounded" />
        <div className="skeleton h-10 w-12 rounded" />
      </div>
      <div className="skeleton h-24 w-full rounded-xl" />
      <div className="space-y-2">
        <div className="skeleton h-3 w-full rounded" />
        <div className="skeleton h-3 w-3/4 rounded" />
      </div>
    </div>
  );
}

export function SkeletonRecommendations() {
  return (
    <div className="card space-y-4 animate-in">
      <div className="skeleton h-4 w-24 rounded" />
      <div className="skeleton h-6 w-48 rounded" />
      <div className="divider" />
      {Array.from({ length: 5 }).map((_, i) => (
        <div key={i} className="card-sm space-y-2">
          <div className="flex gap-3">
            <div className="skeleton h-7 w-7 flex-shrink-0 rounded-lg" />
            <div className="flex-1 space-y-1">
              <div className="skeleton h-4 w-3/4 rounded" />
              <div className="skeleton h-3 w-1/3 rounded" />
            </div>
            <div className="skeleton h-8 w-10 rounded" />
          </div>
          <div className="skeleton h-1.5 w-full rounded-full" />
          <div className="skeleton h-3 w-full rounded" />
        </div>
      ))}
    </div>
  );
}
