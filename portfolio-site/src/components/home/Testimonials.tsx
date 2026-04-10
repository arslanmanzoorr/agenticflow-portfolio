"use client";

import { useState, useEffect, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Quote, ChevronLeft, ChevronRight, Star } from "lucide-react";
import SectionHeading from "@/components/ui/SectionHeading";
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

  useEffect(() => {
    const timer = setInterval(next, 5000);
    return () => clearInterval(timer);
  }, [next]);

  const testimonial = testimonials[current];

  return (
    <section className="py-24 relative">
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ duration: 0.6 }}
        >
          <SectionHeading
            badge="Testimonials"
            title="What Clients Say"
            subtitle="Hear from the businesses that have transformed their operations with automation."
          />
        </motion.div>

        <motion.div
          initial={{ opacity: 0, y: 30 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          transition={{ delay: 0.2, duration: 0.6 }}
          className="max-w-3xl mx-auto"
        >
          <div className="relative overflow-hidden rounded-2xl border border-[#1a1a2e]">
            {/* Gradient border effect */}
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 via-transparent to-blue-500/5 pointer-events-none" />
            <div className="absolute inset-[1px] bg-[#0a0a12]/95 backdrop-blur-xl rounded-2xl" />

            <div className="relative p-8 sm:p-12 min-h-[320px] flex flex-col justify-center">
              {/* Decorative quote */}
              <Quote className="absolute top-6 left-6 w-12 h-12 text-cyan-500/8" />
              <Quote className="absolute bottom-6 right-6 w-12 h-12 text-cyan-500/8 rotate-180" />

              <AnimatePresence mode="wait">
                <motion.div
                  key={current}
                  initial={{ opacity: 0, x: 40 }}
                  animate={{ opacity: 1, x: 0 }}
                  exit={{ opacity: 0, x: -40 }}
                  transition={{
                    duration: 0.4,
                    ease: [0.21, 0.47, 0.32, 0.98],
                  }}
                  className="text-center"
                >
                  {/* Stars */}
                  <div className="flex justify-center gap-1 mb-6">
                    {[...Array(5)].map((_, i) => (
                      <Star
                        key={i}
                        className="w-4 h-4 fill-amber-400 text-amber-400"
                      />
                    ))}
                  </div>

                  <blockquote className="text-lg sm:text-xl text-[#e2e8f0] leading-relaxed mb-8 font-light">
                    &ldquo;{testimonial.text}&rdquo;
                  </blockquote>

                  <div className="flex items-center justify-center gap-4">
                    <div className="w-10 h-10 rounded-full bg-gradient-to-br from-cyan-500 to-blue-600 flex items-center justify-center text-white font-semibold text-sm">
                      {testimonial.name.charAt(0)}
                    </div>
                    <div className="text-left">
                      <p className="font-semibold text-[#f8fafc]">
                        {testimonial.name}
                      </p>
                      <p className="text-sm text-[#64748b]">
                        {testimonial.role}, {testimonial.company}
                      </p>
                    </div>
                  </div>
                </motion.div>
              </AnimatePresence>

              {/* Nav buttons */}
              <button
                onClick={prev}
                aria-label="Previous testimonial"
                className="absolute left-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full text-[#64748b] hover:text-[#f8fafc] hover:bg-white/5 transition-all duration-200 cursor-pointer"
              >
                <ChevronLeft className="w-5 h-5" />
              </button>
              <button
                onClick={next}
                aria-label="Next testimonial"
                className="absolute right-3 top-1/2 -translate-y-1/2 p-2.5 rounded-full text-[#64748b] hover:text-[#f8fafc] hover:bg-white/5 transition-all duration-200 cursor-pointer"
              >
                <ChevronRight className="w-5 h-5" />
              </button>
            </div>
          </div>

          {/* Progress dots */}
          <div className="flex justify-center gap-2 mt-6">
            {testimonials.map((_, i) => (
              <button
                key={i}
                onClick={() => setCurrent(i)}
                aria-label={`Go to testimonial ${i + 1}`}
                className={`h-1.5 rounded-full transition-all duration-300 cursor-pointer ${
                  i === current
                    ? "bg-gradient-to-r from-cyan-400 to-blue-500 w-8"
                    : "bg-[#1a1a2e] hover:bg-[#2a2a3e] w-1.5"
                }`}
              />
            ))}
          </div>
        </motion.div>
      </div>
    </section>
  );
}
