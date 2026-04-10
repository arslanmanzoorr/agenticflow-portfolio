"use client";

import { useEffect, useState } from "react";
import { motion, useMotionValue, useSpring } from "framer-motion";

function SpotlightCursor() {
  const [isDesktop, setIsDesktop] = useState(false);
  const [prefersReducedMotion, setPrefersReducedMotion] = useState(false);

  const cursorX = useMotionValue(-1000);
  const cursorY = useMotionValue(-1000);

  const springX = useSpring(cursorX, { stiffness: 100, damping: 30 });
  const springY = useSpring(cursorY, { stiffness: 100, damping: 30 });

  useEffect(() => {
    const motionQuery = window.matchMedia("(prefers-reduced-motion: reduce)");
    setPrefersReducedMotion(motionQuery.matches);

    const handleMotionChange = (e: MediaQueryListEvent) => {
      setPrefersReducedMotion(e.matches);
    };
    motionQuery.addEventListener("change", handleMotionChange);

    const hoverQuery = window.matchMedia("(hover: hover) and (pointer: fine)");
    setIsDesktop(hoverQuery.matches);

    const handleHoverChange = (e: MediaQueryListEvent) => {
      setIsDesktop(e.matches);
    };
    hoverQuery.addEventListener("change", handleHoverChange);

    return () => {
      motionQuery.removeEventListener("change", handleMotionChange);
      hoverQuery.removeEventListener("change", handleHoverChange);
    };
  }, []);

  useEffect(() => {
    if (!isDesktop || prefersReducedMotion) return;

    const handleMouseMove = (e: MouseEvent) => {
      cursorX.set(e.clientX);
      cursorY.set(e.clientY);
    };

    window.addEventListener("mousemove", handleMouseMove);
    return () => {
      window.removeEventListener("mousemove", handleMouseMove);
    };
  }, [isDesktop, prefersReducedMotion, cursorX, cursorY]);

  if (!isDesktop || prefersReducedMotion) {
    return null;
  }

  return (
    <motion.div
      aria-hidden="true"
      style={{
        position: "fixed",
        top: 0,
        left: 0,
        width: "600px",
        height: "600px",
        borderRadius: "50%",
        pointerEvents: "none",
        zIndex: 1,
        x: springX,
        y: springY,
        translateX: "-50%",
        translateY: "-50%",
        background:
          "radial-gradient(circle, rgba(6, 182, 212, 0.07) 0%, rgba(6, 182, 212, 0.03) 40%, transparent 70%)",
      }}
    />
  );
}

export default SpotlightCursor;
