"use client";

import { useState, useEffect } from "react";
import Link from "next/link";
import Image from "next/image";
import { Menu } from "lucide-react";
import { cn } from "@/lib/utils";
import MobileMenu from "./MobileMenu";

const navLinks = [
  { label: "Projects", href: "/projects" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

export default function Navbar() {
  const [scrolled, setScrolled] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);

  useEffect(() => {
    const handleScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener("scroll", handleScroll, { passive: true });
    return () => window.removeEventListener("scroll", handleScroll);
  }, []);

  return (
    <>
      <header
        className={cn(
          "fixed top-0 left-0 right-0 z-50 transition-all duration-500",
          scrolled
            ? "bg-[#030308]/60 backdrop-blur-2xl border-b border-white/[0.04] shadow-[0_4px_30px_rgba(0,0,0,0.3)]"
            : "bg-transparent"
        )}
      >
        <nav className="mx-auto flex max-w-7xl items-center justify-between px-6 py-4">
          <Link href="/" className="flex items-center gap-2.5 group">
            <Image
              src="/images/arslan-profile.jpg"
              alt="Arslan Manzoor"
              width={36}
              height={36}
              className="rounded-full border border-cyan-500/30 object-cover transition-all duration-300 group-hover:border-cyan-400/60 group-hover:shadow-[0_0_12px_rgba(6,182,212,0.3)]"
            />
            <span className="text-lg font-bold gradient-text hidden sm:inline">
              Arslan Manzoor
            </span>
          </Link>

          {/* Desktop nav */}
          <div className="hidden md:flex items-center gap-1">
            {navLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="relative px-4 py-2 text-sm text-[#94a3b8] hover:text-[#f8fafc] transition-colors duration-200 rounded-lg hover:bg-white/[0.04] cursor-pointer"
              >
                {link.label}
              </Link>
            ))}
            <Link
              href="/contact"
              className="ml-4 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-600 px-5 py-2.5 text-sm font-medium text-white hover:shadow-[0_0_20px_rgba(6,182,212,0.3)] transition-all duration-300 cursor-pointer"
            >
              Schedule a Call
            </Link>
          </div>

          {/* Mobile hamburger */}
          <button
            className="md:hidden text-[#f8fafc] p-2 rounded-lg hover:bg-white/5 transition-colors cursor-pointer"
            onClick={() => setMobileOpen(true)}
            aria-label="Open menu"
          >
            <Menu className="h-5 w-5" />
          </button>
        </nav>
      </header>

      <MobileMenu
        open={mobileOpen}
        onClose={() => setMobileOpen(false)}
        links={navLinks}
      />
    </>
  );
}
