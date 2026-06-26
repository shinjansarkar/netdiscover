import type { Metadata } from "next";
import { Space_Grotesk, Space_Mono } from "next/font/google";
import Sidebar from "@/components/Sidebar";
import "./globals.css";

const spaceGrotesk = Space_Grotesk({
  variable: "--font-space-grotesk",
  subsets: ["latin"],
});

const spaceMono = Space_Mono({
  weight: ["400", "700"],
  variable: "--font-space-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Netdiscover Brutalist",
  description: "Modern network discovery scanner",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html
      lang="en"
      className={`${spaceGrotesk.variable} ${spaceMono.variable} h-full antialiased`}
    >
      <body className="min-h-full flex bg-brutal-bg">
        <Sidebar />
        <main className="flex-1 p-4 overflow-y-auto">
          {children}
        </main>
      </body>
    </html>
  );
}
