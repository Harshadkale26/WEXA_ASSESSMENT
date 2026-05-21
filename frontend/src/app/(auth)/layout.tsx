export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="flex min-h-screen flex-col items-center justify-center bg-background px-4 py-12">
      <div className="mb-8 text-center">
        <p className="text-sm font-medium uppercase tracking-wider text-brand-600">
          Analytics Platform
        </p>
        <h1 className="mt-2 text-2xl font-bold text-foreground">Welcome</h1>
        <p className="mt-1 text-sm text-muted">Sign in or create your organization</p>
      </div>
      <div className="w-full max-w-md">{children}</div>
    </div>
  );
}
