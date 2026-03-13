import Hero from "@/components/home/Hero";
import StatsBar from "@/components/home/StatsBar";
import ServicesGrid from "@/components/home/ServicesGrid";
import OpenClawDemo from "@/components/home/OpenClawDemo";
import FeaturedProjects from "@/components/home/FeaturedProjects";
import ToolsMarquee from "@/components/home/ToolsMarquee";
import Testimonials from "@/components/home/Testimonials";
import CTASection from "@/components/home/CTASection";

export default function HomePage() {
  return (
    <>
      <Hero />
      <StatsBar />
      <ServicesGrid />
      <OpenClawDemo />
      <FeaturedProjects />
      <ToolsMarquee />
      <Testimonials />
      <CTASection />
    </>
  );
}
