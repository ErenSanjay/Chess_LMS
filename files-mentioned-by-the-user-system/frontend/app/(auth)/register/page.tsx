"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import { RegistrationResponse, registerUser } from "../../../lib/auth";

export default function RegisterPage() {
  const [role, setRole] = useState<"teacher" | "student">("teacher");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [error, setError] = useState<string | null>(null);
  const [result, setResult] = useState<RegistrationResponse | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setIsSubmitting(true);

    try {
      const result = await registerUser({
        role,
        display_name: displayName,
        email,
        password,
      });
      setResult(result);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Registration failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  return (
    <main className="flex min-h-screen items-center justify-center bg-paper px-6 py-10 text-ink">
      <section className="w-full max-w-lg border border-ink/15 bg-white p-6 shadow-sm">
        <p className="text-sm font-semibold uppercase tracking-wider text-board">
          Chess LMS
        </p>
        <h1 className="mt-2 text-2xl font-semibold">Create an account</h1>

        {result ? (
          <div className="mt-6 border border-board/30 bg-board/5 p-4 text-sm leading-6">
            <p className="font-semibold">{result.message}</p>
            {result.verification_token ? (
              <p className="mt-3 break-all">
                Development verification link:{" "}
                <Link
                  className="font-semibold text-board"
                  href={`/verify-email?token=${encodeURIComponent(
                    result.verification_token,
                  )}`}
                >
                  Verify email
                </Link>
              </p>
            ) : null}
          </div>
        ) : null}

        <form className="mt-8 space-y-5" onSubmit={handleSubmit}>
          <fieldset>
            <legend className="text-sm font-medium">Account type</legend>
            <div className="mt-2 grid grid-cols-2 border border-ink/20">
              {(["teacher", "student"] as const).map((option) => (
                <button
                  key={option}
                  className={
                    role === option
                      ? "bg-board px-4 py-3 text-sm font-semibold capitalize text-white"
                      : "bg-white px-4 py-3 text-sm font-semibold capitalize text-ink"
                  }
                  type="button"
                  onClick={() => setRole(option)}
                >
                  {option}
                </button>
              ))}
            </div>
          </fieldset>

          <label className="block">
            <span className="text-sm font-medium">Display name</span>
            <input
              className="mt-2 w-full border border-ink/20 px-3 py-2 outline-none focus:border-board"
              value={displayName}
              onChange={(event) => setDisplayName(event.target.value)}
              required
            />
          </label>

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
              minLength={10}
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
            {isSubmitting ? "Creating account..." : "Create account"}
          </button>
        </form>

        <p className="mt-6 text-sm text-ink/65">
          Already have an account?{" "}
          <Link className="font-semibold text-board" href="/login">
            Log in
          </Link>
        </p>
      </section>
    </main>
  );
}
