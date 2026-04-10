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

// Grid placement for each service card on desktop (lg)
const gridPlacements: Record<
  number,
  { colSpan: string; rowSpan: string; lgColSpan: string; lgRowSpan: string }
> = {
  0: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-2",
    lgRowSpan: "lg:row-span-2",
  },
  1: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-1",
    lgRowSpan: "",
  },
  2: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-1",
    lgRowSpan: "",
  },
  3: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-1",
    lgRowSpan: "",
  },
  4: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-1",
    lgRowSpan: "",
  },
  5: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-1",
    lgRowSpan: "",
  },
  6: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-1",
    lgRowSpan: "",
  },
  7: {
    colSpan: "md:col-span-1",
    rowSpan: "",
    lgColSpan: "lg:col-span-2",
    lgRowSpan: "",
  },
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
            title="What I Build"
            subtitle="Intelligent automation systems that think, act, and scale."
          />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
          {services.map((service, i) => {
            const Icon = iconMap[service.icon] || Bot;
            const isOpenClaw = service.icon === "Lobster";
            const placement = gridPlacements[i];

            return (
              <motion.div
                key={service.title}
                initial={{ opacity: 0, y: 30 }}
                whileInView={{ opacity: 1, y: 0 }}
                viewport={{ once: true }}
                transition={{
                  delay: i * 0.06,
                  duration: 0.5,
                  ease: [0.21, 0.47, 0.32, 0.98],
                }}
                className={`${placement.colSpan} ${placement.rowSpan} ${placement.lgColSpan} ${placement.lgRowSpan}`}
              >
                <div
                  className={`relative h-full group cursor-pointer overflow-hidden rounded-2xl border transition-all duration-500 bg-[#0a0a14]/80 backdrop-blur-sm ${
                    isOpenClaw
                      ? "border-[#1a1a2e] hover:border-orange-500/30 hover:shadow-[0_0_40px_-12px_rgba(249,115,22,0.2)]"
                      : "border-[#1a1a2e] hover:border-cyan-500/20 hover:shadow-[0_0_40px_-12px_rgba(6,182,212,0.15)]"
                  } ${isOpenClaw ? "p-8" : "p-6"}`}
                >
                  {/* HOT badge for OpenClaw */}
                  {isOpenClaw && (
                    <span className="absolute top-3 right-3 px-2.5 py-0.5 text-[10px] font-bold uppercase bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-full">
                      HOT
                    </span>
                  )}

                  {/* Icon */}
                  <div
                    className={`inline-flex items-center justify-center rounded-xl border transition-transform duration-300 group-hover:scale-110 ${
                      isOpenClaw
                        ? "w-12 h-12 bg-orange-500/10 border-orange-500/20"
                        : "w-11 h-11 bg-cyan-500/10 border-cyan-500/20"
                    }`}
                  >
                    <Icon
                      className={`${isOpenClaw ? "w-6 h-6 text-orange-400" : "w-5 h-5 text-cyan-400"}`}
                    />
                  </div>

                  {/* Title */}
                  <h3
                    className={`font-semibold text-[#f8fafc] mt-4 mb-2 ${
                      isOpenClaw ? "text-xl" : "text-lg"
                    }`}
                  >
                    {service.title}
                  </h3>

                  {/* Description */}
                  <p
                    className={`text-[#64748b] leading-relaxed ${
                      isOpenClaw ? "text-base" : "text-sm"
                    }`}
                  >
                    {service.description}
                  </p>

                  {/* Decorative gradient line for OpenClaw featured card */}
                  {isOpenClaw && (
                    <div className="absolute bottom-0 left-0 right-0 h-[2px] bg-gradient-to-r from-transparent via-orange-500/40 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500" />
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </section>
  );
}
