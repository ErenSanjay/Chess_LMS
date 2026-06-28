import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "Chess LMS",
  description: "Classroom-first chess coaching and homework platform.",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  );
}
