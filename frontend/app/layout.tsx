import type { Metadata } from "next";
import "./globals.css";
import { PieceProvider } from "../components/PieceProvider";

export const metadata: Metadata = {
  title: "Cello Practice AI",
  description: "Local foundation for score-aware cello performance analysis",
};

export default function RootLayout({
  children,
}: Readonly<{ children: React.ReactNode }>) {
  return (
    <html lang="en">
      <body><PieceProvider>{children}</PieceProvider></body>
    </html>
  );
}
