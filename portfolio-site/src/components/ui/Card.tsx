import * as React from "react";
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

/* shadcn-compatible Card (named exports) */
const ShadcnCard = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn(
      "rounded-lg border border-[#1a1a2e] bg-[#0a0a14]/80 text-[#f8fafc] shadow-sm",
      className
    )}
    {...props}
  />
));
ShadcnCard.displayName = "ShadcnCard";

const CardHeader = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex flex-col space-y-1.5 p-6", className)}
    {...props}
  />
));
CardHeader.displayName = "CardHeader";

const CardTitle = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLHeadingElement>
>(({ className, ...props }, ref) => (
  <h3
    ref={ref}
    className={cn("text-2xl font-semibold leading-none tracking-tight", className)}
    {...props}
  />
));
CardTitle.displayName = "CardTitle";

const CardDescription = React.forwardRef<
  HTMLParagraphElement,
  React.HTMLAttributes<HTMLParagraphElement>
>(({ className, ...props }, ref) => (
  <p
    ref={ref}
    className={cn("text-sm text-[#64748b]", className)}
    {...props}
  />
));
CardDescription.displayName = "CardDescription";

const CardContent = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div ref={ref} className={cn("p-6 pt-0", className)} {...props} />
));
CardContent.displayName = "CardContent";

const CardFooter = React.forwardRef<
  HTMLDivElement,
  React.HTMLAttributes<HTMLDivElement>
>(({ className, ...props }, ref) => (
  <div
    ref={ref}
    className={cn("flex items-center p-6 pt-0", className)}
    {...props}
  />
));
CardFooter.displayName = "CardFooter";

export {
  ShadcnCard as Card,
  CardHeader,
  CardFooter,
  CardTitle,
  CardDescription,
  CardContent,
};
