import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EchoMind — The Senior Who Never Graduates",
  description:
    "Institutional memory AI agent for college clubs. 5 years of minutes, budgets, sponsor emails and post-mortems — with citations for every answer.",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <link
          href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap"
          rel="stylesheet"
        />
      </head>
      <body className="antialiased" style={{ fontFamily: "'Inter', system-ui, sans-serif" }}>
        {children}
      </body>
    </html>
  );
}
