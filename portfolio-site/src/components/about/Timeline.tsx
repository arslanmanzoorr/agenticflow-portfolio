"use client";

import { experience } from "@/data/experience";
import ScrollReveal from "@/components/ui/ScrollReveal";
import { Briefcase } from "lucide-react";

export default function Timeline() {
  return (
    <div className="relative">
      {/* Vertical line */}
      <div className="absolute left-4 md:left-1/2 md:-translate-x-px top-0 bottom-0 w-0.5 bg-gradient-to-b from-cyan-500 via-blue-500 to-transparent" />

      <div className="space-y-12">
        {experience.map((exp, index) => (
          <ScrollReveal
            key={index}
            direction={index % 2 === 0 ? "left" : "right"}
            delay={index * 0.15}
          >
            <div
              className={`relative flex items-start gap-8 ${
                index % 2 === 0
                  ? "md:flex-row"
                  : "md:flex-row-reverse md:text-right"
              }`}
            >
              {/* Dot */}
              <div className="absolute left-4 md:left-1/2 -translate-x-1/2 w-8 h-8 rounded-full bg-surface border-2 border-cyan-500 flex items-center justify-center z-10">
                <Briefcase className="w-3.5 h-3.5 text-cyan-400" />
              </div>

              {/* Content */}
              <div
                className={`ml-16 md:ml-0 md:w-[calc(50%-2rem)] ${
                  index % 2 === 0 ? "md:pr-8" : "md:pl-8"
                }`}
              >
                <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-xl p-6 hover:border-primary/30 transition-colors">
                  <span className="inline-block px-3 py-1 text-xs font-medium text-cyan-400 bg-cyan-500/10 rounded-full mb-3">
                    {exp.period}
                  </span>
                  <h3 className="text-lg font-semibold text-text-primary">
                    {exp.title}
                  </h3>
                  <p className="text-primary text-sm font-medium mt-1">
                    {exp.company}
                  </p>
                  <p className="text-text-secondary text-sm mt-3 leading-relaxed">
                    {exp.description}
                  </p>
                </div>
              </div>
            </div>
          </ScrollReveal>
        ))}
      </div>
    </div>
  );
}
