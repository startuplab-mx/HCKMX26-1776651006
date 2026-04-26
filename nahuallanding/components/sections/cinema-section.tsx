"use client";

import { useState, useRef } from "react";
import { Play } from "lucide-react";

/**
 * Cinema piece — the closing emotional beat of the landing.
 *
 * UX rules requested by the user:
 *   • NO popup, NO autoplay, NO modal.
 *   • Solo si lo quieren ver: poster por default, click para reproducir.
 *   • Estética de lujo — nada de UI ruidosa que rompa el cierre del scroll.
 *
 * Implementation:
 *   • The video element is mounted with `preload="metadata"` so the poster
 *     loads but the 50 MB body isn't fetched until the user opts in.
 *   • Click on the poster → swap to the <video> with controls + autoplay
 *     (autoplay only fires after explicit user gesture, allowed by every
 *     browser autoplay policy).
 *   • Frame: 16:9 cinematic crop with a faint cobre vignette + soft
 *     shadow + thin outer ring so it reads as "framed art" rather than
 *     "embedded YouTube".
 *
 * Asset paths:
 *   /video/nahual-cine.mp4         (≈50 MB, served from public/)
 *   /video/nahual-cine-poster.jpg  (≈420 KB, single frame at 3.5s)
 */
export function CinemaSection() {
  const [playing, setPlaying] = useState(false);
  const videoRef = useRef<HTMLVideoElement>(null);

  function handlePlay() {
    setPlaying(true);
    // Autoplay is allowed because this fires from a user click.
    requestAnimationFrame(() => {
      videoRef.current?.play().catch(() => {
        // If the browser still refuses (rare), the visible controls
        // give the user a manual way to start.
      });
    });
  }

  return (
    <section
      id="por-que-importas"
      className="relative py-28 md:py-36 overflow-hidden"
    >
      {/* Backdrop: soft cobre glow → carbón fade. Pinned behind everything
          via z-0. Decorative, aria-hidden. */}
      <div
        aria-hidden
        className="absolute inset-0 -z-10 pointer-events-none"
        style={{
          background:
            "radial-gradient(60% 50% at 50% 35%, rgba(193,106,76,0.18) 0%, rgba(13,16,19,0) 70%), linear-gradient(180deg, rgba(13,16,19,0) 0%, rgba(13,16,19,0.85) 100%)"
        }}
      />

      <div className="section-wrap text-center">
        <p className="uppercase tracking-[0.4em] text-[11px] md:text-xs text-[#c16a4c] mb-5">
          Cierre · cinema piece
        </p>

        <h2 className="text-4xl md:text-6xl lg:text-7xl font-bold tracking-tight text-[#f5f0eb] leading-[1.05] max-w-4xl mx-auto">
          Nahual,<span className="text-[#c16a4c]"> por qué importas</span>
        </h2>

        <p className="mt-6 max-w-2xl mx-auto text-base md:text-lg text-[#f5f0eb]/65 leading-relaxed">
          95 segundos para entender por qué construimos esto. Sin prisas,
          sin spoilers — sólo dale play cuando estés listo.
        </p>

        {/* Cinema frame */}
        <div className="mt-14 md:mt-16 mx-auto max-w-5xl">
          <div
            className="relative w-full overflow-hidden rounded-[18px] md:rounded-[22px] ring-1 ring-[#c16a4c]/25"
            style={{
              aspectRatio: "16 / 9",
              boxShadow:
                "0 30px 80px -20px rgba(0,0,0,0.7), 0 8px 30px -5px rgba(193,106,76,0.18)"
            }}
          >
            {!playing ? (
              <button
                type="button"
                onClick={handlePlay}
                aria-label="Reproducir el video — Nahual, por qué importas (95 segundos)"
                className="group absolute inset-0 w-full h-full cursor-pointer focus:outline-none focus-visible:ring-2 focus-visible:ring-[#c16a4c] focus-visible:ring-offset-4 focus-visible:ring-offset-[#0d1013] transition-transform"
              >
                {/* Poster — eslint-disable-next-line @next/next/no-img-element
                    is justified: this is a single hero asset shipped in
                    public/, not a content image, so we skip <Image /> to
                    keep the section a pure client component. */}
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  src="/video/nahual-cine-poster.jpg"
                  alt=""
                  aria-hidden
                  className="absolute inset-0 w-full h-full object-cover"
                />

                {/* Vignette + bottom gradient for depth + caption legibility */}
                <div
                  aria-hidden
                  className="absolute inset-0"
                  style={{
                    background:
                      "radial-gradient(120% 80% at 50% 50%, transparent 35%, rgba(13,16,19,0.55) 100%), linear-gradient(180deg, transparent 55%, rgba(13,16,19,0.7) 100%)"
                  }}
                />

                {/* Play button — large, centered, cobre ring, hover lift */}
                <span
                  aria-hidden
                  className="absolute inset-0 flex items-center justify-center"
                >
                  <span className="relative flex items-center justify-center w-20 h-20 md:w-24 md:h-24 rounded-full bg-[#0d1013]/55 backdrop-blur-md ring-1 ring-[#f5f0eb]/30 transition-all duration-300 group-hover:scale-110 group-hover:bg-[#c16a4c]/85 group-hover:ring-[#c16a4c]">
                    <Play
                      size={32}
                      className="text-[#f5f0eb] translate-x-[2px]"
                      strokeWidth={2.2}
                      fill="currentColor"
                    />
                  </span>
                </span>

                {/* Caption inside the frame */}
                <span
                  aria-hidden
                  className="absolute bottom-5 left-0 right-0 text-center text-[#f5f0eb]/85 text-sm md:text-base tracking-wide"
                >
                  <span className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-[#0d1013]/55 backdrop-blur-sm ring-1 ring-[#f5f0eb]/15">
                    <span className="h-1.5 w-1.5 rounded-full bg-[#c16a4c]" />
                    1:35 min · sin sonido auto · 1080p
                  </span>
                </span>
              </button>
            ) : (
              <video
                ref={videoRef}
                className="absolute inset-0 w-full h-full"
                src="/video/nahual-cine.mp4"
                poster="/video/nahual-cine-poster.jpg"
                controls
                playsInline
                preload="metadata"
              />
            )}
          </div>

          <p className="mt-6 text-xs md:text-sm text-[#f5f0eb]/45">
            Si prefieres no verlo, no hace falta. El sistema entero ya
            quedó documentado arriba.
          </p>
        </div>
      </div>
    </section>
  );
}
