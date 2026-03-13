import { cn } from "@/lib/utils";

interface ToolBadgeProps {
  name: string;
  size?: "sm" | "md";
}

const toolColorMap: Record<string, string> = {
  n8n: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  Python: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  Apify: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  Airtable: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  HubSpot: "bg-orange-500/10 text-orange-400 border-orange-500/20",
  OpenAI: "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  FastAPI: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  Slack: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  Shopify: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  PostgreSQL: "bg-blue-500/10 text-blue-400 border-blue-500/20",
  "Google Sheets": "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
  "Gmail API": "bg-orange-500/10 text-orange-400 border-orange-500/20",
  "OpenAI Whisper": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  "GPT-4": "bg-cyan-500/10 text-cyan-400 border-cyan-500/20",
  Webhooks: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  SMTP: "bg-purple-500/10 text-purple-400 border-purple-500/20",
  Calendly: "bg-blue-500/10 text-blue-400 border-blue-500/20",
};

const defaultColor = "bg-cyan-500/10 text-cyan-400 border-cyan-500/20";

const sizeStyles = {
  sm: "px-2 py-0.5 text-[10px]",
  md: "px-2.5 py-1 text-xs",
};

export default function ToolBadge({ name, size = "sm" }: ToolBadgeProps) {
  const colorClass = toolColorMap[name] || defaultColor;

  return (
    <span
      className={cn(
        "inline-flex items-center font-medium rounded-full border whitespace-nowrap",
        colorClass,
        sizeStyles[size]
      )}
    >
      {name}
    </span>
  );
}
