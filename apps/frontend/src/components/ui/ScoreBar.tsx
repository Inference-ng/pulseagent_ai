interface ScoreBarProps { score: number; }

export function ScoreBar({ score }: ScoreBarProps) {
  return (
    <div className="score-bar-track">
      <div className="score-bar-fill" style={{ width: `${Math.max(8, score * 100)}%` }} />
    </div>
  );
}
