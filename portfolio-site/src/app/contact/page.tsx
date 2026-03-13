import type { Metadata } from "next";
import SectionHeading from "@/components/ui/SectionHeading";
import ContactForm from "@/components/contact/ContactForm";
import CalendlyEmbed from "@/components/contact/CalendlyEmbed";
import { Mail, Github, Linkedin, Calendar } from "lucide-react";

export const metadata: Metadata = {
  title: "Contact | Arslan Manzoor",
  description:
    "Get in touch with Arslan Manzoor for AI automation consulting, n8n workflows, and custom API integrations.",
};

const socialLinks = [
  {
    name: "Email",
    href: "mailto:arslanmanzoorhere@gmail.com",
    icon: Mail,
    label: "arslanmanzoorhere@gmail.com",
  },
  {
    name: "GitHub",
    href: "https://github.com/arslanmanzoorr",
    icon: Github,
    label: "github.com/arslanmanzoorr",
  },
  {
    name: "LinkedIn",
    href: "https://www.linkedin.com/in/arslan-manzoor-b148a0204/",
    icon: Linkedin,
    label: "linkedin.com/in/arslan-manzoor",
  },
  {
    name: "Schedule a Call",
    href: "https://calendly.com/arslanmanzoorhere/30min",
    icon: Calendar,
    label: "Book a 30-min consultation",
  },
];

export default function ContactPage() {
  return (
    <div className="min-h-screen pt-24">
      <section className="section-padding">
        <div className="container-custom">
          <SectionHeading
            badge="Contact"
            title="Let's Work Together"
            subtitle="Have a project in mind? Let's discuss how automation can transform your workflows."
          />

          <div className="max-w-5xl mx-auto grid grid-cols-1 lg:grid-cols-5 gap-10">
            {/* Contact Form */}
            <div className="lg:col-span-3">
              <ContactForm />
            </div>

            {/* Sidebar */}
            <div className="lg:col-span-2 space-y-6">
              {/* Quick Info */}
              <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-2xl p-8">
                <h3 className="text-lg font-semibold text-text-primary mb-6">
                  Get in Touch
                </h3>
                <div className="space-y-5">
                  {socialLinks.map((link) => (
                    <a
                      key={link.name}
                      href={link.href}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="flex items-center gap-4 text-text-secondary hover:text-primary transition-colors group"
                    >
                      <div className="w-10 h-10 rounded-lg bg-primary/10 flex items-center justify-center group-hover:bg-primary/20 transition-colors">
                        <link.icon className="w-5 h-5 text-primary" />
                      </div>
                      <div>
                        <p className="text-sm font-medium text-text-primary">
                          {link.name}
                        </p>
                        <p className="text-sm text-text-secondary">
                          {link.label}
                        </p>
                      </div>
                    </a>
                  ))}
                </div>
              </div>

              {/* Availability */}
              <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-2xl p-8">
                <div className="flex items-center gap-3 mb-4">
                  <div className="w-3 h-3 rounded-full bg-emerald-400 animate-pulse" />
                  <h3 className="text-lg font-semibold text-text-primary">
                    Available for Projects
                  </h3>
                </div>
                <p className="text-text-secondary text-sm leading-relaxed">
                  Currently accepting new automation and AI integration
                  projects. Typical response time is within 24 hours.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Calendly Embed Section */}
      <section className="section-padding bg-surface/30">
        <div className="container-custom">
          <SectionHeading
            badge="Book a Call"
            title="Schedule a Consultation"
            subtitle="Pick a time that works for you — let's discuss your automation needs."
          />
          <div className="max-w-4xl mx-auto">
            <CalendlyEmbed />
          </div>
        </div>
      </section>
    </div>
  );
}
