"use client";

import { motion, useInView, useReducedMotion } from "framer-motion";
import { useRef } from "react";

type RevealProps = {
  children: React.ReactNode;
  delay?: number;
  className?: string;
  y?: number;
};

export function Reveal({
  children,
  delay = 0,
  className,
  y = 28
}: RevealProps) {
  const ref = useRef<HTMLDivElement | null>(null);
  const inView = useInView(ref, { once: true, margin: "-15% 0px" });
  const reduceMotion = useReducedMotion();

  if (reduceMotion) {
    return (
      <div ref={ref} className={className}>
        {children}
      </div>
    );
  }

  return (
    <motion.div
      ref={ref}
      className={className}
      initial={{ opacity: 0, y }}
      animate={inView ? { opacity: 1, y: 0 } : undefined}
      transition={{ duration: 0.7, ease: [0.22, 1, 0.36, 1], delay }}
    >
      {children}
    </motion.div>
  );
}
