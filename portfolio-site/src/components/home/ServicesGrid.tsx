import {
  Bot,
  Workflow,
  Code,
  Sparkles,
  TrendingUp,
  Terminal,
  type LucideIcon,
} from "lucide-react";
import Card from "@/components/ui/Card";
import SectionHeading from "@/components/ui/SectionHeading";
import ScrollReveal from "@/components/ui/ScrollReveal";
import { services } from "@/data/services";

const iconMap: Record<string, LucideIcon> = {
  Bot,
  Workflow,
  Code,
  Sparkles,
  TrendingUp,
  Terminal,
};

export default function ServicesGrid() {
  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          badge="Services"
          title="What I Do"
          subtitle="From agentic AI systems to fully automated pipelines — I build solutions that think, act, and scale while you sleep."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {services.map((service, i) => {
            const Icon = iconMap[service.icon] || Bot;
            return (
              <ScrollReveal key={service.title} delay={i * 0.1}>
                <Card className="h-full group">
                  <div className="mb-4 inline-flex items-center justify-center w-12 h-12 rounded-lg bg-cyan-500/10 border border-cyan-500/20 text-cyan-400 transition-colors duration-300 group-hover:bg-cyan-500/20">
                    <Icon className="w-6 h-6" />
                  </div>
                  <h3 className="text-lg font-semibold text-[#f8fafc] mb-2">
                    {service.title}
                  </h3>
                  <p className="text-sm text-[#94a3b8] leading-relaxed">
                    {service.description}
                  </p>
                </Card>
              </ScrollReveal>
            );
          })}
        </div>
      </div>
    </section>
  );
}
