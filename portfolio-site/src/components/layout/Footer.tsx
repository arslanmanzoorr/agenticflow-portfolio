import Link from "next/link";
import { Github, Linkedin, Mail } from "lucide-react";

const quickLinks = [
  { label: "Projects", href: "/projects" },
  { label: "About", href: "/about" },
  { label: "Contact", href: "/contact" },
];

const socialLinks = [
  { label: "GitHub", href: "https://github.com/arslanmanzoorr", icon: Github },
  { label: "LinkedIn", href: "https://www.linkedin.com/in/arslan-manzoor-b148a0204/", icon: Linkedin },
  { label: "Email", href: "mailto:arslanmanzoorhere@gmail.com", icon: Mail },
];

export default function Footer() {
  return (
    <footer className="bg-surface border-t border-surface-border">
      <div className="mx-auto max-w-7xl px-6 py-12">
        <div className="flex flex-col items-center gap-8 md:flex-row md:justify-between">
          {/* Left */}
          <div className="text-center md:text-left">
            <p className="text-sm font-semibold text-foreground">
              AgenticFlow
            </p>
            <p className="mt-1 text-xs text-muted-foreground">
              &copy; {new Date().getFullYear()} Arslan Manzoor. All rights reserved.
            </p>
          </div>

          {/* Center - Quick Links */}
          <nav className="flex items-center gap-6">
            {quickLinks.map((link) => (
              <Link
                key={link.href}
                href={link.href}
                className="text-sm text-muted-foreground hover:text-foreground transition-colors"
              >
                {link.label}
              </Link>
            ))}
          </nav>

          {/* Right - Social */}
          <div className="flex items-center gap-4">
            {socialLinks.map((link) => (
              <a
                key={link.label}
                href={link.href}
                target="_blank"
                rel="noopener noreferrer"
                className="text-muted-foreground hover:text-foreground transition-colors"
                aria-label={link.label}
              >
                <link.icon className="h-5 w-5" />
              </a>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
