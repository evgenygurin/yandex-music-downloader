import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import Link from "next/link";
import "./globals.css";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "DJ AI Studio",
  description: "AI-powered DJ library management and set building",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-background`}
      >
        <header className="border-b border-border">
          <div className="container mx-auto px-4 py-4">
            <nav className="flex items-center justify-between">
              <Link href="/" className="text-xl font-bold">
                DJ AI Studio
              </Link>
              <div className="flex gap-6">
                <Link
                  href="/tracks"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Tracks
                </Link>
                <Link
                  href="/sets"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Sets
                </Link>
                <Link
                  href="/analyze"
                  className="text-muted-foreground hover:text-foreground transition-colors"
                >
                  Analyze
                </Link>
              </div>
            </nav>
          </div>
        </header>
        <main className="container mx-auto px-4 py-8">{children}</main>
      </body>
    </html>
  );
}
