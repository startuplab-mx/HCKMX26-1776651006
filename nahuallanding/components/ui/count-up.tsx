"use client";

import { animate, motion, useInView, useReducedMotion } from "framer-motion";
import { useEffect, useRef, useState } from "react";

type CountUpProps = {
  value: number;
  suffix?: string;
  decimals?: number;
  className?: string;
};

export function CountUp({
  value,
  suffix = "",
  decimals = value % 1 === 0 ? 0 : 1,
  className
}: CountUpProps) {
  const ref = useRef<HTMLSpanElement | null>(null);
  const inView = useInView(ref, { once: true, margin: "-20% 0px" });
  const reduceMotion = useReducedMotion();
  const [displayValue, setDisplayValue] = useState(0);

  useEffect(() => {
    if (!inView) {
      return;
    }

    if (reduceMotion) {
      return;
    }

    const controls = animate(0, value, {
      duration: 1.4,
      ease: [0.16, 1, 0.3, 1],
      onUpdate: (latest) => {
        setDisplayValue(latest);
      }
    });

    return () => controls.stop();
  }, [inView, reduceMotion, value]);

  return (
    <motion.span ref={ref} className={className}>
      {(reduceMotion && inView ? value : displayValue).toFixed(decimals)}
      {suffix}
    </motion.span>
  );
}
