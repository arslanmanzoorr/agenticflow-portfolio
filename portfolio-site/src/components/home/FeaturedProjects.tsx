import Link from "next/link";
import Card from "@/components/ui/Card";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import SectionHeading from "@/components/ui/SectionHeading";
import ScrollReveal from "@/components/ui/ScrollReveal";
import { ArrowRight } from "lucide-react";
import { projects } from "@/data/projects";

const typeColor: Record<string, "primary" | "blue" | "green" | "purple" | "orange"> = {
  n8n: "primary",
  python: "blue",
  hybrid: "purple",
};

export default function FeaturedProjects() {
  const featured = projects.filter((p) => p.featured);

  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          badge="Portfolio"
          title="Featured Projects"
          subtitle="Agentic AI systems and automation pipelines that drive measurable results across industries."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {featured.map((project, i) => (
            <ScrollReveal key={project.id} delay={i * 0.1}>
              <Link href={`/projects/${project.slug}`} className="block h-full">
                <Card className="h-full flex flex-col group">
                  {/* Category & type */}
                  <div className="flex items-center gap-2 mb-4">
                    <Badge label={project.category} />
                    <Badge
                      label={project.type}
                      color={typeColor[project.type] ?? "primary"}
                    />
                  </div>

                  {/* Title */}
                  <h3 className="text-xl font-semibold text-[#f8fafc] mb-2 group-hover:text-cyan-400 transition-colors">
                    {project.title}
                  </h3>

                  {/* Tagline */}
                  <p className="text-sm text-[#94a3b8] leading-relaxed mb-5 flex-1">
                    {project.tagline}
                  </p>

                  {/* Tool badges */}
                  <div className="flex flex-wrap gap-1.5 mb-5">
                    {project.tools.map((tool) => (
                      <span
                        key={tool}
                        className="px-2 py-0.5 text-xs rounded-md bg-white/5 text-[#94a3b8] border border-[#1a1a2e]"
                      >
                        {tool}
                      </span>
                    ))}
                  </div>

                  {/* View link */}
                  <div className="flex items-center text-sm font-medium text-cyan-400 group-hover:gap-2 gap-1 transition-all">
                    View Project
                    <ArrowRight className="w-4 h-4" />
                  </div>
                </Card>
              </Link>
            </ScrollReveal>
          ))}
        </div>

        <div className="mt-12 text-center">
          <Button variant="secondary" size="lg" href="/projects">
            View All Projects
            <ArrowRight className="w-4 h-4" />
          </Button>
        </div>
      </div>
    </section>
  );
}
