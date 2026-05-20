export default function HomePage() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center p-8">
      <div className="max-w-2xl text-center">
        <h1 className="text-4xl font-bold tracking-tight text-brand-900">
          Analytics Platform
        </h1>
        <p className="mt-4 text-lg text-slate-600">
          Real-time analytics SaaS - frontend scaffold ready.
        </p>
        <p className="mt-2 text-sm text-slate-400">
          API: {process.env.NEXT_PUBLIC_API_URL ?? "not configured"}
        </p>
      </div>
    </main>
  );
}

