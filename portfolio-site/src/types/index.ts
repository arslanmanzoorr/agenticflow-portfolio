export interface Project {
  id: number;
  slug: string;
  title: string;
  tagline: string;
  description: string;
  problem: string;
  solution: string;
  tools: string[];
  category: string;
  features: string[];
  architecture: string[];
  type: "n8n" | "python" | "hybrid";
  github?: string;
  featured?: boolean;
}

export interface Service {
  title: string;
  description: string;
  icon: string;
}

export interface Testimonial {
  name: string;
  role: string;
  company: string;
  text: string;
  avatar?: string;
}

export interface Tool {
  name: string;
  category: string;
}

export interface Experience {
  title: string;
  company: string;
  period: string;
  description: string;
}
