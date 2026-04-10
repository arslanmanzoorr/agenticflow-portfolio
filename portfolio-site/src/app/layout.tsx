import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Navbar from "@/components/layout/Navbar";
import Footer from "@/components/layout/Footer";
import AnimatedBackground from "@/components/ui/AnimatedBackground";
import SpotlightCursor from "@/components/ui/SpotlightCursor";
import ChatPanel from "@/components/ChatPanel";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
  weight: ["400", "500", "600", "700", "800"],
});

export const metadata: Metadata = {
  title: "Arslan Manzoor | AI Automation Engineer",
  description:
    "AI Automation Engineer specializing in agentic workflows, n8n pipelines, Python APIs, OpenClaw agents, and intelligent automation solutions that scale businesses.",
  keywords: [
    "AI Automation",
    "n8n",
    "Python",
    "OpenClaw",
    "Workflow Automation",
    "API Integration",
    "Apify",
    "Airtable",
    "HubSpot",
    "Agentic AI",
  ],
  openGraph: {
    title: "Arslan Manzoor | AI Automation Engineer",
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
      <body className="min-h-screen relative">
        <AnimatedBackground />
        <SpotlightCursor />
        <div className="relative z-10">
          <Navbar />
          <main>{children}</main>
          <Footer />
        </div>
        <ChatPanel />
      </body>
    </html>
  );
}
