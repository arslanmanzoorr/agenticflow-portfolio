"use client";

import { cn } from "@/lib/utils";

interface ProjectFilterProps {
  categories: string[];
  activeCategory: string;
  onCategoryChange: (category: string) => void;
}

export default function ProjectFilter({
  categories,
  activeCategory,
  onCategoryChange,
}: ProjectFilterProps) {
  const allCategories = ["All", ...categories];

  return (
    <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide -mx-4 px-4 sm:mx-0 sm:px-0 sm:flex-wrap sm:justify-center">
      {allCategories.map((category) => {
        const isActive = activeCategory === category;

        return (
          <button
            key={category}
            onClick={() => onCategoryChange(category)}
            className={cn(
              "px-4 py-2 text-sm font-medium rounded-lg whitespace-nowrap transition-all duration-300 shrink-0",
              isActive
                ? "bg-gradient-to-r from-cyan-500 to-blue-500 text-white shadow-lg shadow-cyan-500/25"
                : "bg-transparent text-[#94a3b8] hover:text-[#f8fafc] hover:bg-white/5 border border-[#1a1a2e] hover:border-[#06b6d4]/30"
            )}
          >
            {category}
          </button>
        );
      })}
    </div>
  );
}
