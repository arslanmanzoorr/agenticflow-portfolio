import type { Metadata } from "next";
import SectionHeading from "@/components/ui/SectionHeading";
import Timeline from "@/components/about/Timeline";
import SkillsGrid from "@/components/about/SkillsGrid";

export const metadata: Metadata = {
  title: "About | Arslan Manzoor",
  description:
    "Learn about Arslan Manzoor's journey from system administration to AI & automation engineering.",
};

export default function AboutPage() {
  return (
    <div className="min-h-screen pt-24">
      {/* Bio Section */}
      <section className="section-padding">
        <div className="container-custom">
          <SectionHeading
            badge="About Me"
            title="Building the Future of Automation"
            subtitle="From system administration to AI-powered workflow automation — here's my journey."
          />

          <div className="max-w-3xl mx-auto">
            <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-2xl p-8 md:p-10">
              <div className="space-y-4 text-text-secondary leading-relaxed">
                <p>
                  I&apos;m Arslan Manzoor — I started my career as a System
                  Administrator managing IT infrastructure and networking for
                  over 3 years, then progressed through IT support, business
                  development, and development management at KP LEADS LLC
                  where I led teams building web apps, custom CRMs, and API
                  integrations.
                </p>
                <p>
                  In 2023, I founded CallSolPK, building custom technology
                  solutions spanning Linux administration, Python, e-commerce,
                  and AI. That entrepreneurial experience shaped how I
                  approach every automation challenge today — with a founder&apos;s
                  mindset focused on ROI and scalability.
                </p>
                <p>
                  Now as an AI Automation Engineer and Specialist, I design
                  intelligent workflows using n8n, Python, Make.com, Zapier,
                  generative AI, and custom API integrations. My toolkit
                  connects disparate tools — whether it&apos;s syncing your
                  CRM with marketing platforms, building AI-powered lead
                  scoring, or creating self-healing data pipelines.
                </p>
                <p>
                  Every project I take on follows a simple philosophy:{" "}
                  <span className="text-primary font-medium">
                    automate what&apos;s repetitive, augment what&apos;s
                    creative, and measure what matters.
                  </span>
                </p>
              </div>
            </div>
          </div>

          {/* Independent AI Consultant Tile */}
          <div className="max-w-3xl mx-auto mt-8">
            <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500/10 to-blue-600/10 border border-cyan-500/20 p-8 md:p-10">
              <div className="absolute top-0 right-0 w-48 h-48 bg-cyan-500/5 rounded-full blur-[60px]" />
              <div className="relative flex flex-col sm:flex-row items-start sm:items-center gap-6">
                <div className="flex items-center justify-center w-16 h-16 rounded-xl bg-cyan-500/10 border border-cyan-500/20 shrink-0">
                  <svg className="w-8 h-8 text-cyan-400" fill="none" viewBox="0 0 24 24" stroke="currentColor" strokeWidth={1.5}>
                    <path strokeLinecap="round" strokeLinejoin="round" d="M9.813 15.904 9 18.75l-.813-2.846a4.5 4.5 0 0 0-3.09-3.09L2.25 12l2.846-.813a4.5 4.5 0 0 0 3.09-3.09L9 5.25l.813 2.846a4.5 4.5 0 0 0 3.09 3.09L15.75 12l-2.846.813a4.5 4.5 0 0 0-3.09 3.09ZM18.259 8.715 18 9.75l-.259-1.035a3.375 3.375 0 0 0-2.455-2.456L14.25 6l1.036-.259a3.375 3.375 0 0 0 2.455-2.456L18 2.25l.259 1.035a3.375 3.375 0 0 0 2.456 2.456L21.75 6l-1.035.259a3.375 3.375 0 0 0-2.456 2.456ZM16.894 20.567 16.5 21.75l-.394-1.183a2.25 2.25 0 0 0-1.423-1.423L13.5 18.75l1.183-.394a2.25 2.25 0 0 0 1.423-1.423l.394-1.183.394 1.183a2.25 2.25 0 0 0 1.423 1.423l1.183.394-1.183.394a2.25 2.25 0 0 0-1.423 1.423Z" />
                  </svg>
                </div>
                <div>
                  <div className="flex items-center gap-3 mb-2">
                    <h3 className="text-xl font-bold bg-gradient-to-r from-cyan-400 to-blue-500 bg-clip-text text-transparent">
                      Independent AI Consultant
                    </h3>
                    <span className="inline-flex items-center gap-1.5 px-2.5 py-0.5 text-xs font-medium rounded-full bg-emerald-500/10 border border-emerald-500/20 text-emerald-400">
                      <span className="relative flex h-1.5 w-1.5">
                        <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75" />
                        <span className="relative inline-flex h-1.5 w-1.5 rounded-full bg-emerald-400" />
                      </span>
                      Currently Active
                    </span>
                  </div>
                  <p className="text-text-secondary text-sm leading-relaxed">
                    Helping businesses deploy agentic AI systems, n8n workflow automation,
                    and custom Python integrations. Available for new projects and
                    long-term consulting engagements.
                  </p>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Experience Timeline */}
      <section className="section-padding bg-surface/30">
        <div className="container-custom">
          <SectionHeading
            badge="Experience"
            title="My Journey"
            subtitle="From system administration to AI automation engineering."
          />
          <div className="max-w-4xl mx-auto">
            <Timeline />
          </div>
        </div>
      </section>

      {/* Skills */}
      <section className="section-padding">
        <div className="container-custom">
          <SectionHeading
            badge="Skills"
            title="Tools & Technologies"
            subtitle="The platforms and technologies I work with daily."
          />
          <div className="max-w-4xl mx-auto">
            <SkillsGrid />
          </div>
        </div>
      </section>
    </div>
  );
}
