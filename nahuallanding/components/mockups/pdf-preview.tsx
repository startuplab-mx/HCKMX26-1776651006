export function PdfPreview() {
  return (
    <div className="relative h-full min-h-[34rem]">
      <div className="absolute inset-10 rounded-[28px] bg-[rgba(193,106,76,0.16)] blur-3xl" />
      <div className="relative mx-auto h-full max-w-[28rem] rotate-[-5deg] rounded-[28px] border border-[rgba(245,240,235,0.12)] bg-[linear-gradient(180deg,#f7f3ee,#ddd5cc)] p-6 text-[#25282d] shadow-[0_28px_90px_rgba(0,0,0,0.38)]">
        <div className="flex items-start justify-between border-b border-[#c9b8aa] pb-4">
          <div>
            <p className="font-mono text-[11px] uppercase tracking-[0.26em] text-[#7a5b4d]">Nahual</p>
            <h3 className="mt-2 text-2xl font-black">REPORTE DE INCIDENTE DIGITAL</h3>
          </div>
          <div className="rounded-full border border-[#d0c1b6] px-3 py-1 font-mono text-xs uppercase tracking-[0.2em] text-[#7a5b4d]">
            Folio NH-240426-08
          </div>
        </div>
        <div className="mt-5 space-y-4 text-sm">
          <div className="rounded-[18px] border border-[#d7c8bc] bg-white/72 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-[#8d6b58]">
              Resumen del incidente
            </p>
            <div className="mt-3 grid grid-cols-2 gap-3 text-[#394048]">
              <div>Plataforma: WhatsApp</div>
              <div>Riesgo: Alto (0.92)</div>
              <div>Fases: Captación + Enganche</div>
              <div>Evidencia: 4 mensajes</div>
            </div>
          </div>
          <div className="rounded-[18px] border border-[#d7c8bc] bg-white/72 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-[#8d6b58]">
              Análisis
            </p>
            <ul className="mt-3 space-y-2 text-[#394048]">
              <li>• Oferta económica desproporcionada y pago de traslado.</li>
              <li>• Intención de mover la conversación a un canal más opaco.</li>
              <li>• Recomendación: resguardar evidencia y contactar adulto de confianza.</li>
            </ul>
          </div>
          <div className="rounded-[18px] border border-[#d7c8bc] bg-white/72 p-4">
            <p className="font-mono text-[10px] uppercase tracking-[0.24em] text-[#8d6b58]">
              Marco legal y contactos
            </p>
            <div className="mt-3 space-y-2 text-[#394048]">
              <p>LGDNNA · Ley Olimpia · ruta de atención con evidencia digital.</p>
              <p>088 · Fiscalía estatal · DIF municipal · orientación inmediata.</p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
