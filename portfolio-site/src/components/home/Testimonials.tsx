"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Quote, ChevronLeft, ChevronRight } from "lucide-react";
import SectionHeading from "@/components/ui/SectionHeading";
import ScrollReveal from "@/components/ui/ScrollReveal";
import { testimonials } from "@/data/testimonials";

export default function Testimonials() {
  const [current, setCurrent] = useState(0);

  const next = useCallback(() => {
    setCurrent((prev) => (prev + 1) % testimonials.length);
  }, []);

  const prev = useCallback(() => {
    setCurrent(
      (prev) => (prev - 1 + testimonials.length) % testimonials.length
    );
  }, []);

  // Auto-advance every 5 seconds
  useEffect(() => {
    const timer = setInterval(next, 5000);
    return () => clearInterval(timer);
  }, [next]);

  const testimonial = testimonials[current];

  return (
    <section className="py-24">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <ScrollReveal>
          <SectionHeading
            badge="Testimonials"
            title="What Clients Say"
            subtitle="Hear from the businesses that have transformed their operations with automation."
          />
        </ScrollReveal>

        <ScrollReveal>
          <div className="max-w-3xl mx-auto">
            <div className="relative bg-[#12121a]/80 backdrop-blur-sm border border-[#1a1a2e] rounded-2xl p-8 sm:p-10 min-h-[280px] flex flex-col justify-center">
              {/* Quote icon */}
              <Quote className="absolute top-6 left-6 w-10 h-10 text-cyan-500/10" />

              <AnimatePresence mode="wait">
                <motion.div
                  key={current}
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  exit={{ opacity: 0, y: -20 }}
                  transition={{ duration: 0.4, ease: "easeInOut" }}
                  className="text-center"
                >
                  <blockquote className="text-lg sm:text-xl text-[#f8fafc] leading-relaxed mb-8">
                    &ldquo;{testimonial.text}&rdquo;
                  </blockquote>

                  <div>
                    <p className="font-semibold text-[#f8fafc]">
                      {testimonial.name}
                    </p>
                    <p className="text-sm text-[#94a3b8]">
                      {testimonial.role}, {testimonial.company}
                    </p>
                  </div>
                </motion.div>
              </AnimatePresence>

              {/* Prev / Next buttons */}
              <button
                onClick={prev}
                aria-label="Previous testimonial"
                className="absolute left-3 top-1/2 -translate-y-1/2 p-2 rounded-full text-[#94a3b8] hover:text-[#f8fafc] hover:bg-white/5 transition-colors"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={next}
                aria-label="Next testimonial"
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2 rounded-full text-[#94a3b8] hover:text-[#f8fafc] hover:bg-white/5 transition-colors"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>

            {/* Dots */}
            <div className="flex justify-center gap-2 mt-6">
              {testimonials.map((_, i) => (
                <button
                  key={i}
                  onClick={() => setCurrent(i)}
                  aria-label={`Go to testimonial ${i + 1}`}
                  className={`w-2 h-2 rounded-full transition-all duration-300 ${
                    i === current
                      ? "bg-cyan-400 w-6"
                      : "bg-[#1a1a2e] hover:bg-[#94a3b8]/40"
                  }`}
                />
              ))}
            </div>
          </div>
        </ScrollReveal>
      </div>
    </section>
  );
}
