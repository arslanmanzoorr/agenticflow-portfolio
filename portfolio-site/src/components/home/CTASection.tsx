import Button from "@/components/ui/Button";
import ScrollReveal from "@/components/ui/ScrollReveal";
import { ArrowRight } from "lucide-react";

export default function CTASection() {
  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal>
          <div className="relative overflow-hidden rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-600 p-10 sm:p-16 text-center">
            {/* Decorative pattern overlay */}
            <div className="absolute inset-0 bg-[linear-gradient(rgba(255,255,255,0.05)_1px,transparent_1px),linear-gradient(90deg,rgba(255,255,255,0.05)_1px,transparent_1px)] bg-[size:40px_40px]" />

            {/* Glow accents */}
            <div className="absolute top-0 right-0 w-64 h-64 bg-white/10 rounded-full blur-[80px]" />
            <div className="absolute bottom-0 left-0 w-64 h-64 bg-blue-600/40 rounded-full blur-[80px]" />

            <div className="relative z-10">
              <h2 className="text-3xl sm:text-4xl lg:text-5xl font-bold text-white leading-tight">
                Ready to Deploy
                <br />
                Your AI Agents?
              </h2>

              <p className="mt-6 text-lg text-white/80 max-w-2xl mx-auto leading-relaxed">
                Let&apos;s build agentic workflows that think, decide, and
                execute — saving your team 20+ hours every week.
              </p>

              <div className="mt-10 flex flex-wrap justify-center gap-4">
                <Button
                  href="/contact"
                  size="lg"
                  className="bg-white text-gray-900 shadow-lg hover:bg-white/90 hover:shadow-xl border-0 hover:brightness-100"
                >
                  Schedule a Call
                  <ArrowRight className="w-4 h-4" />
                </Button>
                <Button
                  href="/projects"
                  size="lg"
                  className="bg-transparent border border-white/30 text-white hover:bg-white/10 hover:border-white/50 shadow-none"
                >
                  View Projects
                </Button>
              </div>
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
