type SectionShellProps = {
  id: string;
  eyebrow: string;
  title: string;
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
  return (
    <section id={id} className={className}>
      <div className="section-wrap">
        <div className="section-header">
          <div className="eyebrow">{eyebrow}</div>
          <h2 className="section-title">{title}</h2>
          {copy ? <p className="section-copy">{copy}</p> : null}
        </div>
        {children}
      </div>
    </section>
  );
}
