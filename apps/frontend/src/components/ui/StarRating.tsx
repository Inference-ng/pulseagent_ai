interface StarRatingProps { rating: number; size?: 'sm' | 'md' | 'lg'; }

export function StarRating({ rating, size = 'md' }: StarRatingProps) {
  const sizeClass = { sm: 'text-lg', md: 'text-2xl', lg: 'text-3xl' }[size];
  const width = `${Math.max(0, Math.min(100, (rating / 5) * 100))}%`;
  return (
    <div className={`relative inline-block leading-none tracking-[0.2em] ${sizeClass}`}>
      <div className="text-white/10">★★★★★</div>
      <div className="absolute inset-0 overflow-hidden text-amber transition-all duration-700" style={{ width }}>
        ★★★★★
      </div>
    </div>
  );
}
