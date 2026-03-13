"use client";

import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { ArrowRight } from "lucide-react";

const container = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.15, delayChildren: 0.2 },
  },
};

const item = {
  hidden: { opacity: 0, y: 20 },
  show: {
    opacity: 1,
    y: 0,
    transition: { duration: 0.6, ease: [0.21, 0.47, 0.32, 0.98] },
  },
};

const terminalLines = [
  { prefix: "~", text: "agent.deploy()", color: "text-cyan-400" },
  { prefix: ">", text: "Spawning 3 AI agents...", color: "text-[#94a3b8]" },
  { prefix: ">", text: "Agent[lead-scout]: Scraped 142 leads", color: "text-[#94a3b8]" },
  { prefix: ">", text: "Agent[enricher]: Scoring via GPT-4...", color: "text-[#94a3b8]" },
  { prefix: ">", text: "Agent[syncer]: Pushed 87 to HubSpot", color: "text-emerald-400" },
  { prefix: "✓", text: "All agents complete — 4.2s", color: "text-cyan-400" },
];

export default function Hero() {
  return (
    <section className="relative min-h-screen flex items-center overflow-hidden">
      {/* Background grid pattern */}
      <div className="absolute inset-0 bg-[linear-gradient(rgba(6,182,212,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(6,182,212,0.03)_1px,transparent_1px)] bg-[size:64px_64px]" />

      {/* Gradient orbs */}
      <div className="absolute top-1/4 -left-32 w-96 h-96 bg-cyan-500/10 rounded-full blur-[128px]" />
      <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-blue-500/10 rounded-full blur-[128px]" />

      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-20">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-16 items-center">
          {/* Left — Copy */}
          <motion.div
            variants={container}
            initial="hidden"
            animate="show"
            className="max-w-2xl"
          >
            <motion.div variants={item} className="mb-6">
              <span className="inline-flex items-center gap-2 px-3 py-1 text-xs font-medium rounded-full border border-cyan-500/20 bg-cyan-500/10 text-cyan-400">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-400" />
                </span>
                Available for new projects
              </span>
            </motion.div>

            <motion.h1
              variants={item}
              className="text-4xl sm:text-5xl lg:text-6xl font-bold tracking-tight text-[#f8fafc] leading-[1.1]"
            >
              I Build Agentic AI
              <br />
              <span className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                That Runs Your Business
              </span>
            </motion.h1>

            <motion.p
              variants={item}
              className="mt-6 text-lg text-[#94a3b8] leading-relaxed max-w-xl"
            >
              AI Automation Engineer building agentic workflows with n8n,
              Python, and intelligent integrations that eliminate 20+ hours
              of manual work per week.
            </motion.p>

            <motion.div variants={item} className="mt-8 flex flex-wrap gap-4">
              <Button variant="primary" size="lg" href="/projects">
                View Projects
                <ArrowRight className="w-4 h-4" />
              </Button>
              <Button variant="secondary" size="lg" href="/contact">
                Let&apos;s Talk
              </Button>
            </motion.div>
          </motion.div>

          {/* Right — Animated Terminal */}
          <motion.div
            initial={{ opacity: 0, x: 40 }}
            animate={{ opacity: 1, x: 0 }}
            transition={{ duration: 0.8, delay: 0.5, ease: [0.21, 0.47, 0.32, 0.98] }}
            className="hidden lg:block"
          >
            <div className="relative">
              {/* Glow behind terminal */}
              <div className="absolute -inset-4 bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-2xl blur-xl" />

              <div className="relative bg-[#0d0d14] border border-[#1a1a2e] rounded-xl overflow-hidden shadow-2xl">
                {/* Terminal header */}
                <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1a1a2e] bg-[#12121a]">
                  <div className="w-3 h-3 rounded-full bg-red-500/70" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/70" />
                  <div className="w-3 h-3 rounded-full bg-green-500/70" />
                  <span className="ml-2 text-xs text-[#94a3b8] font-mono">
                    automation-pipeline.sh
                  </span>
                </div>

                {/* Terminal body */}
                <div className="p-5 font-mono text-sm space-y-2.5">
                  {terminalLines.map((line, i) => (
                    <motion.div
                      key={i}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: 0.8 + i * 0.3, duration: 0.4 }}
                      className="flex items-start gap-3"
                    >
                      <span className="text-cyan-500/60 select-none shrink-0">
                        {line.prefix}
                      </span>
                      <span className={line.color}>{line.text}</span>
                    </motion.div>
                  ))}

                  {/* Blinking cursor */}
                  <motion.div
                    initial={{ opacity: 0 }}
                    animate={{ opacity: 1 }}
                    transition={{ delay: 3.2 }}
                    className="flex items-center gap-3"
                  >
                    <span className="text-cyan-500/60 select-none">~</span>
                    <span className="w-2 h-5 bg-cyan-400 animate-pulse" />
                  </motion.div>
                </div>
              </div>
            </div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
