import { notFound } from "next/navigation";
import { Metadata } from "next";
import Link from "next/link";
import {
  ArrowLeft,
  ChevronRight,
  CheckCircle2,
  Github,
  ArrowRight,
  Workflow,
  Code2,
  Layers,
} from "lucide-react";
import Badge from "@/components/ui/Badge";
import Button from "@/components/ui/Button";
import Card from "@/components/ui/Card";
import ScrollReveal from "@/components/ui/ScrollReveal";
import ToolBadge from "@/components/projects/ToolBadge";
import { projects } from "@/data/projects";

interface PageProps {
  params: { slug: string };
}

export function generateStaticParams() {
  return projects.map((project) => ({
    slug: project.slug,
  }));
}

export function generateMetadata({ params }: PageProps): Metadata {
  const project = projects.find((p) => p.slug === params.slug);
  if (!project) return { title: "Project Not Found" };

  return {
    title: `${project.title} | Arslan - Automation Engineer`,
    description: project.tagline,
  };
}

const typeConfig = {
  n8n: { label: "n8n Workflow", color: "orange" as const, Icon: Workflow },
  python: { label: "Python App", color: "blue" as const, Icon: Code2 },
  hybrid: { label: "Hybrid System", color: "purple" as const, Icon: Layers },
};

const categoryColor: Record<string, "primary" | "blue" | "green" | "purple" | "orange"> = {
  "Lead Generation": "orange",
  "AI/ML": "primary",
  "E-commerce": "green",
  CRM: "blue",
  Data: "purple",
  HR: "orange",
};

