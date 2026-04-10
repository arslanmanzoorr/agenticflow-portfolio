"use client";

import { motion, useReducedMotion, Variants } from "framer-motion";
import { useState, useEffect, useCallback } from "react";
import Button from "@/components/ui/Button";
import { ArrowRight } from "lucide-react";

// ---------------------------------------------------------------------------
// Animation variants
// ---------------------------------------------------------------------------

const staggerContainer: Variants = {
  hidden: { opacity: 0 },
  show: {
    opacity: 1,
    transition: { staggerChildren: 0.1, delayChildren: 0.15 },
  },
};

const slideFromLeft: Variants = {
  hidden: { opacity: 0, x: -40 },
  show: {
    opacity: 1,
    x: 0,
    transition: { type: "spring", stiffness: 100, damping: 15 },
  },
};

const fadeUp: Variants = {
  hidden: { opacity: 0, y: 24 },
  show: {
    opacity: 1,
    y: 0,
    transition: { type: "spring", stiffness: 100, damping: 15 },
  },
};

const toolBadgeFadeIn = (i: number): Variants => ({
  hidden: { opacity: 0, scale: 0.85 },
  show: {
    opacity: 1,
    scale: 1,
    transition: {
      type: "spring",
      stiffness: 100,
      damping: 15,
      delay: 0.8 + i * 0.1,
    },
  },
});

// ---------------------------------------------------------------------------
// Word-by-word reveal component
// ---------------------------------------------------------------------------

function WordReveal({
  text,
  className,
  staggerDelay = 0.08,
  startDelay = 0,
}: {
  text: string;
  className?: string;
  staggerDelay?: number;
  startDelay?: number;
}) {
  const words = text.split(" ");
  return (
    <span className={className}>
      {words.map((word, i) => (
        <motion.span
          key={i}
          className="inline-block"
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{
            type: "spring",
            stiffness: 100,
            damping: 15,
            delay: startDelay + i * staggerDelay,
          }}
        >
          {word}
          {i < words.length - 1 ? "\u00A0" : ""}
        </motion.span>
      ))}
    </span>
  );
}

// ---------------------------------------------------------------------------
// Typing terminal
// ---------------------------------------------------------------------------

const terminalLines = [
  { prefix: "~", text: "workflow.trigger()", color: "text-cyan-400" },
  {
    prefix: ">",
    text: "Scraping leads from 3 sources...",
    color: "text-[#94a3b8]",
  },
  {
    prefix: ">",
    text: "Enriching 142 contacts via API",
    color: "text-[#94a3b8]",
  },
  {
    prefix: ">",
    text: "Scoring & qualifying leads...",
    color: "text-[#94a3b8]",
  },
  {
    prefix: ">",
    text: "Synced 87 leads to HubSpot",
    color: "text-emerald-400",
  },
  {
    prefix: "\u2713",
    text: "Pipeline complete \u2014 4.2s",
    color: "text-cyan-400",
  },
];

function useTypingTerminal(lines: typeof terminalLines) {
  const [visibleLines, setVisibleLines] = useState<
    { prefix: string; text: string; color: string; displayedText: string }[]
  >([]);

  const prefersReduced = useReducedMotion();

  const runTyping = useCallback(() => {
    if (prefersReduced) {
      setVisibleLines(lines.map((l) => ({ ...l, displayedText: l.text })));
      return;
    }

    let lineIdx = 0;
    const lineDelay = 500;
    const charDelay = 22;

    function typeLine() {
      if (lineIdx >= lines.length) return;
      const currentLine = lines[lineIdx];
      const currentIdx = lineIdx;
      let charIdx = 0;

      setVisibleLines((prev) => [
        ...prev,
        { ...currentLine, displayedText: "" },
      ]);

      function typeChar() {
        if (charIdx <= currentLine.text.length) {
          setVisibleLines((prev) => {
            const next = [...prev];
            next[currentIdx] = {
              ...currentLine,
              displayedText: currentLine.text.slice(0, charIdx),
            };
            return next;
          });
          charIdx++;
          setTimeout(typeChar, charDelay);
        } else {
          lineIdx++;
          setTimeout(typeLine, lineDelay);
        }
      }

      typeChar();
    }

    const startTimeout = setTimeout(typeLine, 1200);
    return () => clearTimeout(startTimeout);
  }, [lines, prefersReduced]);

  useEffect(() => {
    const cleanup = runTyping();
    return cleanup;
  }, [runTyping]);

  return visibleLines;
}

