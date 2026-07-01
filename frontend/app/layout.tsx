import type { Metadata } from "next";
import "./globals.css";

export const metadata: Metadata = {
  title: "EchoMind — The senior who never graduates",
  description: "Institutional memory agent for Nexus Tech Club",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="antialiased">{children}</body>
    </html>
  );
}
