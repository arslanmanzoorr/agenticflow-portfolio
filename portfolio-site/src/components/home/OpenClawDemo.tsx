"use client";

import { useState, useEffect, useRef } from "react";
import { motion, AnimatePresence } from "framer-motion";
import SectionHeading from "@/components/ui/SectionHeading";
import { Shield, Lock, Server, Eye } from "lucide-react";

const demoScenarios = [
  {
    id: "inbox",
    label: "Email Automation",
    icon: "📧",
    messages: [
      { role: "system", text: "🦞 OpenClaw Agent Active — Monitoring inbox..." },
      { role: "agent", text: "📥 47 new emails detected overnight" },
      { role: "agent", text: "🔍 Classifying with GPT-4... done" },
      { role: "agent", text: "✅ 31 routine — auto-drafted responses" },
      { role: "agent", text: "⚡ 8 urgent — flagged for immediate review" },
      { role: "agent", text: "🗑️ 8 spam/marketing — archived" },
      { role: "agent", text: "📋 Morning briefing sent to #inbox-summary" },
      { role: "result", text: "⏱️ Total time: 23 seconds | You saved: ~2.5 hours" },
    ],
  },
  {
    id: "support",
    label: "Customer Support",
    icon: "🎧",
    messages: [
      { role: "system", text: "🦞 ClawSupport Agent Online — Watching #support" },
      { role: "user", text: "Customer: 'How do I reset my API key?'" },
      { role: "agent", text: "🔍 Searching knowledge base via RAG..." },
      { role: "agent", text: "📄 Found: docs/api/authentication.md (98% match)" },
      { role: "agent", text: "✍️ Drafting personalized response..." },
      { role: "agent", text: "✅ Response sent — ticket auto-resolved" },
      { role: "agent", text: "📊 L1 resolution rate today: 87% (26/30 tickets)" },
      { role: "result", text: "⏱️ Response time: 8 seconds | Human agent time saved: 4.2 hrs" },
    ],
  },
  {
    id: "client",
    label: "Client Manager",
    icon: "👥",
    messages: [
      { role: "system", text: "🦞 ClawClientManager — Monitoring 12 active clients" },
      { role: "agent", text: "📩 Slack: @acme-corp requesting project update" },
      { role: "agent", text: "🔍 Pulling context from HubSpot CRM..." },
      { role: "agent", text: "✍️ Drafting response with last 3 interactions..." },
      { role: "agent", text: "✅ Draft ready for review (urgency: medium)" },
      { role: "agent", text: "⏰ Auto-scheduled follow-up: Friday 2pm" },
      { role: "agent", text: "⚠️ Alert: @bigcorp hasn't responded in 5 days" },
      { role: "result", text: "📊 Client health: 10 green | 1 yellow | 1 red" },
    ],
  },
];

const securityFeatures = [
  {
    icon: Shield,
    title: "Docker Isolation",
    description: "Every OpenClaw agent runs in an isolated Docker container with restricted network access and zero host-level permissions.",
  },
  {
    icon: Lock,
    title: "Encrypted Credentials",
    description: "API keys and tokens stored in encrypted vaults — never hardcoded, never exposed. Rotated automatically on schedule.",
  },
  {
    icon: Server,
    title: "Self-Hosted Only",
    description: "Your data never leaves your infrastructure. I deploy exclusively on your VPS/cloud — no third-party agent platforms.",
  },
  {
    icon: Eye,
    title: "Audit Logging",
    description: "Every agent action is logged with timestamps, inputs, and outputs. Full transparency — nothing happens in the dark.",
  },
];

