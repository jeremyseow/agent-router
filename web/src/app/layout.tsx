import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import { Sidebar } from "@/components/Sidebar";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agent Router | AI Orchestration",
  description: "Advanced autonomous conversational AI middleware",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className="dark">
      <body className={`${inter.className} antialiased bg-background text-foreground overflow-hidden`}>
        <div className="flex h-screen w-full">
          <Sidebar />
          <main className="flex-1 relative overflow-auto bg-zinc-950/20">
            {children}
          </main>
        </div>
      </body>
    </html>
  );
}
