import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import ChatPanel from "@/components/ChatPanel";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Arslan Manzoor | AgenticFlow — AI Automation Engineer",
  description:
    "AI Automation Engineer specializing in agentic workflows, n8n pipelines, Python APIs, and intelligent automation solutions that scale businesses.",
  keywords: [
    "AI Automation",
    "n8n",
    "Python",
    "Workflow Automation",
    "API Integration",
    "Apify",
    "Airtable",
    "HubSpot",
  ],
  openGraph: {
    title: "Arslan Manzoor | AgenticFlow — AI Automation Engineer",
    description:
      "Building agentic automation solutions that scale businesses.",
    type: "website",
    locale: "en_US",
  },
};

export default function RootLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="min-h-screen">
        <Navbar />
        <main>{children}</main>
        <Footer />
        <ChatPanel />
      </body>
    </html>
  );
}
