"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";

import {
  RegistrationResponse,
  confirmPasswordReset,
  requestPasswordReset,
} from "../../../lib/auth";

export default function ResetPasswordPage() {
  const [email, setEmail] = useState("");
  const [token, setToken] = useState("");
  const [newPassword, setNewPassword] = useState("");
  const [requestResult, setRequestResult] = useState<RegistrationResponse | null>(null);
  const [message, setMessage] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [isSubmitting, setIsSubmitting] = useState(false);

  async function handleRequest(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSubmitting(true);

    try {
      const result = await requestPasswordReset(email);
      setRequestResult(result);
      if (result.verification_token) {
        setToken(result.verification_token);
      }
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Request failed");
    } finally {
      setIsSubmitting(false);
    }
  }

  async function handleConfirm(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError(null);
    setMessage(null);
    setIsSubmitting(true);

    try {
      const result = await confirmPasswordReset({
        token,
        new_password: newPassword,
      });
      setMessage(result.message);
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : "Reset failed");
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
        <h1 className="mt-2 text-2xl font-semibold">Reset password</h1>

        <form className="mt-8 space-y-4" onSubmit={handleRequest}>
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
          <button
            className="w-full border border-ink/20 bg-white px-4 py-3 font-semibold disabled:cursor-not-allowed disabled:opacity-60"
            type="submit"
            disabled={isSubmitting}
          >
            Request reset token
          </button>
        </form>

        {requestResult ? (
          <p className="mt-4 break-all text-sm leading-6 text-ink/70">
            {requestResult.message}
          </p>
        ) : null}

        <form className="mt-8 space-y-4" onSubmit={handleConfirm}>
          <label className="block">
            <span className="text-sm font-medium">Reset token</span>
            <textarea
              className="mt-2 min-h-24 w-full border border-ink/20 px-3 py-2 outline-none focus:border-board"
              value={token}
              onChange={(event) => setToken(event.target.value)}
              required
            />
          </label>

          <label className="block">
            <span className="text-sm font-medium">New password</span>
            <input
              className="mt-2 w-full border border-ink/20 px-3 py-2 outline-none focus:border-board"
              type="password"
              minLength={10}
              value={newPassword}
              onChange={(event) => setNewPassword(event.target.value)}
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
            Reset password
          </button>
        </form>

        <Link className="mt-6 block text-sm font-semibold text-board" href="/login">
          Back to login
        </Link>
      </section>
    </main>
  );
}
