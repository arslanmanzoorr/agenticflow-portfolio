"use client";

import { useEffect, useRef, useCallback } from "react";
import { motion } from "framer-motion";

// ---------------------------------------------------------------------------
// Neural network canvas — nodes drift, connect when near, pulses travel
// ---------------------------------------------------------------------------

interface Node {
  x: number;
  y: number;
  vx: number;
  vy: number;
  radius: number;
  brightness: number;
  pulsePhase: number;
}

function AnimatedBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const frameRef = useRef<number>(0);
  const reducedMotion = useRef(false);

  const initNodes = useCallback((w: number, h: number) => {
    const count = Math.min(Math.floor((w * h) / 18000), 80);
    const nodes: Node[] = [];
    for (let i = 0; i < count; i++) {
      nodes.push({
        x: Math.random() * w,
        y: Math.random() * h,
        vx: (Math.random() - 0.5) * 0.35,
        vy: (Math.random() - 0.5) * 0.35,
        radius: 1.2 + Math.random() * 1.8,
        brightness: 0.3 + Math.random() * 0.5,
        pulsePhase: Math.random() * Math.PI * 2,
      });
    }
    nodesRef.current = nodes;
  }, []);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext("2d");
    if (!ctx) return;

    // Check reduced motion
    const mql = window.matchMedia("(prefers-reduced-motion: reduce)");
    reducedMotion.current = mql.matches;
    const motionHandler = (e: MediaQueryListEvent) => {
      reducedMotion.current = e.matches;
    };
    mql.addEventListener("change", motionHandler);

    // Sizing
    const resize = () => {
      const dpr = Math.min(window.devicePixelRatio || 1, 2);
      canvas.width = window.innerWidth * dpr;
      canvas.height = window.innerHeight * dpr;
      canvas.style.width = `${window.innerWidth}px`;
      canvas.style.height = `${window.innerHeight}px`;
      ctx.setTransform(dpr, 0, 0, dpr, 0, 0);
      initNodes(window.innerWidth, window.innerHeight);
    };
    resize();
    window.addEventListener("resize", resize);

    // Data pulse state
    const pulses: { fromIdx: number; toIdx: number; progress: number; speed: number }[] = [];
    let lastPulseTime = 0;

    // Animation loop
    const draw = (time: number) => {
      const w = window.innerWidth;
      const h = window.innerHeight;
      const nodes = nodesRef.current;
      const CONNECTION_DIST = 160;
      const t = time * 0.001;

      ctx.clearRect(0, 0, w, h);

      if (!reducedMotion.current) {
        // Move nodes
        for (const node of nodes) {
          node.x += node.vx;
          node.y += node.vy;

          // Bounce off edges with padding
          if (node.x < -20) node.vx = Math.abs(node.vx);
          if (node.x > w + 20) node.vx = -Math.abs(node.vx);
          if (node.y < -20) node.vy = Math.abs(node.vy);
          if (node.y > h + 20) node.vy = -Math.abs(node.vy);
        }

        // Spawn data pulses periodically
        if (time - lastPulseTime > 800 && nodes.length > 1) {
          lastPulseTime = time;
          const fromIdx = Math.floor(Math.random() * nodes.length);
          // Find a nearby node to pulse toward
          let closestIdx = -1;
          let closestDist = Infinity;
          for (let j = 0; j < nodes.length; j++) {
            if (j === fromIdx) continue;
            const dx = nodes[j].x - nodes[fromIdx].x;
            const dy = nodes[j].y - nodes[fromIdx].y;
            const d = Math.sqrt(dx * dx + dy * dy);
            if (d < CONNECTION_DIST && d < closestDist) {
              closestDist = d;
              closestIdx = j;
            }
          }
          if (closestIdx !== -1) {
            pulses.push({ fromIdx, toIdx: closestIdx, progress: 0, speed: 0.015 + Math.random() * 0.01 });
          }
        }
      }

      // Draw connections
      for (let i = 0; i < nodes.length; i++) {
        for (let j = i + 1; j < nodes.length; j++) {
          const dx = nodes[j].x - nodes[i].x;
          const dy = nodes[j].y - nodes[i].y;
          const dist = Math.sqrt(dx * dx + dy * dy);
          if (dist < CONNECTION_DIST) {
            const alpha = (1 - dist / CONNECTION_DIST) * 0.15;
            ctx.beginPath();
            ctx.moveTo(nodes[i].x, nodes[i].y);
            ctx.lineTo(nodes[j].x, nodes[j].y);
            ctx.strokeStyle = `rgba(6, 182, 212, ${alpha})`;
            ctx.lineWidth = 0.5;
            ctx.stroke();
          }
        }
      }

      // Draw nodes
      for (const node of nodes) {
        const pulse = Math.sin(t * 1.5 + node.pulsePhase) * 0.3 + 0.7;
        const alpha = node.brightness * pulse;

        // Glow
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius * 4, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6, 182, 212, ${alpha * 0.08})`;
        ctx.fill();

        // Core
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.radius, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6, 182, 212, ${alpha})`;
        ctx.fill();
      }

      // Draw and update data pulses
      for (let p = pulses.length - 1; p >= 0; p--) {
        const pulse = pulses[p];
        pulse.progress += pulse.speed;
        if (pulse.progress >= 1) {
          pulses.splice(p, 1);
          continue;
        }

        const from = nodes[pulse.fromIdx];
        const to = nodes[pulse.toIdx];
        if (!from || !to) { pulses.splice(p, 1); continue; }

        const px = from.x + (to.x - from.x) * pulse.progress;
        const py = from.y + (to.y - from.y) * pulse.progress;
        const pulseAlpha = Math.sin(pulse.progress * Math.PI) * 0.9;

        // Pulse glow
        ctx.beginPath();
        ctx.arc(px, py, 6, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(6, 182, 212, ${pulseAlpha * 0.3})`;
        ctx.fill();

        // Pulse core
        ctx.beginPath();
        ctx.arc(px, py, 2.5, 0, Math.PI * 2);
        ctx.fillStyle = `rgba(100, 220, 255, ${pulseAlpha})`;
        ctx.fill();
      }

      frameRef.current = requestAnimationFrame(draw);
    };

    frameRef.current = requestAnimationFrame(draw);

    return () => {
      cancelAnimationFrame(frameRef.current);
      window.removeEventListener("resize", resize);
      mql.removeEventListener("change", motionHandler);
    };
  }, [initNodes]);

  return (
    <div
      aria-hidden="true"
      className="pointer-events-none fixed inset-0 z-0 overflow-hidden"
      style={{ backgroundColor: "#030308" }}
    >
      {/* Neural network canvas */}
      <canvas
        ref={canvasRef}
        className="absolute inset-0"
        style={{ willChange: "transform" }}
      />

      {/* Floating ambient orbs behind network */}
      <motion.div
        className="absolute rounded-full"
        style={{
          width: 500,
          height: 500,
          background: "radial-gradient(circle, rgba(6, 182, 212, 0.08), transparent 70%)",
          filter: "blur(120px)",
          left: "15%",
          top: "20%",
          willChange: "transform",
        }}
        animate={{ x: [0, 60, -40, 0], y: [0, -50, 30, 0] }}
        transition={{ duration: 20, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute rounded-full"
        style={{
          width: 400,
          height: 400,
          background: "radial-gradient(circle, rgba(59, 130, 246, 0.07), transparent 70%)",
          filter: "blur(120px)",
          right: "10%",
          bottom: "15%",
          willChange: "transform",
        }}
        animate={{ x: [0, -50, 30, 0], y: [0, 40, -60, 0] }}
        transition={{ duration: 25, repeat: Infinity, ease: "easeInOut" }}
      />
      <motion.div
        className="absolute rounded-full"
        style={{
          width: 350,
          height: 350,
          background: "radial-gradient(circle, rgba(139, 92, 246, 0.06), transparent 70%)",
          filter: "blur(100px)",
          left: "60%",
          top: "50%",
          willChange: "transform",
        }}
        animate={{ x: [0, 40, -30, 0], y: [0, -30, 50, 0] }}
        transition={{ duration: 22, repeat: Infinity, ease: "easeInOut" }}
      />

      {/* Noise texture */}
      <div
        className="absolute inset-0"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg viewBox='0 0 256 256' xmlns='http://www.w3.org/2000/svg'%3E%3Cfilter id='n'%3E%3CfeTurbulence type='fractalNoise' baseFrequency='0.9' numOctaves='4' stitchTiles='stitch'/%3E%3C/filter%3E%3Crect width='100%25' height='100%25' filter='url(%23n)' opacity='0.04'/%3E%3C/svg%3E")`,
          backgroundRepeat: "repeat",
          backgroundSize: "128px 128px",
          opacity: 0.3,
          mixBlendMode: "overlay",
        }}
      />

      {/* Vignette */}
      <div
        className="absolute inset-0"
        style={{
          background: "radial-gradient(ellipse at 50% 50%, transparent 30%, #030308 100%)",
        }}
      />
    </div>
  );
}

export default AnimatedBackground;
