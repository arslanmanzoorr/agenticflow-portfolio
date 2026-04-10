"use client";

import Link from "next/link";
import { motion } from "framer-motion";
import SectionHeading from "@/components/ui/SectionHeading";
import { ArrowRight, ArrowUpRight } from "lucide-react";
import { projects } from "@/data/projects";

const gradientMap: Record<string, string> = {
  n8n: "from-orange-500/20 to-amber-500/10",
  python: "from-blue-500/20 to-indigo-500/10",
  hybrid: "from-violet-500/20 to-purple-500/10",
};

export default function FeaturedProjects() {
  const featured = projects.filter((p) => p.featured);

  return (
    <section className="py-24">
      <style>{`
        .scrollbar-hide::-webkit-scrollbar { display: none; }
        .scrollbar-hide { -ms-overflow-style: none; scrollbar-width: none; }
      `}</style>

      <div className="max-w-7xl mx-auto px-6">
        <SectionHeading
          badge="Portfolio"
          title="Selected Work"
          subtitle="Agentic AI systems and automation pipelines that drive measurable results across industries."
        />
      </div>

      <div className="scrollbar-hide overflow-x-auto snap-x snap-mandatory mt-12">
        <div className="flex gap-6 px-6 lg:px-[calc((100vw-1280px)/2+24px)]">
          {featured.map((project, i) => (
            <motion.div
              key={project.id}
              initial={{ opacity: 0, x: 40 }}
              whileInView={{ opacity: 1, x: 0 }}
              viewport={{ once: true, margin: "-100px" }}
              transition={{
                delay: i * 0.1,
                duration: 0.6,
                ease: [0.21, 0.47, 0.32, 0.98],
              }}
              className="w-[340px] sm:w-[400px] flex-shrink-0 snap-center"
            >
              <Link
                href={`/projects/${project.slug}`}
                className="block group cursor-pointer"
              >
                <div className="rounded-2xl overflow-hidden bg-[#0a0a14]/90 border border-[#1a1a2e] hover:border-cyan-500/20 transition-all duration-500 hover:shadow-[0_8px_40px_-12px_rgba(6,182,212,0.2)] group-hover:-translate-y-1">
                  {/* Top section */}
                  <div className="h-48 relative overflow-hidden">
                    <div
                      className={`absolute inset-0 bg-gradient-to-br ${
                        gradientMap[project.type] || "from-cyan-500/20 to-blue-500/10"
                      }`}
                    />
                    <span className="absolute top-4 left-5 text-6xl font-black text-white/[0.06] tracking-tighter select-none">
                      {String(i + 1).padStart(2, "0")}
                    </span>
                    <span className="absolute bottom-4 left-5 px-2.5 py-1 text-xs font-medium rounded-md bg-white/[0.08] text-[#94a3b8] border border-white/[0.06]">
                      {project.category}
                    </span>
                    <div className="absolute top-4 right-4 w-8 h-8 rounded-full border border-white/10 flex items-center justify-center">
                      <ArrowUpRight className="w-4 h-4 text-[#64748b] transition-transform duration-300 group-hover:rotate-45" />
                    </div>
                  </div>

                  {/* Bottom section */}
                  <div className="p-5">
                    <h3 className="text-xl font-bold text-[#f8fafc] mb-2">
                      {project.title}
                    </h3>
                    <p className="text-sm text-[#64748b] line-clamp-2 mb-4">
                      {project.tagline}
                    </p>
                    <div className="flex flex-wrap gap-1.5">
                      {project.tools.map((tool) => (
                        <span
                          key={tool}
                          className="px-2 py-0.5 text-[11px] rounded-md bg-white/[0.04] text-[#94a3b8] border border-[#1e293b]"
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
      </div>

      <div className="max-w-7xl mx-auto px-6 mt-12 text-center">
        <Link
          href="/projects"
          className="cursor-pointer inline-flex items-center gap-2 text-sm font-medium text-[#94a3b8] hover:text-[#f8fafc] transition-colors border border-[#1e293b] hover:border-[#94a3b8] rounded-full px-6 py-3"
        >
          View All Projects
          <ArrowRight className="w-4 h-4" />
        </Link>
      </div>
    </section>
  );
}
