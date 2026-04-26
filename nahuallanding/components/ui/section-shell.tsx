type SectionShellProps = {
  id: string;
  /** Optional — section may render its own header inside `children`
   *  (used by AdvancedFeaturesSection / LiveDemoSection / PlainTechSection
   *  which need custom layouts above the grid). */
  eyebrow?: string;
  title?: string;
  copy?: string;
  children: React.ReactNode;
  className?: string;
};

export function SectionShell({
  id,
  eyebrow,
  title,
  copy,
  children,
  className
}: SectionShellProps) {
  const hasHeader = Boolean(eyebrow || title || copy);
  return (
    <section id={id} className={className}>
      <div className="section-wrap">
        {hasHeader ? (
          <div className="section-header">
            {eyebrow ? <div className="eyebrow">{eyebrow}</div> : null}
            {title ? <h2 className="section-title">{title}</h2> : null}
            {copy ? <p className="section-copy">{copy}</p> : null}
          </div>
        ) : null}
        {children}
      </div>
    </section>
  );
}
