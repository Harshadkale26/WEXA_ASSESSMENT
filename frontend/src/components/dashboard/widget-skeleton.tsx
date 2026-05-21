export function WidgetSkeleton() {
  return (
    <div className="flex h-full min-h-[180px] flex-col animate-pulse p-4">
      <div className="h-4 w-1/3 rounded bg-muted-bg" />
      <div className="mt-6 flex flex-1 items-end gap-2">
        {[40, 65, 45, 80, 55, 70].map((h, i) => (
          <div
            key={i}
            className="flex-1 rounded-t bg-muted-bg"
            style={{ height: `${h}%` }}
          />
        ))}
      </div>
    </div>
  );
}
