"use client";

import Link from "next/link";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";

import {
  AuthUser,
  clearAuthSession,
  fetchCurrentUser,
  getAccessToken,
} from "../../lib/auth";

export default function DashboardPage() {
  const router = useRouter();
  const [user, setUser] = useState<AuthUser | null>(null);
  const [status, setStatus] = useState("Loading session...");

  useEffect(() => {
    const token = getAccessToken();
    if (!token) {
      router.replace("/login");
      return;
    }

    fetchCurrentUser(token)
      .then((currentUser) => {
        setUser(currentUser);
        setStatus("Connected");
      })
      .catch(() => {
        clearAuthSession();
        router.replace("/login");
      });
  }, [router]);

  function handleLogout() {
    clearAuthSession();
    router.replace("/login");
  }

  return (
    <main className="min-h-screen bg-paper text-ink">
      <section className="mx-auto w-full max-w-6xl px-6 py-8 sm:px-8 lg:px-10">
        <header className="flex flex-col gap-4 border-b border-ink/10 pb-6 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-board">
              Dashboard
            </p>
            <h1 className="mt-2 text-3xl font-semibold">Chess LMS workspace</h1>
          </div>
          <button
            className="border border-ink/20 bg-white px-4 py-2 text-sm font-semibold"
            type="button"
            onClick={handleLogout}
          >
            Log out
          </button>
        </header>

        <div className="grid gap-6 py-8 lg:grid-cols-[0.75fr_1.25fr]">
          <section className="border border-ink/15 bg-white p-5 shadow-sm">
            <p className="text-sm font-semibold text-board">{status}</p>
            {user ? (
              <div className="mt-4 space-y-2 text-sm">
                <p>
                  <span className="font-semibold">Name:</span>{" "}
                  {user.display_name}
                </p>
                <p>
                  <span className="font-semibold">Email:</span> {user.email}
                </p>
                <p>
                  <span className="font-semibold">Role:</span> {user.role}
                </p>
                <p>
                  <span className="font-semibold">Status:</span> {user.status}
                </p>
              </div>
            ) : null}
          </section>

          <section className="grid gap-4 sm:grid-cols-2">
            {["Classrooms", "Homework", "Live board", "Schedule"].map((item) => (
              <div key={item} className="border border-ink/15 bg-white p-5 shadow-sm">
                <h2 className="text-lg font-semibold">{item}</h2>
                <p className="mt-3 text-sm leading-6 text-ink/65">
                  This module will become active in the next implementation
                  milestones.
                </p>
              </div>
            ))}
          </section>
        </div>

        <Link className="text-sm font-semibold text-board" href="/">
          Back to home
        </Link>
      </section>
    </main>
  );
}
