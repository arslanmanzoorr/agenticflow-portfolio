import SectionHeading from "@/components/ui/SectionHeading";
import ScrollReveal from "@/components/ui/ScrollReveal";
import { tools } from "@/data/tools";

const firstRow = tools.slice(0, Math.ceil(tools.length / 2));
const secondRow = tools.slice(Math.ceil(tools.length / 2));

function MarqueeRow({
  items,
  reverse = false,
}: {
  items: typeof tools;
  reverse?: boolean;
}) {
  // Duplicate for seamless infinite scroll
  const doubled = [...items, ...items];

  return (
    <div className="relative flex overflow-hidden py-2 group">
      {/* Fade edges */}
      <div className="absolute left-0 top-0 bottom-0 w-24 z-10 bg-gradient-to-r from-[#0a0a0f] to-transparent pointer-events-none" />
      <div className="absolute right-0 top-0 bottom-0 w-24 z-10 bg-gradient-to-l from-[#0a0a0f] to-transparent pointer-events-none" />

      <div
        className={`flex gap-4 shrink-0 ${
          reverse ? "animate-marquee-reverse" : "animate-marquee"
        }`}
      >
        {doubled.map((tool, i) => (
          <div
            key={`${tool.name}-${i}`}
            className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-[#12121a]/80 border border-[#1a1a2e] text-sm font-medium text-[#f8fafc] whitespace-nowrap shrink-0 hover:border-cyan-500/30 transition-colors"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            {tool.name}
            <span className="text-xs text-[#94a3b8]">{tool.category}</span>
          </div>
        ))}
      </div>
      <div
        aria-hidden
        className={`flex gap-4 shrink-0 ${
          reverse ? "animate-marquee-reverse" : "animate-marquee"
        }`}
      >
        {doubled.map((tool, i) => (
          <div
            key={`${tool.name}-dup-${i}`}
            className="flex items-center gap-2 px-4 py-2.5 rounded-full bg-[#12121a]/80 border border-[#1a1a2e] text-sm font-medium text-[#f8fafc] whitespace-nowrap shrink-0 hover:border-cyan-500/30 transition-colors"
          >
            <span className="w-1.5 h-1.5 rounded-full bg-cyan-400" />
            {tool.name}
            <span className="text-xs text-[#94a3b8]">{tool.category}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

export default function ToolsMarquee() {
  return (
    <section className="py-24 overflow-hidden">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal>
          <SectionHeading
            badge="Tech Stack"
            title="Tools & Technologies"
            subtitle="Battle-tested tools and platforms I use to build reliable automation solutions."
          />
        </ScrollReveal>
      </div>

      <div className="mt-4 space-y-4">
        <MarqueeRow items={firstRow} />
        <MarqueeRow items={secondRow} reverse />
      </div>
    </section>
  );
}
