// app/page.tsx
import Link from "next/link";

export default function Home() {
  return (
    <main className="min-h-screen flex items-center justify-center bg-background text-foreground">
      <div className="w-full max-w-md p-8 rounded-2xl border border-neutral-200 shadow-sm">
        <h1 className="text-2xl font-semibold mb-2">
          Open Learning Assistant
        </h1>
        <p className="text-sm text-neutral-600 mb-6">
          Welcome! Please login or create an account to continue.
        </p>

        <div className="flex gap-3">
          <Link
            href="/login"
            className="flex-1 text-center py-2.5 rounded-lg border border-neutral-900 bg-neutral-900 text-white text-sm font-medium hover:bg-neutral-800 transition"
          >
            Login
          </Link>
          <Link
            href="/signup"
            className="flex-1 text-center py-2.5 rounded-lg border border-neutral-300 text-sm font-medium hover:bg-neutral-50 transition"
          >
            Sign up
          </Link>
        </div>
      </div>
    </main>
  );
}
