import {
  Bot,
  Workflow,
  Code,
  Sparkles,
  TrendingUp,
  Terminal,
  Mail,
  Users,
  Shell,
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
  Mail,
  Users,
  Lobster: Shell,
};

export default function ServicesGrid() {
  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <SectionHeading
          badge="Services"
          title="What I Do"
          subtitle="From OpenClaw agent deployments to fully automated pipelines — I build AI systems that think, act, and scale while you sleep."
        />

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          {services.map((service, i) => {
            const Icon = iconMap[service.icon] || Bot;
            const isOpenClaw = service.icon === "Lobster";
            return (
              <ScrollReveal key={service.title} delay={i * 0.08}>
                <Card className={`h-full group ${isOpenClaw ? "relative overflow-hidden border-orange-500/30 hover:border-orange-400/50" : ""}`}>
                  {isOpenClaw && (
                    <div className="absolute top-0 right-0 px-2 py-0.5 text-[10px] font-bold uppercase tracking-wider bg-gradient-to-r from-orange-500 to-red-500 text-white rounded-bl-lg">
                      Hot
                    </div>
                  )}
                  <div className={`mb-4 inline-flex items-center justify-center w-12 h-12 rounded-lg border transition-colors duration-300 ${
                    isOpenClaw
                      ? "bg-orange-500/10 border-orange-500/20 text-orange-400 group-hover:bg-orange-500/20"
                      : "bg-cyan-500/10 border-cyan-500/20 text-cyan-400 group-hover:bg-cyan-500/20"
                  }`}>
                    {isOpenClaw ? (
                      <span className="text-2xl">🦞</span>
                    ) : (
                      <Icon className="w-6 h-6" />
                    )}
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
