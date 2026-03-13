import Link from "next/link";
import { ArrowRight } from "lucide-react";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import ToolBadge from "./ToolBadge";
import type { Project } from "@/types";

interface ProjectCardProps {
  project: Project;
}

const categoryColor: Record<string, "primary" | "blue" | "green" | "purple" | "orange"> = {
  "Lead Generation": "orange",
  "AI/ML": "primary",
  "E-commerce": "green",
  CRM: "blue",
  Data: "purple",
  HR: "orange",
};

export default function ProjectCard({ project }: ProjectCardProps) {
  const maxVisible = 4;
  const visibleTools = project.tools.slice(0, maxVisible);
  const remaining = project.tools.length - maxVisible;

  return (
    <Link href={`/projects/${project.slug}`} className="group block">
      <Card className="h-full flex flex-col transition-all duration-300 group-hover:-translate-y-1.5 group-hover:border-[#06b6d4]/40 group-hover:shadow-xl group-hover:shadow-cyan-500/10">
        <div className="flex items-center justify-between mb-4">
          <Badge
            label={project.category}
            color={categoryColor[project.category] || "primary"}
          />
          {project.featured && (
            <span className="text-[10px] font-medium uppercase tracking-wider text-cyan-400">
              Featured
            </span>
          )}
        </div>

        <h3 className="text-xl font-bold text-[#f8fafc] mb-2 group-hover:text-cyan-400 transition-colors duration-200">
          {project.title}
        </h3>

        <p className="text-[#94a3b8] text-sm leading-relaxed mb-5 flex-1 line-clamp-3">
          {project.tagline}
        </p>

        <div className="flex flex-wrap items-center gap-1.5 mb-5">
          {visibleTools.map((tool) => (
            <ToolBadge key={tool} name={tool} size="sm" />
          ))}
          {remaining > 0 && (
            <span className="text-[10px] text-[#64748b] font-medium px-2 py-0.5 rounded-full border border-[#1a1a2e]">
              +{remaining} more
            </span>
          )}
        </div>

        <div className="flex items-center text-sm font-medium text-[#06b6d4] group-hover:text-cyan-300 transition-colors duration-200">
          View Project
          <ArrowRight className="ml-1.5 h-4 w-4 transition-transform duration-200 group-hover:translate-x-1" />
        </div>
      </Card>
    </Link>
  );
}