export default function ProjectDetailPage({ params }: PageProps) {
  const project = projects.find((p) => p.slug === params.slug);

  if (!project) {
    notFound();
  }

  const typeInfo = typeConfig[project.type];

  return (
    <main className="min-h-screen bg-[#0a0a0f]">
      {/* Hero */}
      <section className="relative pt-28 pb-16 overflow-hidden">
        <div className="absolute inset-0 bg-gradient-to-b from-cyan-500/5 via-blue-500/5 to-transparent" />
        <div className="absolute top-0 left-0 right-0 h-1 bg-gradient-to-r from-cyan-500 to-blue-500" />

        <div className="relative max-w-4xl mx-auto px-4">
          {/* Breadcrumb */}
          <ScrollReveal>
            <nav className="flex items-center gap-2 text-sm text-[#64748b] mb-8">
              <Link
                href="/projects"
                className="hover:text-cyan-400 transition-colors"
              >
                Projects
              </Link>
              <ChevronRight className="h-3.5 w-3.5" />
              <span className="text-[#94a3b8]">{project.title}</span>
            </nav>
          </ScrollReveal>

          <ScrollReveal>
            <div className="flex flex-wrap items-center gap-3 mb-5">
              <Badge
                label={project.category}
                color={categoryColor[project.category] || "primary"}
              />
              <Badge label={typeInfo.label} color={typeInfo.color} />
            </div>
          </ScrollReveal>

          <ScrollReveal delay={0.1}>
            <h1 className="text-4xl sm:text-5xl lg:text-6xl font-bold text-[#f8fafc] mb-4">
              {project.title}
            </h1>
          </ScrollReveal>

          <ScrollReveal delay={0.15}>
            <p className="text-lg sm:text-xl text-[#94a3b8] leading-relaxed mb-8 max-w-3xl">
              {project.tagline}
            </p>
          </ScrollReveal>

          <ScrollReveal delay={0.2}>
            <div className="flex flex-wrap gap-2">
              {project.tools.map((tool) => (
                <ToolBadge key={tool} name={tool} size="md" />
              ))}
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* Problem */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <Card hover={false} className="p-8 border-red-500/20">
              <h2 className="text-2xl font-bold text-[#f8fafc] mb-4 flex items-center gap-3">
                <span className="w-10 h-10 rounded-lg bg-red-500/10 flex items-center justify-center text-red-400 text-lg">
                  !
                </span>
                The Problem
              </h2>
              <p className="text-[#94a3b8] leading-relaxed text-lg">
                {project.problem}
              </p>
            </Card>
          </ScrollReveal>
        </div>
      </section>

      {/* Solution */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <Card hover={false} className="p-8 border-emerald-500/20">
              <h2 className="text-2xl font-bold text-[#f8fafc] mb-4 flex items-center gap-3">
                <span className="w-10 h-10 rounded-lg bg-emerald-500/10 flex items-center justify-center text-emerald-400 text-lg">
                  &#10003;
                </span>
                The Solution
              </h2>
              <p className="text-[#94a3b8] leading-relaxed text-lg">
                {project.solution}
              </p>
            </Card>
          </ScrollReveal>
        </div>
      </section>

      {/* Architecture */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#f8fafc] mb-10 text-center">
              How It Works
            </h2>
          </ScrollReveal>

          <div className="relative">
            {/* Vertical line */}
            <div className="absolute left-6 top-0 bottom-0 w-px bg-gradient-to-b from-cyan-500/50 via-blue-500/50 to-transparent hidden sm:block" />

            <div className="space-y-6">
              {project.architecture.map((step, index) => (
                <ScrollReveal key={index} delay={index * 0.1}>
                  <div className="flex items-start gap-5">
                    <div className="relative z-10 shrink-0 w-12 h-12 rounded-full bg-[#12121a] border-2 border-cyan-500/40 flex items-center justify-center">
                      <span className="text-sm font-bold text-cyan-400">
                        {index + 1}
                      </span>
                    </div>
                    <Card hover={false} className="flex-1 p-5">
                      <p className="text-[#e2e8f0] leading-relaxed">{step}</p>
                    </Card>
                  </div>
                </ScrollReveal>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Features */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#f8fafc] mb-10 text-center">
              Key Features
            </h2>
          </ScrollReveal>

          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            {project.features.map((feature, index) => (
              <ScrollReveal key={index} delay={index * 0.05}>
                <Card hover={false} className="p-5 flex items-start gap-3">
                  <CheckCircle2 className="h-5 w-5 text-cyan-400 shrink-0 mt-0.5" />
                  <p className="text-[#e2e8f0] text-sm leading-relaxed">
                    {feature}
                  </p>
                </Card>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </section>

      {/* Tech Stack */}
      <section className="py-16 px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <h2 className="text-2xl sm:text-3xl font-bold text-[#f8fafc] mb-8 text-center">
              Tech Stack
            </h2>
          </ScrollReveal>

          <ScrollReveal delay={0.1}>
            <div className="flex flex-wrap justify-center gap-3">
              {project.tools.map((tool) => (
                <ToolBadge key={tool} name={tool} size="md" />
              ))}
            </div>
          </ScrollReveal>
        </div>
      </section>

      {/* CTA */}
      <section className="py-20 px-4">
        <div className="max-w-4xl mx-auto">
          <ScrollReveal>
            <Card hover={false} className="p-10 text-center border-[#06b6d4]/20">
              <h2 className="text-2xl sm:text-3xl font-bold text-[#f8fafc] mb-4">
                Want to see more?
              </h2>
              <p className="text-[#94a3b8] mb-8 max-w-lg mx-auto">
                Check out the source code on GitHub or browse other projects in
                my portfolio.
              </p>
              <div className="flex flex-wrap items-center justify-center gap-4">
                {project.github && (
                  <Button
                    variant="primary"
                    size="lg"
                    href={project.github}
                    target="_blank"
                    rel="noopener noreferrer"
                  >
                    <Github className="h-5 w-5" />
                    View on GitHub
                  </Button>
                )}
                <Button variant="secondary" size="lg" href="/projects">
                  <ArrowLeft className="h-5 w-5" />
                  All Projects
                </Button>
              </div>
            </Card>
          </ScrollReveal>
        </div>
      </section>
    </main>
  );
}
