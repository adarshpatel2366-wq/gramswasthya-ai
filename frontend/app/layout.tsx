import "../styles/globals.css";
import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "GramSwasthya AI — स्वास्थ्य सहायक",
  description: "AI Healthcare Assistant for Rural India",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="min-h-screen">{children}</body>
    </html>
  );
}
