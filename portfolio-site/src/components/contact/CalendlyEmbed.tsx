"use client";

import { useEffect } from "react";

export default function CalendlyEmbed() {
  useEffect(() => {
    const script = document.createElement("script");
    script.src = "https://assets.calendly.com/assets/external/widget.js";
    script.async = true;
    document.body.appendChild(script);

    return () => {
      document.body.removeChild(script);
    };
  }, []);

  return (
    <div className="bg-surface/80 backdrop-blur-sm border border-surface-border rounded-2xl overflow-hidden">
      <div
        className="calendly-inline-widget"
        data-url="https://calendly.com/arslanmanzoorhere/30min?hide_gdpr_banner=1&background_color=12121a&text_color=f8fafc&primary_color=06b6d4"
        style={{ minWidth: "320px", height: "700px" }}
      />
    </div>
  );
}
