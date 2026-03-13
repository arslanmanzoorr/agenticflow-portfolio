import { cn } from "@/lib/utils";

interface CardProps {
  className?: string;
  hover?: boolean;
  children: React.ReactNode;
}

export default function Card({ className, hover = true, children }: CardProps) {
  return (
    <div
      className={cn(
        "bg-[#12121a]/80 backdrop-blur-sm border border-[#1a1a2e] rounded-xl p-6",
        hover &&
          "transition-all duration-300 hover:-translate-y-1 hover:border-[#06b6d4]/30 hover:shadow-lg hover:shadow-cyan-500/5",
        className
      )}
    >
      {children}
    </div>
  );
}
