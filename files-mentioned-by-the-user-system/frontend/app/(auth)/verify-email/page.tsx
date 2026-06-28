"use client";

import Link from "next/link";
import { useSearchParams } from "next/navigation";
import { FormEvent, useEffect, useState } from "react";

import { verifyEmail } from "../../../lib/auth";

export default function VerifyEmailPage() {
  const searchParams = useSearchParams();
  const [token, setToken] = useState(searchParams.get("token") ?? "");
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  useEffect(() => {
    const tokenFromUrl = searchParams.get("token");
    if (tokenFromUrl) {
      setToken(tokenFromUrl);
    }
  }, [searchParams]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSubmitting(true);

    try {
      const result = await verifyEmail(token);
      setMessage(result.message);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Verification failed");
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
        <h1 className="mt-2 text-2xl font-semibold">Verify email</h1>

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <label className="block">
            <span className="text-sm font-medium">Verification token</span>
            <textarea
              className="mt-2 min-h-28 w-full border border-ink/20 px-3 py-2 outline-none focus:border-board"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              required
            />
          </label>

          {message ? <p className="text-sm text-board">{message}</p> : null}
          {error ? <p className="text-sm text-red-700">{error}</p> : null}

          <button
            className="w-full bg-board px-4 py-3 font-semibold text-white disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={isSubmitting}
          >
            {isSubmitting ? "Verifying..." : "Verify email"}
          </button>
        </form>

        <Link className="mt-6 block text-sm font-semibold text-board" href="/login">
          Continue to login
        </Link>
      </section>
    </main>
  );
}