export default function OpenClawDemo() {
  const [activeScenario, setActiveScenario] = useState(0);
  const [visibleLines, setVisibleLines] = useState(0);
  const [isPlaying, setIsPlaying] = useState(false);
  const terminalRef = useRef<HTMLDivElement>(null);

  const scenario = demoScenarios[activeScenario];

  useEffect(() => {
    setVisibleLines(0);
    setIsPlaying(true);
  }, [activeScenario]);

  useEffect(() => {
    if (!isPlaying) return;
    if (visibleLines >= scenario.messages.length) {
      setIsPlaying(false);
      return;
    }

    const timer = setTimeout(() => {
      setVisibleLines((v) => v + 1);
      if (terminalRef.current) {
        terminalRef.current.scrollTop = terminalRef.current.scrollHeight;
      }
    }, 600);

    return () => clearTimeout(timer);
  }, [visibleLines, isPlaying, scenario.messages.length]);

  const handleReplay = () => {
    setVisibleLines(0);
    setIsPlaying(true);
  };

  return (
    <section className="py-24 relative overflow-hidden">
      {/* Background glow */}
      <div className="absolute inset-0 pointer-events-none">
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-orange-500/5 rounded-full blur-[120px]" />
      </div>

      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 relative">
        <SectionHeading
          badge="🦞 OpenClaw Agents"
          title="See AI Agents in Action"
          subtitle="Watch how I deploy OpenClaw agents that actually do the work — securely, on your infrastructure."
        />

        {/* Interactive Demo Terminal */}
        <div className="max-w-4xl mx-auto mb-16">
          {/* Scenario Tabs */}
          <div className="flex gap-2 mb-4 overflow-x-auto pb-2">
            {demoScenarios.map((s, i) => (
              <button
                key={s.id}
                onClick={() => setActiveScenario(i)}
                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                  activeScenario === i
                    ? "bg-orange-500/20 border border-orange-500/40 text-orange-300"
                    : "bg-[#12121a]/80 border border-[#1e293b] text-[#94a3b8] hover:border-orange-500/20"
                }`}
              >
                <span>{s.icon}</span>
                {s.label}
              </button>
            ))}
          </div>

          {/* Terminal Window */}
          <div className="rounded-xl border border-[#1e293b] bg-[#0a0a0f] overflow-hidden shadow-2xl">
            {/* Terminal header */}
            <div className="flex items-center justify-between px-4 py-3 bg-[#12121a] border-b border-[#1e293b]">
              <div className="flex items-center gap-2">
                <div className="flex gap-1.5">
                  <div className="w-3 h-3 rounded-full bg-red-500/80" />
                  <div className="w-3 h-3 rounded-full bg-yellow-500/80" />
                  <div className="w-3 h-3 rounded-full bg-green-500/80" />
                </div>
                <span className="text-xs text-[#64748b] ml-2 font-mono">
                  openclaw-agent — {scenario.label.toLowerCase()}
                </span>
              </div>
              <div className="flex items-center gap-2">
                <span className="inline-flex items-center gap-1 px-2 py-0.5 text-[10px] font-medium rounded bg-green-500/10 border border-green-500/20 text-green-400">
                  <span className="w-1.5 h-1.5 rounded-full bg-green-400 animate-pulse" />
                  LIVE
                </span>
                <button
                  onClick={handleReplay}
                  className="text-xs text-[#64748b] hover:text-orange-400 transition-colors font-mono"
                >
                  ↻ replay
                </button>
              </div>
            </div>

            {/* Terminal body */}
            <div
              ref={terminalRef}
              className="p-4 h-[320px] overflow-y-auto font-mono text-sm space-y-1.5 scroll-smooth"
            >
              <AnimatePresence mode="sync">
                {scenario.messages.slice(0, visibleLines).map((msg, i) => (
                  <motion.div
                    key={`${scenario.id}-${i}`}
                    initial={{ opacity: 0, x: -10 }}
                    animate={{ opacity: 1, x: 0 }}
                    transition={{ duration: 0.3 }}
                    className={`flex items-start gap-2 ${
                      msg.role === "system"
                        ? "text-[#64748b]"
                        : msg.role === "user"
                        ? "text-blue-400"
                        : msg.role === "result"
                        ? "text-emerald-400 font-semibold mt-2 pt-2 border-t border-[#1e293b]"
                        : "text-orange-300"
                    }`}
                  >
                    <span className="text-[#475569] select-none shrink-0">
                      {msg.role === "result" ? ">>>" : "$"}
                    </span>
                    <span>{msg.text}</span>
                  </motion.div>
                ))}
              </AnimatePresence>

              {/* Blinking cursor */}
              {isPlaying && (
                <div className="flex items-center gap-2 text-[#475569]">
                  <span>$</span>
                  <span className="w-2 h-4 bg-orange-400 animate-pulse" />
                </div>
              )}
            </div>
          </div>
        </div>

        {/* Security Section */}
        <div className="max-w-5xl mx-auto">
          <div className="text-center mb-10">
            <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 text-xs font-medium mb-4">
              <Shield className="w-3.5 h-3.5" />
              Security-First Deployment
            </div>
            <h3 className="text-2xl font-bold text-[#f8fafc]">
              Your Data Never Leaves Your Infrastructure
            </h3>
            <p className="text-[#94a3b8] mt-2 max-w-2xl mx-auto">
              I deploy OpenClaw agents with enterprise-grade security practices — Docker isolation, encrypted credentials, audit logging, and zero third-party data exposure.
            </p>
          </div>

          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
            {securityFeatures.map((feature, i) => {
              const Icon = feature.icon;
              return (
                <motion.div
                  key={feature.title}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1 }}
                  className="group p-5 rounded-xl bg-[#12121a]/80 border border-[#1e293b] hover:border-emerald-500/30 transition-all duration-300"
                >
                  <div className="mb-3 inline-flex items-center justify-center w-10 h-10 rounded-lg bg-emerald-500/10 border border-emerald-500/20 text-emerald-400 group-hover:bg-emerald-500/20 transition-colors">
                    <Icon className="w-5 h-5" />
                  </div>
                  <h4 className="text-sm font-semibold text-[#f8fafc] mb-1">
                    {feature.title}
                  </h4>
                  <p className="text-xs text-[#94a3b8] leading-relaxed">
                    {feature.description}
                  </p>
                </motion.div>
              );
            })}
          </div>
        </div>
      </div>
    </section>
  );
}
