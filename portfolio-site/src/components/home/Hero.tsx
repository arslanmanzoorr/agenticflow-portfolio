"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import { ChevronDown } from "lucide-react";
import { SplineScene } from "@/components/ui/splite";
import { Spotlight } from "@/components/ui/spotlight";
import { GooeyText } from "@/components/ui/gooey-text";

// ---------------------------------------------------------------------------
// Clip-mask line reveal component
// ---------------------------------------------------------------------------

function RevealLine({
  children,
  delay = 0,
}: {
  children: React.ReactNode;
  delay?: number;
}) {
  return (
    <div className="overflow-hidden">
      <motion.div
        initial={{ y: "100%" }}
        animate={{ y: 0 }}
        transition={{
          duration: 0.8,
          delay,
          ease: [0.76, 0, 0.24, 1],
        }}
      >
        {children}
      </motion.div>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Hero component — Spline 3D + Gooey text morphing
// ---------------------------------------------------------------------------

export default function Hero() {
  const headingStagger = 0.15;
  const line1Delay = 0.3;
  const line2Delay = line1Delay + headingStagger;
  const line3Delay = line2Delay + headingStagger;
  const dividerDelay = line3Delay + 0.4;
  const subtitleDelay = 0.6;
  const ctaDelay = 0.8;

  return (
    <section className="relative min-h-[100dvh] flex items-center overflow-hidden">
      {/* Spotlight effect */}
      <Spotlight
        className="-top-40 left-0 md:left-60 md:-top-20"
        fill="rgba(6, 182, 212, 0.15)"
      />

      <div className="relative z-10 max-w-7xl mx-auto px-6 w-full py-20">
        <div className="flex flex-col lg:flex-row items-center gap-8 lg:gap-0">
          {/* Left content */}
          <div className="flex-1 w-full">
            {/* Status badge */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.6, delay: 0.2 }}
              className="mb-10"
            >
              <span className="inline-flex items-center gap-2.5 px-5 py-2 text-xs font-medium tracking-widest uppercase rounded-full border border-white/10 bg-white/5 text-[#94a3b8]">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-emerald-400" />
                </span>
                Available for Projects
              </span>
            </motion.div>

            {/* Main heading */}
            <h1 className="text-5xl sm:text-6xl lg:text-7xl xl:text-8xl font-black tracking-tighter leading-[0.9]">
              <RevealLine delay={line1Delay}>
                <span className="block text-[#f8fafc]">I Build</span>
              </RevealLine>
              <RevealLine delay={line2Delay}>
                <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-violet-500 bg-clip-text text-transparent">
                  Agentic AI
                </span>
              </RevealLine>
              <RevealLine delay={line3Delay}>
                <span className="block text-[#f8fafc]">Systems</span>
              </RevealLine>
            </h1>

            {/* Gooey text morphing role titles */}
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.8, delay: dividerDelay }}
              className="mt-6 h-12"
            >
              <GooeyText
                texts={[
                  "AI Automation Engineer",
                  "n8n Pipeline Architect",
                  "OpenClaw Agent Builder",
                  "Python API Developer",
                  "Workflow Specialist",
                ]}
                morphTime={1.5}
                cooldownTime={1}
                className="h-12"
                textClassName="text-xl sm:text-2xl lg:text-3xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent"
              />
            </motion.div>

            {/* Subtitle */}
            <motion.p
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.7,
                delay: subtitleDelay,
                ease: [0.25, 0.46, 0.45, 0.94],
              }}
              className="text-base sm:text-lg text-[#64748b] max-w-xl leading-relaxed mt-6"
            >
              I design intelligent workflows with n8n, Python, and OpenClaw that
              save businesses 20+ hours weekly &mdash; turning manual chaos into
              automated excellence.
            </motion.p>

            {/* CTA row */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{
                duration: 0.7,
                delay: ctaDelay,
                ease: [0.25, 0.46, 0.45, 0.94],
              }}
              className="flex flex-wrap gap-4 mt-8"
            >
              <Link
                href="/projects"
                className="cursor-pointer inline-flex items-center justify-center bg-[#f8fafc] text-[#030308] font-semibold rounded-full px-8 py-4 text-sm hover:scale-105 transition-transform duration-200"
              >
                Explore Work
              </Link>
              <Link
                href="/contact"
                className="cursor-pointer inline-flex items-center justify-center text-[#94a3b8] border border-[#1e293b] rounded-full px-8 py-4 text-sm hover:border-[#94a3b8] transition-colors duration-200"
              >
                Get in Touch
              </Link>
            </motion.div>
          </div>

          {/* Right content — 3D Spline Robot */}
          <div className="flex-1 relative h-[400px] sm:h-[500px] lg:h-[600px] w-full">
            <motion.div
              initial={{ opacity: 0, scale: 0.9 }}
              animate={{ opacity: 1, scale: 1 }}
              transition={{
                duration: 1.2,
                delay: 0.5,
                ease: [0.25, 0.46, 0.45, 0.94],
              }}
              className="w-full h-full"
            >
              <SplineScene
                scene="https://prod.spline.design/kZDDjO5HuC9GJUM2/scene.splinecode"
                className="w-full h-full"
              />
            </motion.div>
          </div>
        </div>
      </div>

      {/* Scroll indicator */}
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        transition={{ duration: 0.6, delay: 1.2 }}
        className="absolute bottom-8 left-1/2 -translate-x-1/2 flex flex-col items-center gap-1 text-[#64748b]"
      >
        <span className="text-[10px] tracking-[0.2em] uppercase">Scroll</span>
        <motion.div
          animate={{ y: [0, 8, 0] }}
          transition={{
            duration: 2,
            repeat: Infinity,
            ease: "easeInOut",
          }}
        >
          <ChevronDown className="w-5 h-5" />
        </motion.div>
      </motion.div>
    </section>
  );
}
