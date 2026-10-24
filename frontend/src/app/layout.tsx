import type { Metadata, Viewport } from "next";
import { Geist, Geist_Mono } from "next/font/google";
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
  title: "SwasthyaAI - AI Health Assistant",
  description: "Intelligent health triage and symptom assessment powered by AI. Get guidance on your health concerns.",
  keywords: ["health", "AI", "triage", "symptoms", "healthcare", "medical assistant"],
  authors: [{ name: "SwasthyaAI Team" }],
  creator: "SwasthyaAI",
  publisher: "SwasthyaAI",
  robots: "index, follow",
  openGraph: {
    title: "SwasthyaAI - AI Health Assistant",
    description: "Intelligent health triage and symptom assessment powered by AI.",
    type: "website",
    locale: "en_IN",
    siteName: "SwasthyaAI",
  },
  twitter: {
    card: "summary_large_image",
    title: "SwasthyaAI - AI Health Assistant",
    description: "Intelligent health triage and symptom assessment powered by AI.",
  },
  verification: {
    google: "swasthyaai",
  },
};

export const viewport: Viewport = {
  themeColor: [
    { media: "(prefers-color-scheme: light)", color: "#0d9488" },
    { media: "(prefers-color-scheme: dark)", color: "#14b8a6" },
  ],
  width: "device-width",
  initialScale: 1,
  maximumScale: 5,
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en-IN" className={`${geistSans.variable} ${geistMono.variable} h-full antialiased`}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="min-h-full flex flex-col bg-background text-foreground">{children}</body>
    </html>
  );
}