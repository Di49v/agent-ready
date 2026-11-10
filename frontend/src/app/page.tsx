"use client";

import React from "react";
import { Navbar } from "@/components/landing/Navbar";
import { HeroSection } from "@/components/landing/HeroSection";
import { AboutSection } from "@/components/landing/AboutSection";
import { WhySection } from "@/components/landing/WhySection";
import { FeaturesBento } from "@/components/landing/FeaturesBento";
import { InteractiveDemoPreview } from "@/components/landing/InteractiveDemoPreview";
import { WorkflowSteps } from "@/components/landing/WorkflowSteps";
import { DeveloperServices } from "@/components/landing/DeveloperServices";
import { DocumentationHub } from "@/components/landing/DocumentationHub";
import { PostmanSection } from "@/components/landing/PostmanSection";
import { Footer } from "@/components/landing/Footer";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-[var(--bg)] text-[var(--text)] flex flex-col font-sans transition-colors duration-200">
      {/* Sticky Top Navbar */}
      <Navbar />

      {/* Main Content Sections */}
      <main className="flex-1 flex flex-col landing-dark-spacing">
        {/* Section A: Hero, Quotes, Metrics, Primary CTAs */}
        <HeroSection />

        {/* Section B: About the Product (README-Inspired Architecture) */}
        <AboutSection />

        {/* Section C: Why Use AgentReady Lab (6 Fatal Threat Vectors) */}
        <WhySection />

        {/* Section D: Product Features & Deliverables (MongoDB Bento Grid) */}
        <FeaturesBento />

        {/* Section E: Interactive Product Demo Preview (Micro-Simulator) */}
        <InteractiveDemoPreview />

        {/* Section F: How to Use AgentReady Lab (Step-by-Step Developer Workflow) */}
        <WorkflowSteps />

        {/* Section G: Developer Services & Package Installation Spec */}
        <DeveloperServices />

        {/* Section H: Complete Technical Documentation Area (Tabbed Docs) */}
        <DocumentationHub />

        {/* Section I: Postman API Testing Hub (Collection v2.1 & RFC 9457) */}
        <PostmanSection />
      </main>

      {/* Section J: Closing High-Impact CTA & Comprehensive Footer */}
      <Footer />
    </div>
  );
}
