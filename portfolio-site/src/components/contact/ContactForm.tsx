"use client";

import { useState } from "react";
import { useForm } from "react-hook-form";
import { zodResolver } from "@hookform/resolvers/zod";
import { z } from "zod";
import Button from "@/components/ui/Button";
import { Send, CheckCircle } from "lucide-react";

const contactSchema = z.object({
  name: z.string().min(2, "Name must be at least 2 characters"),
  email: z.string().email("Please enter a valid email"),
  service: z.string().min(1, "Please select a service"),
  message: z.string().min(10, "Message must be at least 10 characters"),
});

type ContactFormData = z.infer<typeof contactSchema>;

export default function ContactForm() {
  const [isSubmitted, setIsSubmitted] = useState(false);

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm<ContactFormData>({
    resolver: zodResolver(contactSchema),
  });

  const onSubmit = async (data: ContactFormData) => {
    // Simulate form submission
    await new Promise((resolve) => setTimeout(resolve, 1000));
    console.log("Form submitted:", data);
    setIsSubmitted(true);
  };

  if (isSubmitted) {
    return (
      <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-2xl p-10 text-center">
        <CheckCircle className="w-16 h-16 text-emerald-400 mx-auto mb-4" />
        <h3 className="text-2xl font-bold text-text-primary mb-2">
          Message Sent!
        </h3>
        <p className="text-text-secondary">
          Thanks for reaching out. I&apos;ll get back to you within 24 hours.
        </p>
      </div>
    );
  }

  return (
    <form
      onSubmit={handleSubmit(onSubmit)}
      className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-2xl p-8 space-y-6"
    >
      <div>
        <label
          htmlFor="name"
          className="block text-sm font-medium text-text-primary mb-2"
        >
          Name
        </label>
        <input
          {...register("name")}
          id="name"
          type="text"
          placeholder="Your name"
          className="w-full px-4 py-3 bg-background border border-surface-border rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-colors"
        />
        {errors.name && (
          <p className="mt-1.5 text-sm text-red-400">{errors.name.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="email"
          className="block text-sm font-medium text-text-primary mb-2"
        >
          Email
        </label>
        <input
          {...register("email")}
          id="email"
          type="email"
          placeholder="you@example.com"
          className="w-full px-4 py-3 bg-background border border-surface-border rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-colors"
        />
        {errors.email && (
          <p className="mt-1.5 text-sm text-red-400">{errors.email.message}</p>
        )}
      </div>

      <div>
        <label
          htmlFor="service"
          className="block text-sm font-medium text-text-primary mb-2"
        >
          Service Interest
        </label>
        <select
          {...register("service")}
          id="service"
          className="w-full px-4 py-3 bg-background border border-surface-border rounded-lg text-text-primary focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-colors"
        >
          <option value="">Select a service...</option>
          <option value="workflow-automation">Workflow Automation</option>
          <option value="ai-chatbot">AI Chatbot Development</option>
          <option value="api-integration">Custom API Integration</option>
          <option value="generative-ai">Generative AI Solutions</option>
          <option value="process-optimization">Process Optimization</option>
          <option value="custom-scripting">Custom Scripting & Tools</option>
          <option value="other">Other</option>
        </select>
        {errors.service && (
          <p className="mt-1.5 text-sm text-red-400">
            {errors.service.message}
          </p>
        )}
      </div>

      <div>
        <label
          htmlFor="message"
          className="block text-sm font-medium text-text-primary mb-2"
        >
          Project Details
        </label>
        <textarea
          {...register("message")}
          id="message"
          rows={5}
          placeholder="Tell me about your project, timeline, and goals..."
          className="w-full px-4 py-3 bg-background border border-surface-border rounded-lg text-text-primary placeholder:text-text-muted focus:outline-none focus:border-primary/50 focus:ring-1 focus:ring-primary/50 transition-colors resize-none"
        />
        {errors.message && (
          <p className="mt-1.5 text-sm text-red-400">
            {errors.message.message}
          </p>
        )}
      </div>

      <Button type="submit" size="lg" className="w-full" disabled={isSubmitting}>
        {isSubmitting ? (
          "Sending..."
        ) : (
          <>
            Send Message <Send className="w-4 h-4" />
          </>
        )}
      </Button>
    </form>
  );
}
