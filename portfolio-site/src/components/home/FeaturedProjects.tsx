"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import SectionHeading from "@/components/ui/SectionHeading";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import { projects } from "@/data/projects";

const typeColor: Record<string, "primary" | "blue" | "green" | "purple" | "orange"> = {
  n8n: "orange",
  python: "blue",
  hybrid: "purple",
};

const cardVariants = {
  hidden: { opacity: 0, y: 40 },
  visible: (i: number) => ({
    opacity: 1,
    y: 0,
    transition: {
      delay: i * 0.12,
      duration: 0.6,
      ease: [0.21, 0.47, 0.32, 0.98],
    },
  }),
};

export default function FeaturedProjects() {
  const featured = projects.filter((p) => p.featured);

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
            badge="Portfolio"
            title="Featured Projects"
            subtitle="Agentic AI systems and automation pipelines that drive measurable results across industries."
          />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {featured.map((project, i) => (
            <motion.div
              key={project.id}
              custom={i}
              variants={cardVariants}
              initial="hidden"
              whileInView="visible"
              viewport={{ once: true, margin: "-50px" }}
            >
              <Link href={`/projects/${project.slug}`} className="block h-full group">
                <div className="relative h-full overflow-hidden rounded-2xl border border-[#1a1a2e] transition-all duration-500 hover:border-cyan-500/30 hover:shadow-[0_0_40px_-10px_rgba(6,182,212,0.15)]">
                  {/* Animated gradient on hover */}
                  <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/0 via-transparent to-blue-500/0 group-hover:from-cyan-500/5 group-hover:to-blue-500/5 transition-all duration-700 pointer-events-none" />
                  <div className="absolute inset-[1px] bg-[#0a0a12]/95 rounded-2xl" />

                  {/* Content */}
                  <div className="relative p-7 flex flex-col h-full">
                    {/* Top row: badges + arrow */}
                    <div className="flex items-center justify-between mb-5">
                      <div className="flex items-center gap-2">
                        <Badge label={project.category} />
                        <Badge
                          label={project.type}
                          color={typeColor[project.type] ?? "primary"}
                        />
                      </div>
                      <div className="w-8 h-8 rounded-full border border-[#1a1a2e] flex items-center justify-center group-hover:border-cyan-500/30 group-hover:bg-cyan-500/10 transition-all duration-300">
                        <ArrowUpRight className="w-4 h-4 text-[#64748b] group-hover:text-cyan-400 transition-colors duration-300 group-hover:-translate-y-0.5 group-hover:translate-x-0.5" />
                      </div>
                    </div>

                    {/* Title */}
                    <h3 className="text-xl font-bold text-[#f8fafc] mb-2 group-hover:text-transparent group-hover:bg-gradient-to-r group-hover:from-cyan-400 group-hover:to-blue-400 group-hover:bg-clip-text transition-all duration-300">
                      {project.title}
                    </h3>

                    {/* Tagline */}
                    <p className="text-sm text-[#94a3b8] leading-relaxed mb-6 flex-1 line-clamp-3">
                      {project.tagline}
                    </p>

                    {/* Tool badges */}
                    <div className="flex flex-wrap gap-1.5">
                      {project.tools.map((tool) => (
                        <span
                          key={tool}
                          className="px-2.5 py-1 text-xs rounded-lg bg-white/[0.03] text-[#94a3b8] border border-[#1a1a2e] font-medium"
                        >
                          {tool}
                        </span>
                      ))}
                    </div>
                  </div>
                </div>
              </Link>
            </motion.div>
          ))}
        </div>

        <motion.div
          initial={{ opacity: 0, y: 20 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.4, duration: 0.5 }}
          className="mt-12 text-center"
        >
          <Button variant="secondary" size="lg" href="/projects">
            View All Projects
            <ArrowRight className="w-4 h-4" />
          </Button>
        </motion.div>
      </div>
    </section>
  );
}