// ---------------------------------------------------------------------------
// Tool badges
// ---------------------------------------------------------------------------

const tools = [
  { label: "n8n", accent: "border-orange-500/30 text-orange-400" },
  { label: "Python", accent: "border-yellow-500/30 text-yellow-400" },
  { label: "OpenClaw", accent: "border-purple-500/30 text-purple-400" },
  { label: "OpenAI", accent: "border-emerald-500/30 text-emerald-400" },
];

// ---------------------------------------------------------------------------
// Hero component
// ---------------------------------------------------------------------------

export default function Hero() {
  const prefersReduced = useReducedMotion();
  const typedLines = useTypingTerminal(terminalLines);

  // heading word delays (line 1 starts at 0.3s, line 2 after line 1 finishes)
  const line1Words = "I Build Agentic AI".split(" ").length;
  const line1Start = 0.3;
  const line2Start = line1Start + line1Words * 0.08 + 0.05;

  return (
    <section className="relative min-h-[100dvh] flex items-center overflow-hidden">
      <div className="relative z-10 max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 w-full py-20">
        <div className="grid lg:grid-cols-2 gap-12 lg:gap-20 items-center">
          {/* ------------------------------------------------------------ */}
          {/* Left -- Text content                                         */}
          {/* ------------------------------------------------------------ */}
          <motion.div
            variants={staggerContainer}
            initial="hidden"
            animate="show"
            className="max-w-2xl"
          >
            {/* Status badge */}
            <motion.div variants={slideFromLeft} className="mb-8">
              <span className="inline-flex items-center gap-2 px-4 py-1.5 text-xs font-medium tracking-wide rounded-full border border-cyan-500/20 bg-cyan-500/5 text-cyan-400 backdrop-blur-sm">
                <span className="relative flex h-2 w-2">
                  <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-cyan-400 opacity-75" />
                  <span className="relative inline-flex h-2 w-2 rounded-full bg-cyan-400" />
                </span>
                Available for new projects
              </span>
            </motion.div>

            {/* Heading with per-word reveal */}
            <h1 className="text-4xl sm:text-5xl lg:text-6xl xl:text-[4.25rem] font-bold tracking-tight text-[#f8fafc] leading-[1.08]">
              <WordReveal
                text="I Build Agentic AI"
                staggerDelay={0.08}
                startDelay={line1Start}
              />
              <br />
              <WordReveal
                text="That Runs Your Business"
                className="bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent"
                staggerDelay={0.08}
                startDelay={line2Start}
              />
            </h1>

            {/* Subtitle */}
            <motion.p
              variants={fadeUp}
              className="mt-7 text-lg text-[#94a3b8] leading-relaxed max-w-xl"
            >
              AI Automation Engineer building agentic workflows with n8n,
              Python, and intelligent integrations that eliminate 20+ hours of
              manual work per week.
            </motion.p>

            {/* CTA buttons */}
            <motion.div variants={fadeUp} className="mt-10 flex flex-wrap gap-4">
              <Button
                variant="primary"
                size="lg"
                href="/projects"
                className="bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl px-8 py-4 shadow-lg shadow-cyan-500/25 hover:shadow-cyan-500/40 hover:brightness-110 transition-all duration-200"
              >
                View Projects
                <ArrowRight className="w-4 h-4 ml-1" />
              </Button>
              <Button
                variant="secondary"
                size="lg"
                href="/contact"
                className="border border-[#2a2a3e] text-[#94a3b8] rounded-xl px-8 py-4 hover:border-cyan-500/40 hover:text-[#f8fafc] transition-all duration-200"
              >
                Let&apos;s Talk
              </Button>
            </motion.div>

            {/* Tool badges */}
            <div className="mt-10 flex flex-wrap items-center gap-3">
              {tools.map((tool, i) => (
                <motion.span
                  key={tool.label}
                  variants={toolBadgeFadeIn(i)}
                  initial="hidden"
                  animate="show"
                  className={`inline-flex items-center px-3 py-1 text-xs font-medium rounded-md border bg-white/[0.02] backdrop-blur-sm ${tool.accent}`}
                >
                  {tool.label}
                </motion.span>
              ))}
            </div>
          </motion.div>

          {/* ------------------------------------------------------------ */}
          {/* Right -- Animated terminal                                    */}
          {/* ------------------------------------------------------------ */}
          <motion.div
            initial={
              prefersReduced
                ? { opacity: 1 }
                : { opacity: 0, x: 60, rotateY: -8 }
            }
            animate={
              prefersReduced
                ? { opacity: 1 }
                : { opacity: 1, x: 0, rotateY: -5 }
            }
            transition={{
              duration: 0.7,
              delay: 0.4,
              ease: [0.21, 0.47, 0.32, 0.98],
            }}
            className="hidden lg:block"
            style={{ perspective: 1200 }}
          >
            <motion.div
              animate={
                prefersReduced
                  ? {}
                  : { y: [0, -10, 0] }
              }
              transition={
                prefersReduced
                  ? {}
                  : {
                      y: {
                        duration: 5,
                        repeat: Infinity,
                        repeatType: "loop",
                        ease: "easeInOut",
                      },
                    }
              }
              className="relative"
            >
              {/* Glow behind terminal */}
              <div className="absolute -inset-6 bg-gradient-to-br from-cyan-500/[0.08] via-blue-500/[0.06] to-purple-500/[0.04] rounded-3xl blur-2xl" />

              <div className="relative bg-[#0a0a12] border border-[#1a1a2e] rounded-2xl overflow-hidden shadow-2xl shadow-cyan-950/30">
                {/* Terminal header */}
                <div className="flex items-center gap-2 px-4 py-3 border-b border-[#1a1a2e] bg-[#0e0e18]">
                  <div className="w-3 h-3 rounded-full bg-[#ff5f57]" />
                  <div className="w-3 h-3 rounded-full bg-[#febc2e]" />
                  <div className="w-3 h-3 rounded-full bg-[#28c840]" />
                  <span className="ml-3 text-xs text-[#94a3b8]/70 font-mono tracking-wide">
                    automation-pipeline.sh
                  </span>
                </div>

                {/* Terminal body */}
                <div className="p-6 font-mono text-sm min-h-[220px] space-y-3">
                  {typedLines.map((line, i) => (
                    <div key={i} className="flex items-start gap-3">
                      <span className="text-cyan-500/50 select-none shrink-0 w-4 text-right">
                        {line.prefix}
                      </span>
                      <span className={line.color}>
                        {line.displayedText}
                      </span>
                    </div>
                  ))}

                  {/* Blinking cursor */}
                  {typedLines.length < terminalLines.length && (
                    <div className="flex items-center gap-3">
                      <span className="text-cyan-500/50 select-none w-4 text-right">
                        ~
                      </span>
                      <span className="w-[9px] h-[18px] bg-cyan-400 animate-pulse rounded-[1px]" />
                    </div>
                  )}

                  {typedLines.length === terminalLines.length && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      transition={{ duration: 0.3, delay: 0.2 }}
                      className="flex items-center gap-3"
                    >
                      <span className="text-cyan-500/50 select-none w-4 text-right">
                        ~
                      </span>
                      <span className="w-[9px] h-[18px] bg-cyan-400 animate-pulse rounded-[1px]" />
                    </motion.div>
                  )}
                </div>
              </div>
            </motion.div>
          </motion.div>
        </div>
      </div>
    </section>
  );
}
