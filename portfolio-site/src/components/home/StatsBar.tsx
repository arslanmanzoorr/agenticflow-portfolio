import ScrollReveal from "@/components/ui/ScrollReveal";
import AnimatedCounter from "@/components/ui/AnimatedCounter";

const stats = [
  { target: 50, suffix: "+", label: "Workflows Built" },
  { target: 20, suffix: "+", label: "Happy Clients" },
  { target: 10000, suffix: "+", label: "Hours Saved" },
  { target: 98, suffix: "%", label: "Client Satisfaction" },
];

export default function StatsBar() {
  return (
    <section className="relative py-16">
      <ScrollReveal>
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="bg-[#12121a]/80 backdrop-blur-sm border border-[#1a1a2e] rounded-2xl p-8 sm:p-10">
            <div className="grid grid-cols-2 md:grid-cols-4 gap-8 md:gap-4">
              {stats.map((stat, i) => (
                <div key={i} className="text-center">
                  <div className="text-3xl sm:text-4xl font-bold text-[#f8fafc]">
                    <AnimatedCounter
                      target={stat.target}
                      suffix={stat.suffix}
                    />
                  </div>
                  <p className="mt-2 text-sm text-[#94a3b8]">{stat.label}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </ScrollReveal>
    </section>
  );
}
