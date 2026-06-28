const features = [
  "Classrooms",
  "Homework",
  "Live boards",
  "Schedules",
  "Position database",
];

export default function HomePage() {
  return (
    <main className="min-h-screen bg-paper text-ink">
      <section className="mx-auto flex min-h-screen w-full max-w-6xl flex-col justify-between px-6 py-8 sm:px-8 lg:px-10">
        <header className="flex items-center justify-between border-b border-ink/10 pb-5">
          <div>
            <p className="text-sm font-semibold uppercase tracking-wider text-board">
              Chess LMS
            </p>
            <h1 className="mt-2 text-3xl font-semibold sm:text-4xl">
              Coaching classrooms, homework, and live chess in one workspace.
            </h1>
          </div>
          <div className="hidden h-16 w-16 grid-cols-2 grid-rows-2 overflow-hidden border border-ink/20 sm:grid">
            <span className="bg-board" />
            <span className="bg-paper" />
            <span className="bg-paper" />
            <span className="bg-board" />
          </div>
        </header>

        <div className="grid gap-8 py-12 lg:grid-cols-[1.15fr_0.85fr] lg:items-center">
          <div>
            <p className="max-w-2xl text-lg leading-8 text-ink/75">
              The implementation has started with a production-oriented
              foundation: typed frontend, FastAPI backend, Dockerized services,
              and clean module boundaries ready for the next milestones.
            </p>
            <div className="mt-8 flex flex-wrap gap-3">
              {features.map((feature) => (
                <span
                  key={feature}
                  className="border border-ink/15 bg-white px-3 py-2 text-sm font-medium"
                >
                  {feature}
                </span>
              ))}
            </div>
            <div className="mt-8 flex flex-wrap gap-3">
              <a className="bg-board px-5 py-3 font-semibold text-white" href="/register">
                Create account
              </a>
              <a className="border border-ink/20 bg-white px-5 py-3 font-semibold" href="/login">
                Log in
              </a>
            </div>
          </div>

          <div className="border border-ink/15 bg-white p-5 shadow-sm">
            <div className="grid aspect-square grid-cols-8 grid-rows-8 border border-ink/20">
              {Array.from({ length: 64 }, (_, index) => {
                const row = Math.floor(index / 8);
                const col = index % 8;
                const isDark = (row + col) % 2 === 1;

                return (
                  <div
                    key={index}
                    className={isDark ? "bg-board" : "bg-[#e8dcc5]"}
                  />
                );
              })}
            </div>
          </div>
        </div>

        <footer className="border-t border-ink/10 pt-5 text-sm text-ink/60">
          Milestone 1 foundation is ready for backend database work next.
        </footer>
      </section>
    </main>
  );
}
