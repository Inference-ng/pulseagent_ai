interface StarRatingProps {
  rating: number;
}

export function StarRating({ rating }: StarRatingProps) {
  const width = `${Math.max(0, Math.min(100, (rating / 5) * 100))}%`;

  return (
    <div className="relative inline-block text-3xl leading-none tracking-[0.28em]">
      <div className="text-white/10">★★★★★</div>
      <div className="absolute inset-0 overflow-hidden text-amber transition-all duration-700" style={{ width }}>
        ★★★★★
      </div>
    </div>
  );
}