"use client";

import { tools } from "@/data/tools";
import ScrollReveal from "@/components/ui/ScrollReveal";

const categoryColors: Record<string, string> = {
  Automation: "from-orange-500/20 to-orange-500/5 border-orange-500/20 text-orange-400",
  Programming: "from-blue-500/20 to-blue-500/5 border-blue-500/20 text-blue-400",
  Database: "from-emerald-500/20 to-emerald-500/5 border-emerald-500/20 text-emerald-400",
  AI: "from-purple-500/20 to-purple-500/5 border-purple-500/20 text-purple-400",
  CRM: "from-cyan-500/20 to-cyan-500/5 border-cyan-500/20 text-cyan-400",
  Communication: "from-pink-500/20 to-pink-500/5 border-pink-500/20 text-pink-400",
  Infrastructure: "from-slate-500/20 to-slate-500/5 border-slate-500/20 text-slate-400",
};

export default function SkillsGrid() {
  const grouped = tools.reduce(
    (acc, tool) => {
      if (!acc[tool.category]) acc[tool.category] = [];
      acc[tool.category].push(tool.name);
      return acc;
    },
    {} as Record<string, string[]>
  );

  return (
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-6">
      {Object.entries(grouped).map(([category, toolNames], index) => (
        <ScrollReveal key={category} delay={index * 0.1}>
          <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-xl p-6 hover:border-primary/30 transition-colors">
            <h3 className="text-sm font-semibold text-text-secondary uppercase tracking-wider mb-4">
              {category}
            </h3>
            <div className="flex flex-wrap gap-2">
              {toolNames.map((name) => (
                <span
                  key={name}
                  className={`inline-flex items-center px-3 py-1.5 text-sm font-medium rounded-lg border bg-gradient-to-br ${
                    categoryColors[category] || categoryColors.Infrastructure
                  }`}
                >
                  {name}
                </span>
              ))}
            </div>
          </div>
        </ScrollReveal>
      ))}
    </div>
  );
}
