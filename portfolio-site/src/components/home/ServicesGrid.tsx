"use client";

import { motion } from "framer-motion";
import {
  Bot,
  Workflow,
  Code,
  Sparkles,
  Terminal,
  Mail,
  Users,
  Shell,
  type LucideIcon,
} from "lucide-react";
import SectionHeading from "@/components/ui/SectionHeading";
import { services } from "@/data/services";

const iconMap: Record<string, LucideIcon> = {
  Bot,
  Workflow,
  Code,
  Sparkles,
  Terminal,
  Mail,
  Users,
  Lobster: Shell,
};

const cardVariants = {
  hidden: { opacity: 0, y: 30 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.08,
      duration: 0.5,
      ease: [0.21, 0.47, 0.32, 0.98],
    },
  }),
};

export default function ServicesGrid() {
  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <SectionHeading
            badge="Services"
            title="What I Do"
            subtitle="From OpenClaw agent deployments to fully automated pipelines — I build AI systems that think, act, and scale while you sleep."
          />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {services.map((service, i) => {
            const Icon = iconMap[service.icon] || Bot;
            const isOpenClaw = service.icon === "Lobster";

            return (
              <motion.div
                key={service.title}
                custom={i}
                variants={cardVariants}
                initial="hidden"
                whileInView="visible"
                viewport={{ once: true, margin: "-50px" }}
              >
                <div
                  className={`relative h-full group cursor-pointer overflow-hidden rounded-xl border transition-all duration-500 ${
                    isOpenClaw
                      ? "border-orange-500/20 hover:border-orange-400/40 hover:shadow-[0_0_30px_-8px_rgba(249,115,22,0.15)]"
                      : "border-[#1a1a2e] hover:border-cyan-500/30 hover:shadow-[0_0_30px_-8px_rgba(6,182,212,0.1)]"
                  }`}
                >
                  {/* Gradient hover background */}
                  <div
                    className={`absolute inset-0 transition-all duration-700 pointer-events-none ${
                      isOpenClaw
                        ? "bg-gradient-to-b from-orange-500/0 to-orange-500/0 group-hover:from-orange-500/5 group-hover:to-transparent"
                        : "bg-gradient-to-b from-cyan-500/0 to-cyan-500/0 group-hover:from-cyan-500/5 group-hover:to-transparent"
                    }`}
                  />
                  <div className="absolute inset-[1px] bg-[#0a0a12]/95 rounded-xl" />

                  {/* Hot badge */}
                  {isOpenClaw && (
                    <div className="absolute top-0 right-0 px-2.5 py-1 text-[10px] font-bold uppercase tracking-wider bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-bl-xl z-10">
                      Hot
                    </div>
                  )}

                  {/* Content */}
                  <div className="relative p-6">
                    <div
                      className={`mb-4 inline-flex items-center justify-center w-11 h-11 rounded-lg border transition-all duration-300 ${
                        isOpenClaw
                          ? "bg-orange-500/10 border-orange-500/20 group-hover:bg-orange-500/20 group-hover:scale-110"
                          : "bg-cyan-500/10 border-cyan-500/20 group-hover:bg-cyan-500/20 group-hover:scale-110"
                      }`}
                    >
                      <Icon
                        className={`w-5 h-5 ${
                          isOpenClaw ? "text-orange-400" : "text-cyan-400"
                        }`}
                      />
                    </div>

                    <h3 className="text-base font-semibold text-[#f8fafc] mb-2">
                      {service.title}
                    </h3>

                    <p className="text-sm text-[#64748b] leading-relaxed">
                      {service.description}
                    </p>
                  </div>
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
