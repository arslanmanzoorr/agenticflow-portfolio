import { cn } from "@/lib/utils";

interface BadgeProps {
  label: string;
  color?: "primary" | "blue" | "green" | "purple" | "orange";
  className?: string;
}

const colorStyles: Record<NonNullable<BadgeProps["color"]>, string> = {
  primary: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  green: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  purple: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  orange: "bg-orange-500/10 text-orange-400 border-orange-500/20",
};

export default function Badge({
  label,
  color = "primary",
  className,
}: BadgeProps) {
  return (
    <span
      className={cn(
        "inline-flex items-center px-2.5 py-0.5 text-xs font-medium rounded-full border",
        colorStyles[color],
        className
      )}
    >
      {label}
    </span>
  );
}
