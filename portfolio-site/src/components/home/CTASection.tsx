"use client";

import { motion } from "framer-motion";
import Button from "@/components/ui/Button";
import { ArrowRight, Zap } from "lucide-react";

export default function CTASection() {
  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.7, ease: [0.21, 0.47, 0.32, 0.98] }}
        >
          <div className="relative overflow-hidden rounded-3xl">
            {/* Animated gradient background */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-600 via-blue-600 to-indigo-700" />
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.03)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.03)_1px,transparent_1px)] bg-[size:32px_32px]" />

            {/* Animated orbs */}
            <motion.div
              animate={{
                x: [0, 30, -20, 0],
                y: [0, -20, 30, 0],
                scale: [1, 1.2, 0.9, 1],
              }}
              transition={{ duration: 8, repeat: Infinity, ease: "easeInOut" }}
              className="absolute top-0 right-0 w-80 h-80 bg-white/10 rounded-full blur-[100px]"
            />
            <motion.div
              animate={{
                x: [0, -30, 20, 0],
                y: [0, 20, -30, 0],
                scale: [1, 0.9, 1.2, 1],
              }}
              transition={{ duration: 10, repeat: Infinity, ease: "easeInOut" }}
              className="absolute bottom-0 left-0 w-80 h-80 bg-indigo-500/30 rounded-full blur-[100px]"
            />

            <div className="relative z-10 px-8 py-16 sm:px-16 sm:py-20 text-center">
              <motion.div
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                viewport={{ once: true }}
                transition={{ delay: 0.2, duration: 0.5 }}
                className="inline-flex items-center gap-2 px-4 py-1.5 rounded-full bg-white/10 border border-white/20 text-white/90 text-sm font-medium mb-8 backdrop-blur-sm"
              >
                <Zap className="w-4 h-4" />
                Ready to automate?
              </motion.div>

              <motion.h2
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.3, duration: 0.6 }}
                className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white leading-tight"
              >
                Let&apos;s Deploy Your
                <br />
                <span className="text-white/90">AI Agents Today</span>
              </motion.h2>

              <motion.p
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.4, duration: 0.6 }}
                className="mt-6 text-lg text-white/70 max-w-2xl mx-auto leading-relaxed"
              >
                From OpenClaw agents to n8n pipelines — I build agentic
                workflows that think, decide, and execute, saving your team
                20+ hours every week.
              </motion.p>

              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{ delay: 0.5, duration: 0.6 }}
                className="mt-10 flex flex-wrap justify-center gap-4"
              >
                <Button
                  href="/contact"
                  size="lg"
                  className="bg-white text-gray-900 shadow-lg shadow-black/20 hover:bg-white/90 hover:shadow-xl border-0 hover:brightness-100 font-semibold"
                >
                  Schedule a Call
                  <ArrowRight className="w-4 h-4" />
                </Button>
                <Button
                  href="/projects"
                  size="lg"
                  className="bg-transparent border border-white/25 text-white hover:bg-white/10 hover:border-white/40 shadow-none backdrop-blur-sm"
                >
                  View Projects
                </Button>
              </motion.div>
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
