"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

import { loginUser, saveAuthSession } from "../../../lib/auth";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const result = await loginUser({ email, password });
      saveAuthSession(result);
      router.push("/dashboard");
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Login failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper px-6 py-10 text-ink">
      <section className="w-full max-w-md border border-ink/15 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wider text-board">
          Chess LMS
        </p>
        <h1 className="mt-2 text-2xl font-semibold">Log in</h1>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="text-sm font-medium">Email</span>
            <input
              className="mt-2 w-full border border-ink/20 px-3 py-2 outline-none focus:border-board"
              type="email"
              value={email}
              onChange={(event) => setEmail(event.target.value)}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">Password</span>
            <input
              className="mt-2 w-full border border-ink/20 px-3 py-2 outline-none focus:border-board"
              type="password"
              value={password}
              onChange={(event) => setPassword(event.target.value)}
              required
            />
          </label>

          {error ? <p className="text-sm text-red-700">{error}</p> : null}

          <button
            className="w-full bg-board px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Logging in..." : "Log in"}
          </button>
        </form>

        <p className="mt-6 text-sm text-ink/65">
          Need an account?{" "}
          <Link className="font-semibold text-board" href="/register">
            Create one
          </Link>
        </p>
        <Link className="mt-3 block text-sm font-semibold text-board" href="/reset-password">
          Reset password
        </Link>
      </section>
    </main>
  );
}
