"use client";

import { motion } from "framer-motion";
import AnimatedCounter from "@/components/ui/AnimatedCounter";

const stats = [
  { target: 50, suffix: "+", label: "Workflows Built", icon: "W" },
  { target: 20, suffix: "+", label: "Happy Clients", icon: "C" },
  { target: 10000, suffix: "+", label: "Hours Saved", icon: "H" },
  { target: 98, suffix: "%", label: "Client Satisfaction", icon: "S" },
];

export default function StatsBar() {
  return (
    <section className="relative py-20">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 40 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true, margin: "-100px" }}
          transition={{ duration: 0.6, ease: [0.21, 0.47, 0.32, 0.98] }}
        >
          <div className="relative overflow-hidden rounded-2xl border border-[#1a1a2e]">
            {/* Gradient border glow */}
            <div className="absolute inset-0 bg-gradient-to-r from-cyan-500/10 via-transparent to-blue-500/10 pointer-events-none" />
            <div className="absolute inset-[1px] bg-[#0a0a12]/95 backdrop-blur-xl rounded-2xl" />

            <div className="relative grid grid-cols-2 md:grid-cols-4 gap-0">
              {stats.map((stat, i) => (
                <motion.div
                  key={i}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  viewport={{ once: true }}
                  transition={{ delay: i * 0.1, duration: 0.5 }}
                  className={`relative p-8 sm:p-10 text-center group ${
                    i < stats.length - 1 ? "md:border-r border-[#1a1a2e]" : ""
                  } ${i < 2 ? "border-b md:border-b-0 border-[#1a1a2e]" : ""}`}
                >
                  {/* Hover glow */}
                  <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/0 to-cyan-500/0 group-hover:from-cyan-500/5 group-hover:to-transparent transition-all duration-500 pointer-events-none" />

                  <div className="relative">
                    <div className="text-4xl sm:text-5xl font-bold bg-gradient-to-b from-[#f8fafc] to-[#94a3b8] bg-clip-text text-transparent tabular-nums">
                      <AnimatedCounter
                        target={stat.target}
                        suffix={stat.suffix}
                      />
                    </div>
                    <p className="mt-3 text-sm font-medium text-[#64748b] uppercase tracking-wider">
                      {stat.label}
                    </p>
                  </div>
                </motion.div>
              ))}
            </div>
          </div>
        </motion.div>
      </div>
    </section>
  );
}
